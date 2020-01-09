import logging

from typing import Any, Optional, Dict, Generator

import botocore.exceptions

import aws.common as common

logger = logging.getLogger(__name__)


def receive_message(queue_url: str,
                    wait_seconds: Optional[int]=1) -> Optional[Dict[str, Any]]:
    client = common.get_client('sqs')

    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_seconds,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )

        if len(response.get('Messages', [])) == 0:
            return None

        message = response['Messages'][0]

        message_id = message['MessageId']

        logger.info(
            f'Successfully received message {message_id} from {queue_url}'
        )

        return {
            'message': message['Body'],
            'message_id': message_id,
            'receipt_handle': message['ReceiptHandle']
        }

    except botocore.exceptions.ClientError:
        logger.exception(f'Failed to receive message from {queue_url}')

        raise


def exhaust_queue(queue_url: str,
                  max_message_count: Optional[int]=1,
                  wait_seconds: Optional[int]=1
                  ) -> Generator[Dict[str, Any], None, None]:
    while True:
        message = receive_message(
            queue_url=queue_url,
            wait_seconds=wait_seconds,
        )

        if message is None:
            break

        yield message


def send_message(queue_url: str, message: str):
    client = common.get_client('sqs')

    try:
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
        )

        message_id = response['MessageId']

        logger.info(
            f'Successfully sent message {message_id} to queue {queue_url}'
        )

        return message_id

    except botocore.exceptions.ClientError:
        logger.exception(f'Failed to send message to {queue_url}')

        raise


def delete_message(queue_url: str, receipt_handle: str, message_id: str):
    client = common.get_client('sqs')

    try:
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    except botocore.exceptions.ClientError:
        logger.exception(
            f'Failed to delete message {message_id} from {queue_url}'
        )

        raise
