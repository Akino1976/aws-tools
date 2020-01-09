import logging

from typing import Optional

import botocore.exceptions

import aws.common as common

logger = logging.getLogger(__name__)


def invoke(function_name: str, payload: str, message_id: Optional[str]='N/A'):
    client = common.get_client('lambda')

    try:
        client.invoke(
            FunctionName=function_name,
            InvocationType='Event',
            LogType='Tail',
            Payload=payload.encode(),
        )

        logger.info(
            f'Successfully invoked {function_name} with message {message_id}'
        )

    except botocore.exceptions.ClientError:
        logger.exception(f'Failed to invoke {function_name}')

        raise
