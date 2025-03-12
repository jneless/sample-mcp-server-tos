import logging
import os
from typing import List, Dict, Any

import tos
from tos.exceptions import TosServerError
from tos.models2 import ListedBucket, ListedObject

logger = logging.getLogger("tos_mcp_server")


class TosResource:
    """火山引擎TOS资源操作类（兼容MCP协议规范）"""

    def __init__(self, region: str = None, max_buckets: int = 5):
        self.client = tos.TosClientV2(
            ak=os.getenv('TOS_ACCESS_KEY'),
            sk=os.getenv('TOS_SECRET_KEY'),
            region=region or os.getenv('TOS_REGION', 'cn-beijing'),
            endpoint=os.getenv('TOS_ENDPOINT')
        )
        self.max_buckets = max_buckets
        self.configured_buckets = self._get_configured_buckets()

    def _get_configured_buckets(self) -> List[str]:
        """从环境变量加载预配置存储桶"""
        bucket_list = os.getenv('TOS_BUCKETS')
        if bucket_list:
            return [b.strip() for b in bucket_list.split(',')]
        return []

    async def list_buckets(self) -> List[ListedBucket]:
        """列举存储桶"""
        try:
            response = self.client.list_buckets()
            if self.configured_buckets:
                return [b for b in response.buckets if b.name in self.configured_buckets]
            return response.buckets
        except TosServerError as e:
            logger.error(f"List buckets error: {e.message}")
            raise

    async def list_objects(self, bucket: str, prefix: str = "", marker: str = None) -> List[ListedObject]:
        """列举存储桶对象"""
        try:
            response = self.client.list_objects(
                bucket=bucket,
                prefix=prefix,
                marker=marker,
                max_keys=1000
            )
            return response.contents
        except TosServerError as e:
            logger.error(f"List objects error in {bucket}: {e.message}")
            raise

    async def get_object(self, bucket: str, key: str) -> Dict[str, Any]:
        """获取对象内容（自动处理流式读取）"""
        try:
            response = self.client.get_object(bucket, key)
            content = b''
            async for chunk in response.content.data:
                content += chunk

            return {
                'content_type': response.content_type,
                'content': content,
                'metadata': {k.lower(): v for k, v in response.content.items()}
            }
        except TosServerError as e:
            if e.status_code == 404:
                raise ValueError(f"Object {key} not found in {bucket}")
            logger.error(f"Get object error: {e.message}")
            raise

    def is_text_file(self, key: str) -> bool:
        """判断文件是否为文本类型"""
        text_exts = {'.txt', '.log', '.csv', '.json', '.xml', '.md'}
        return any(key.lower().endswith(ext) for ext in text_exts)
