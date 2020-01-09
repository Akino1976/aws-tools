# queue-tools

## What is this?

This is a Docker image that helps with handling failed messages in an SQS or
Lambda based processing environment by moving messages from one queue to another or
queue to lambda.

It's also possible to fake file drop events to queues based on S3 objects
matching a given prefix or matching a date span based on the filename.

---

## Example usage

```bash
docker run --rm -it \
  -e AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile ${AWS_PROFILE:-default}) \
  -e AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile ${AWS_PROFILE:-default}) \
  -e AWS_SESSION_TOKEN=$(aws configure get aws_session_token --profile ${AWS_PROFILE:-default}) \
  docker.io/aws-tools \
    queue-to-queue \
    --origin-queue https://sqs.eu-west-1.amazonaws.com/254506858912/custexp-ems-interval-queue-dead-letters-dev-eu-west-1 \
    --target-queue https://sqs.eu-west-1.amazonaws.com/254506858912/custexp-ems-interval-queue-dev-eu-west-1
```

## Operations

Pass in any of the following _operations_ as the first argument before the flags.

### `queue-to-queue`

Moves the messages from the `origin-queue` to the `target-queue`.

#### Parameters

- `--origin-queue` The queue to move messages from
- `--target-queue` The queue to send messages from

#### Example

```bash
docker run --rm -it docker.io/aws-tools \
  queue-to-queue \
  --origin-queue https://sqs.eu-west-1.amazonaws.com/254506858912/custexp-ems-interval-queue-dead-letters-dev-eu-west-1 \
  --target-queue https://sqs.eu-west-1.amazonaws.com/254506858912/custexp-ems-interval-queue-dev-eu-west-1
```

### `queue-to-lambda`

Moves the messages from the `origin-queue` and triggers them as _events_ on the `target-function`.

#### Parameters

- `--origin-queue` The queue to move messages from
- `--target-function` The lambda function to trigger

#### Example

```bash
docker run --rm -it docker.io/aws-tools \
  queue-to-lambda \
  --origin-queue https://sqs.eu-west-1.amazonaws.com/254506858912/surway-notifications-dead-letters-dev-eu-west-1 \
  --target-function surway-notifications-dev-eu-west-1
```


### `bucket-to-queue`

Generate SQS messages based on objects in `origin-bucket` and put them on `target-queue`.

#### Parameters

- `--origin-bucket` The bucket to base the messages on
- `--target-queue` The queue to put messages on
- `--prefix` The prefix to use when listing objects.
- `--s3-event-transform` Space separated list of transformations of the generated S3 PutObject event message. (See help for valid values). All events will be based on an S3 PutObject event message which will be _piped_ through each type.
- `--from-date` Date to filter out S3 objects from (date is read in from the date)
- `--to-date` Date to filter out S3 objects to (date is read in from the date)
- `--s3-key-date-pattern` The pattern to use for finding the date part in the S3 key

#### Example

```bash
docker run --rm -it docker.io/aws-tools \
  bucket-to-queue \
  --origin-bucket bi-storage-data-lake-dev-eu-west-1 \
  --target-queue https://sqs.eu-west-1.amazonaws.com/254506858912/bi-storage-data-lake-queue-dev-eu-west-1 \
  --s3-event-transforms sns \
  --from-date 2018-08-01 \
  --to-date 2018-09-19
```
