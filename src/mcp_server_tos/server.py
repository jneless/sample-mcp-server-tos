import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_server_tos.config import load_config
from mcp_server_tos.resources.bucket import BucketResource
from mcp_server_tos.resources.object import ObjectResource

# Initialize FastMCP server
mcp = FastMCP("TOS MCP Server", port=int(os.getenv("PORT", "8000")))


@mcp.tool()
async def list_buckets() -> list[dict]:
    """
    List all buckets in TOS.
    Returns:
        A list of buckets.
    """
    try:
        config = load_config()
        tos_resource = BucketResource(config)
        buckets = await tos_resource.list_buckets()
        return buckets
    except Exception as e:
        logging.error(f"Error listing buckets: {e}")
        raise


@mcp.tool()
async def list_objects(bucket: str, prefix: Optional[str] = None, start_after: Optional[str] = None,
                       continuation_token: Optional[str] = None) -> list[dict]:
    """
    List all objects in a bucket.
    Args:
        bucket: The name of the bucket.
        prefix: The prefix to filter objects.
        start_after: The start after key to filter objects.
        continuation_token: The continuation token to filter objects.
    Returns:
        A list of objects.
    """
    try:
        config = load_config()
        tos_resource = BucketResource(config)
        objects = await tos_resource.list_objects(bucket, prefix, start_after, continuation_token)
        return objects
    except Exception as e:
        logging.error(f"Error listing objects: {e}")
        raise


@mcp.tool()
async def get_object(bucket: str, key: str) -> str:
    """
    Retrieves an object from VolcEngine TOS. In the GetObject request, specify the full key name for the object.
    Args:
        bucket: The name of the bucket.
        key: The key of the object.
    Returns:
        If the object content is text format, return the content as string.
        If the object content is binary format, return the content as base64 encoded string.
    """
    try:
        config = load_config()
        tos_resource = ObjectResource(config)
        object = await tos_resource.get_object(bucket, key)
        return object
    except Exception as e:
        logging.error(f"Error getting object: {e}")
        raise
