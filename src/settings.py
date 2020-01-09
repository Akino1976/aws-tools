import datetime
import logging
import os

from argparse import ArgumentParser, ArgumentTypeError

APP_NAME = os.getenv('APP_NAME')
APP_COMPONENT = os.getenv('APP_COMPONENT')

VERSION = os.getenv('VERSION')
ENVIRONMENT = os.getenv('ENVIRONMENT')

AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')

OPERATION_QUEUE_TO_QUEUE = 'queue-to-queue'
OPERATION_QUEUE_TO_LAMBDA = 'queue-to-lambda'
OPERATION_BUCKET_TO_QUEUE = 'bucket-to-queue'

OPERATIONS = [
    OPERATION_QUEUE_TO_QUEUE,
    OPERATION_QUEUE_TO_LAMBDA,
    OPERATION_BUCKET_TO_QUEUE,
]

EVENT_TRANSFORM_SNS = 'sns'
EVENT_TRANSFORM_SNS_LAMBDA = 'sns:lambda'

EVENT_TRANSFORMS = [
    EVENT_TRANSFORM_SNS,
    EVENT_TRANSFORM_SNS_LAMBDA,
]

DEFAULT_S3_KEY_DATE_PATTERN = r'\d{4}/\d{2}/\d{2}'
DATE_PATTERN = '%Y-%m-%d'

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())

arguments = object()


def date_type(value) -> datetime.date:
    try:
        return datetime.datetime.strptime(value, DATE_PATTERN).date()

    except ValueError:
        raise ArgumentTypeError(f'{value} is not a valid date')


def parse_flags():
    global arguments

    global AWS_REGION

    parser = ArgumentParser()

    parser.add_argument(
        'operation',
        action='store',
        type=str,
        choices=OPERATIONS,
    )

    parser.add_argument(
        '--target-queue',
        action='store',
        type=str,
        dest='target_queue',
    )

    parser.add_argument(
        '--origin-queue',
        action='store',
        type=str,
        dest='origin_queue',
    )

    parser.add_argument(
        '--origin-bucket',
        action='store',
        type=str,
        dest='origin_bucket',
    )

    parser.add_argument(
        '--target-function',
        action='store',
        type=str,
        dest='target_function',
    )

    parser.add_argument(
        '--region',
        action='store',
        type=str,
        dest='region',
        default=AWS_REGION,
    )

    parser.add_argument(
        '--prefix',
        action='store',
        type=str,
        dest='prefix',
        default="",
    )

    parser.add_argument(
        '--s3-event-transforms',
        action='store',
        type=str,
        nargs='*',
        dest='s3_event_transforms',
        choices=EVENT_TRANSFORMS,
    )

    parser.add_argument(
        '--from-date',
        action='store',
        type=date_type,
        dest='from_date',
    )

    parser.add_argument(
        '--to-date',
        action='store',
        type=date_type,
        dest='to_date',
    )

    parser.add_argument(
        '--s3-key-date-pattern',
        action='store',
        type=str,
        dest='s3_key_pattern',
        default=DEFAULT_S3_KEY_DATE_PATTERN,
    )

    arguments = parser.parse_args()

    AWS_REGION = arguments.region
