import asyncio
import base64
import logging
import os
from typing import List

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import Resource, LoggingLevel, EmptyResult, Tool, TextContent, BlobResourceContents, ReadResourceResult
from pydantic import AnyUrl
from tos.models2 import ListedBucket

from .resources.tos_resource import TosResource

# 初始化MCP服务
server = Server("tos_service")
logger = logging.getLogger("tos_mcp_server")

# 加载TOS资源处理器
tos_resource = TosResource(
    region=os.getenv('TOS_REGION'),
    max_buckets=int(os.getenv('TOS_MAX_BUCKETS', '5'))
)


@server.set_logging_level()
async def set_log_level(level: LoggingLevel) -> EmptyResult:
    """设置日志级别"""
    logger.setLevel(level.value)
    return EmptyResult()


@server.list_resources()
async def list_resources() -> List[Resource]:
    """列举TOS资源（兼容MCP协议分页）"""
    resources = []
    try:
        buckets = await tos_resource.list_buckets()

        async def process_bucket(bucket: ListedBucket):
            objects = await tos_resource.list_objects(bucket.name)
            for obj in objects:
                mime_type = "text/plain" if tos_resource.is_text_file(obj.key) else "application/octet-stream"
                resources.append(Resource(
                    uri=f"tos://{bucket.name}/{obj.key}",
                    name=obj.key,
                    mimeType=mime_type
                ))

        # 并发处理存储桶（限制并发数）
        sem = asyncio.Semaphore(3)
        async with sem:
            await asyncio.gather(*[process_bucket(b) for b in buckets])

    except Exception as e:
        logger.error(f"Resource listing failed: {str(e)}")
        raise

    return resources


@server.read_resource()
async def read_resource(uri: AnyUrl) -> BlobResourceContents:
    """读取TOS资源内容"""
    try:
        if not uri.startswith("tos://"):
            raise ValueError("Invalid TOS URI format")

        path = uri[6:]  # 去除tos://
        bucket, key = path.split("/", 1)

        response = await tos_resource.get_object(bucket, key)

        # Process the data based on file type
        if tos_resource.is_text_file(key):
            # text_content = data.decode('utf-8')
            text_content = base64.b64encode(response['content']).decode('utf-8')
            return text_content
        else:
            text_content = str(base64.b64encode(response['content']))
            result = ReadResourceResult(
                contents=[
                    BlobResourceContents(
                        blob=text_content,
                        uri=uri,
                        mimeType=response.get("content_type")
                    )
                ]
            )

            logger.debug(result)

            return text_content
    except ValueError as e:
        logger.error(f"URI parsing error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Read resource failed: {str(e)}")
        raise


@server.list_tools()
async def list_tools() -> list[dict]:
    """返回支持的TOS操作工具"""
    return [
        Tool(
            name="ListBuckets",
            description="Returns a list of all buckets owned by the authenticated sender of the request.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ListObjectsV2",
            description="Returns some or all (up to 1,000) of the objects in a bucket with each request.",
            inputSchema={
                "type": "object",
                "properties": {
                    "Bucket": {"type": "string", "description": "bucket name"},
                    "MaxKeys": {"type": "integer",
                                "description": "Sets the maximum number of keys returned in the response."},
                    "Prefix": {"type": "string",
                               "description": "Limits the response to keys that begin with the specified prefix."},
                    "StartAfter": {"type": "string",
                                   "description": "StartAfter is where you want Amazon S3 to start listing from."}
                },
                "required": ["Bucket"],
            },
        ),
        Tool(
            name="GetObject",
            description="Retrieves an object from TOS",
            inputSchema={
                "type": "object",
                "properties": {
                    "Bucket": {"type": "string", "description": "bucket name"},
                    "Key": {"type": "string",
                            "description": "Key of the object to get. Length Constraints: Minimum length of 1."},
                    "Range": {"type": "string", "description": "Downloads the specified byte range of an object."},
                    "VersionId": {"type": "string",
                                  "description": "Version ID used to reference a specific version of the object."},
                },
                "required": ["Bucket", "Key"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, args: dict) -> list[TextContent]:
    """执行TOS操作工具"""
    try:
        match name:
            case "ListBuckets":
                result = tos_resource.client.list_buckets()
                return [TextContent(type="text", text=str([b.name for b in result.buckets]))]
            case "ListObjectsV2":
                objects = tos_resource.client.list_objects(**args)
                return [
                    TextContent(
                        type="text",
                        text=str(objects)
                    )
                ]
            case "GetObject":
                content = tos_resource.client.get_object(**args)
                return [TextContent(type="text", text=str(content.content.read().decode('utf-8')))]
            case _:
                raise ValueError("Unsupported operation")
    except Exception as e:
        return [TextContent(text=f"Error: {str(e)}")]


async def main():
    """MCP服务启动入口"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tos-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
