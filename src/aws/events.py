import datetime
import json
import uuid

from typing import Optional, Dict, Any, Union, List

import settings

DEFAULT_TOPIC_ARN = 'arn:aws:sns:eu-west-1:123456789012:some-topic'
DEFAULT_TOPIC_SUBJECT = 'Amazon S3 Notification'


def transform_s3_event(s3_event: Dict[str, Any],
                       transforms: List[str]) -> Dict[str, Any]:
    event = s3_event

    for transform in transforms:
        if transform == settings.EVENT_TRANSFORM_SNS:
            event = fake_sns_message(event)

        elif transform == settings.EVENT_TRANSFORM_SNS_LAMBDA:
            event = fake_sns_lambda_event(event)

    return event


def fake_s3_event(bucket: str,
                  key: str,
                  region: str,
                  etag: str,
                  size: Optional[int]=1024,
                  ) -> Dict[str, Any]:
    return {
        'Records': [
            {
                'eventVersion': '2.0',
                'eventTime': datetime.datetime.now().isoformat() + 'Z',
                'requestParameters': {
                    'sourceIPAddress': '127.0.0.1'
                },
                's3': {
                    'configurationId': 'testConfigRule',
                    'object': {
                        'eTag': '0123456789abcdef0123456789abcdef',
                        'sequencer': '0A1B2C3D4E5F678901',
                        'key': key,
                        'size': size,
                    },
                    'bucket': {
                        'arn': f'arn:aws:s3:::{bucket}',
                        'name': bucket,
                        'ownerIdentity': {
                            'principalId': 'EXAMPLE',
                        },
                    },
                    's3SchemaVersion': '1.0'
                },
                'responseElements': {
                    'x-amz-id-2': 'EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH',
                    'x-amz-request-id': 'EXAMPLE123456789'
                },
                'awsRegion': region,
                'eventName': 'ObjectCreated:Put',
                'userIdentity': {
                    'principalId': 'EXAMPLE'
                },
                'eventSource': 'aws:s3'
            }
        ]
    }


def fake_sns_message(message: Union[str, Any],
                     subject: Optional[str]=DEFAULT_TOPIC_SUBJECT,
                     topic_arn: Optional[str]=DEFAULT_TOPIC_ARN,
                     ) -> Dict[str, Any]:
    if not isinstance(message, str):
        message = json.dumps(message, ensure_ascii=False)

    return {
        'Type': 'Notification',
        'MessageId': str(uuid.uuid4()),
        'TopicArn': topic_arn,
        'Subject': subject,
        'Message': message,
        'Timestamp': datetime.datetime.now().isoformat() + 'Z',
        'SignatureVersion': '1',
        'Signature': 'N/A',
        'SigningCertURL': 'N/A',
        'UnsubscribeURL': 'N/A',
    }


def fake_sns_lambda_event(message: Union[str, Any],
                          subject: Optional[str]=DEFAULT_TOPIC_SUBJECT,
                          topic_arn: Optional[str]=DEFAULT_TOPIC_ARN,
                          ) -> Dict[str, Any]:
    if not isinstance(message, str):
        message = json.dumps(message, ensure_ascii=False)

    return {
        'Records': [
            {
                'EventVersion': '1.0',
                'EventSubscriptionArn': 'N/A',
                'EventSource': 'aws:sns',
                'Sns': {
                    'SignatureVersion': '1',
                    'Timestamp': datetime.datetime.now().isoformat() + 'Z',
                    'Signature': 'N/A',
                    'SigningCertUrl': 'N/A',
                    'MessageId': str(uuid.uuid4()),
                    'Message': message,
                    'MessageAttributes': {},
                    'Type': 'Notification',
                    'UnsubscribeUrl': 'N/A',
                    'TopicArn': topic_arn,
                    'Subject': subject,
                }
            }
        ]
    }
