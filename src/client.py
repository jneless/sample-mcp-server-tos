import asyncio
import os
import sys

from mcp import ClientSession
from mcp.client.stdio import stdio_client


async def main():
    server_script = os.path.join(os.path.dirname(__file__), "tos_mcp_server/server.py")

    async with stdio_client(
            command=sys.executable,
            args=[server_script],
            env={
                "TOS_ACCESS_KEY": "your-access-key",
                "TOS_SECRET_KEY": "your-secret-key",
                "TOS_ENDPOINT": "https://your-bucket.tos-cn-beijing.volces.com",
                "TOS_REGION": "cn-beijing"
            }
    ) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 列出资源示例
            resources = await session.list_resources()
            print(f"Found {len(resources)} resources")

            # 读取资源示例
            if resources:
                content = await session.read_resource(resources[0].uri)
                print(f"First resource content: {content[:50]}...")


if __name__ == "__main__":
    asyncio.run(main())
