import datetime
import logging
import re

from typing import List, Optional, Dict, Any

import botocore.exceptions
import dateutil.parser

import aws.common as common

logger = logging.getLogger(__name__)


def list_objects(bucket: str,
                 prefix: str,
                 ignore_empty: Optional[bool]=True) -> List[Dict[str, Any]]:
    client = common.get_client('s3')

    items = []

    try:
        paginator = client.get_paginator('list_objects_v2')

        parameters = dict(
            Bucket=bucket,
            MaxKeys=1000,
            Prefix=prefix,
        )

        for page in paginator.paginate(**parameters):
            for item in page.get('Contents', []):
                if ignore_empty and item.get('Size', 0) == 0:
                    continue

                items.append({
                    'bucket': page['Name'],
                    'key': item['Key'],
                    'region': page['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region'],
                    'etag': item['ETag'],
                    'size': item['Size'],
                })

    except botocore.exceptions.ClientError:
        logger.exception(f'Failed to list objects in bucket {bucket}')

        raise

    return items


def filter_objects_by_datespan(items: List[Dict[str, Any]],
                               s3_key_pattern: str,
                               from_date: Optional[datetime.date]=None,
                               to_date: Optional[datetime.date]=None,
                               ) -> List[Dict[str, Any]]:
    if from_date is None and to_date is None:
        return items

    from_date = from_date or datetime.date(0, 0, 0)
    to_date = to_date or datetime.date.today()

    pattern = re.compile(s3_key_pattern)

    filtered = []

    for item in items:
        matches = pattern.findall(item['key'])

        if len(matches) == 0:
            continue

        parsed_date = dateutil.parser.parse(matches[0]).date()

        if from_date <= parsed_date and parsed_date <= to_date:
            filtered.append(item)

    return filtered
