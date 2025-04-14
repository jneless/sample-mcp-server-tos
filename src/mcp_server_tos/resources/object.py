import base64
import logging

from mcp_server_tos.resources.service import TosResource
from mcp_server_tos.config import TosConfig

logger = logging.getLogger(__name__)


class ObjectResource(TosResource):
    """
        火山引擎TOS 对象资源操作类
    """

    def __init__(self, config: TosConfig):
        super(ObjectResource, self).__init__(config)

    async def get_object(self, bucket_name: str, key: str) -> str:
        """
        调用 TOS GetObject 接口获取对象内容
        api: https://www.volcengine.com/docs/6349/74850
        Args:
            bucket_name: 存储桶名称
            key: 对象名称
        Returns:
            对象内容
        """
        if self.configured_buckets and bucket_name not in self.configured_buckets:
            raise ValueError(f"Bucket {bucket_name} not in configured bucket list")
        chunk_size = 69 * 1024  # Using same chunk size as example for proven performance

        response = await self.get(bucket=bucket_name, key=key)

        content = bytearray()
        async for chunk in response.aiter_bytes(chunk_size):
            content.extend(chunk)

        if is_text_file(key):
            return content.decode('utf-8')
        else:
            return base64.b64encode(content).decode()


def is_text_file(key: str) -> bool:
    """Determine if a file is text-based by its extension"""
    text_extensions = {
        '.txt', '.log', '.json', '.xml', '.yml', '.yaml', '.md',
        '.csv', '.ini', '.conf', '.py', '.js', '.html', '.css',
        '.sh', '.bash', '.cfg', '.properties'
    }
    return any(key.lower().endswith(ext) for ext in text_extensions)
