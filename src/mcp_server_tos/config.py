import logging
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class TosConfig:
    """Configuration for Storage TOS MCP Server.

    Required environment variables:
        VOLC_ACCESSKEY: The Access key ID for authentication
        VOLC_SECRETKEY: Access key secret for authentication
        TOS_ENDPOINT:   The TOS service endpoint
        REGION:         The region of the TOS service
        TOS_BUCKETS:    The bucket list to use for the TOS service
    """
    access_key: str
    secret_key: str
    region: str
    endpoint: str
    security_token: str
    buckets: List[str]


def validate_required_vars():
    """
    Validate that all required environment variables are set.

    Raises:
    ValueError: If any required environment variable is missing.
    """
    missing_vars = []
    for var in ["VOLC_ACCESSKEY", "VOLC_SECRETKEY", "TOS_ENDPOINT"]:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


def load_config() -> TosConfig:
    validate_required_vars()
    config = TosConfig(
        access_key=os.environ["VOLC_ACCESSKEY"],
        secret_key=os.environ["VOLC_SECRETKEY"],
        region=os.getenv("REGION", ""),
        endpoint=os.environ["TOS_ENDPOINT"],
        security_token=os.getenv("SECURITY_TOKEN", ""),
        buckets=os.getenv("TOS_BUCKETS", "").split(","),
    )
    logger.info(f"Loaded configuration, endpoint: {config.endpoint}, region: {config.region} buckets: {config.buckets}")

    return config


load_dotenv()
