SERVICE_NAME := queue-tools
APP_NAME := queue-tools
APP_COMPONENT := queue-tools-cli

DOCKER_HUB := docker.io/akino1976

CURRENT_DATE := $(shell echo `date +'%Y-%m-%d'`)
VERSION ?= $(CURRENT_DATE)

ENVIRONMENT ?= dev
AWS_REGION ?= eu-west-1
PROFILE ?= onelogin

AWS_ACCOUNT := $(shell aws --profile $(PROFILE) sts get-caller-identity | jq '.Account')

export VERSION
export ENVIRONMENT
export AWS_REGION
export AWS_ACCOUNT
export APP_NAME
export APP_COMPONENT

help:
	python3 src/app.py --help

build:
	docker build \
		-t $(SERVICE_NAME):latest \
		-t $(SERVICE_NAME):$(VERSION) \
		-t $(DOCKER_HUB)/$(SERVICE_NAME):latest \
		-t $(DOCKER_HUB)/$(SERVICE_NAME):$(VERSION) \
		src

date:
	@echo $(CURRENT_DATE)

version:
	@echo ${VERSION}

profile:
	@echo ${PROFILE}

queue-to-queue-match: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			queue-to-queue \
			--origin-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/custexp-match-lookup-queue-dead-letters-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/custexp-match-lookup-queue-$(ENVIRONMENT)-$(AWS_REGION)

queue-to-queue-surway: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			queue-to-queue \
			--origin-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/custexp-surway-message-item-queue-dead-letters-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/custexp-surway-message-item-queue-$(ENVIRONMENT)-$(AWS_REGION)

queue-to-lambda-surway-notifications: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			queue-to-lambda \
			--origin-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/surway-notifications-dead-letters-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-function surway-notifications-$(ENVIRONMENT)-$(AWS_REGION)

queue-to-lambda-bi-file-formatter: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			queue-to-lambda \
			--origin-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/bi-file-formatter-all-dead-letters-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-function bi-file-formatter-all-$(ENVIRONMENT)-$(AWS_REGION)

queue-to-lambda-financial-adjustments-notifier: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			queue-to-lambda \
			--origin-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/fa-notifier-internal-notifications-dead-letters-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-function fa-notifier-internal-notifications-$(ENVIRONMENT)-$(AWS_REGION)

bucket-to-queue-bi-formatted-boclassic-product: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			bucket-to-queue \
			--origin-bucket bi-storage-formatted-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/bi-storage-formatted-queue-$(ENVIRONMENT)-$(AWS_REGION) \
			--prefix BOCLASSIC/BOCLASSIC-product/ \
			--s3-event-transforms sns

bucket-to-queue-bi-data-lake-boclassic-product: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			bucket-to-queue \
			--origin-bucket bi-storage-data-lake-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/bi-storage-data-lake-queue-$(ENVIRONMENT)-$(AWS_REGION) \
			--prefix BOCLASSIC/BOCLASSIC-product/ \
			--s3-event-transforms sns

bucket-to-queue-bi-data-lake-all-with-datespan: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
		$(DOCKER_HUB)/queue-tools:$(VERSION) \
			--region $(AWS_REGION) \
			bucket-to-queue \
			--origin-bucket bi-storage-data-lake-$(ENVIRONMENT)-$(AWS_REGION) \
			--target-queue https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ACCOUNT)/bi-storage-data-lake-queue-$(ENVIRONMENT)-$(AWS_REGION) \
			--s3-event-transforms sns \
			--from-date 2018-08-01 \
			--to-date 2018-09-19

bucket-to-payment: build
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
		-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
		-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
	dkr.jfrog.io/queue-tools \
	queue-to-queue \
	--origin-queue https://sqs.eu-west-1.amazonaws.com/927637421120/bi-storage-data-integration-all-dead-letters-prod-eu-west-1 \
	--target-queue https://sqs.eu-west-1.amazonaws.com/927637421120/bi-storage-data-integration-queue-prod-eu-west-1

bucket-to-payment-depo: build
	docker run --rm -it \
	-e AWS_ACCESS_KEY_ID=$(strip $(shell aws configure get aws_access_key_id --profile $(PROFILE))) \
	-e AWS_SECRET_ACCESS_KEY=$(strip $(shell aws configure get aws_secret_access_key --profile $(PROFILE))) \
	-e AWS_SESSION_TOKEN=$(strip $(shell aws configure get aws_session_token --profile $(PROFILE))) \
	$(DOCKER_HUB)/queue-tools:$(VERSION) \
	bucket-to-queue \
	--origin-bucket bi-storage-formatted-prod-eu-west-1 \
	--target-queue https://sqs.eu-west-1.amazonaws.com/927637421120/bi-storage-data-integration-queue-prod-eu-west-1 \
	--s3-event-transforms sns \
	--from-date 2019-07-01 \
	--to-date 2019-07-06 \
	--s3-key-date-pattern "PAYMENTDEPOT-transactions\/(.{10})"
