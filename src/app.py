import logging
import json

from typing import List

import settings
import aws.queue as queue
import aws.aws_lambda as aws_lambda
import aws.s3 as s3
import aws.events as events

logger = logging.getLogger(__name__)


def queue_to_queue(origin_queue: str, target_queue: str):
    total_message_count = 0

    logger.info(
        f'Moving messages from queue {origin_queue}'
        f' to queue {target_queue}'
    )

    for message in queue.exhaust_queue(origin_queue):
        total_message_count += 1

        queue.send_message(
            queue_url=target_queue,
            message=message['message']
        )

        queue.delete_message(
            queue_url=origin_queue,
            receipt_handle=message['receipt_handle'],
            message_id=message['message_id'],
        )

    if total_message_count == 0:
        logger.info(f'No messages on {origin_queue}, nothing to do')

    else:
        logger.info(
            f'Successfully sent a total of {total_message_count} messages'
            f' from queue {origin_queue} to queue {target_queue}'
        )


def queue_to_lambda(origin_queue: str, target_function: str):
    total_message_count = 0

    logger.info(
        f'Moving messages from queue {origin_queue}'
        f' to function {target_function}'
    )

    for message in queue.exhaust_queue(origin_queue):
        total_message_count += 1

        aws_lambda.invoke(
            function_name=target_function,
            payload=message['message'],
            message_id=message['message_id'],
        )

        queue.delete_message(
            queue_url=origin_queue,
            receipt_handle=message['receipt_handle'],
            message_id=message['message_id'],
        )

    if total_message_count == 0:
        logger.info(f'No messages on {origin_queue}, nothing to do')

    else:
        logger.info(
            f'Successfully sent a total of {total_message_count} messages'
            f' from queue {origin_queue} to queue {target_function}'
        )


def s3_to_queue(origin_bucket: str,
                target_queue: str,
                prefix: str,
                event_transforms: List[str]):
    items = s3.list_objects(origin_bucket, prefix)

    items = s3.filter_objects_by_datespan(
        items=items,
        s3_key_pattern=settings.arguments.s3_key_pattern,
        from_date=settings.arguments.from_date,
        to_date=settings.arguments.to_date,
    )

    total_message_count = 0

    logger.info(
        f'Sending messages from s3://{origin_bucket}/{prefix}*'
        f' to queue {target_queue}'
    )

    for item in items:
        event = events.fake_s3_event(
            bucket=item['bucket'],
            key=item['key'],
            region=item['region'],
            etag=item['etag'],
            size=item['size'],
        )

        if event_transforms:
            event = events.transform_s3_event(event, event_transforms)

        queue.send_message(
            queue_url=target_queue,
            message=json.dumps(event, ensure_ascii=False),
        )

        total_message_count += 1

    if total_message_count == 0:
        logger.info(
            f'No relevant items at s3://{origin_bucket}/{prefix}*,'
            ' nothing to do'
        )

    else:
        logger.info(
            f'Successfully sent a total of {total_message_count} messages'
            f' based on s3://{origin_bucket}/{prefix}* to queue {target_queue}'
        )


def main():
    settings.parse_flags()

    if settings.arguments.operation == settings.OPERATION_QUEUE_TO_QUEUE:
        queue_to_queue(
            origin_queue=settings.arguments.origin_queue,
            target_queue=settings.arguments.target_queue,
        )

    elif settings.arguments.operation == settings.OPERATION_QUEUE_TO_LAMBDA:
        queue_to_lambda(
            origin_queue=settings.arguments.origin_queue,
            target_function=settings.arguments.target_function,
        )

    elif settings.arguments.operation == settings.OPERATION_BUCKET_TO_QUEUE:
        s3_to_queue(
            origin_bucket=settings.arguments.origin_bucket,
            target_queue=settings.arguments.target_queue,
            prefix=settings.arguments.prefix,
            event_transforms=settings.arguments.s3_event_transforms,
        )

    else:
        logger.warn(
            f'Invalid operation {settings.arguments.operation}, nothing to'
        )


if __name__ == '__main__':
    main()
