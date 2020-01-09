
import os
import logging

from functools import lru_cache
from typing import Optional

import boto3
import botocore

import settings

logger = logging.getLogger(__name__)


def _get_proxy(service_name: str) -> Optional[str]:
    service_proxy = os.getenv(f'{service_name.upper()}_HOST')

    if service_proxy is not None:
        return service_proxy

    return os.getenv('MOCK_AWS_HOST')


@lru_cache(maxsize=256)
def get_client(service_name: str) -> botocore.client.BaseClient:
    proxy = _get_proxy(service_name)

    parameters = dict(
        service_name=service_name,
        region_name=settings.AWS_REGION,
    )

    if proxy is not None:
        parameters.update({
            'use_ssl': proxy.startswith('https://'),
            'config': botocore.config.Config(
                connect_timeout=1,
                read_timeout=1,
                retries={'max_attempts': 5},
                proxies={'http': proxy},
            ),
        })

    return boto3.client(**parameters)
