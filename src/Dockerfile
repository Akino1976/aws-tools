FROM python:3.7-alpine3.10 AS base

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install wheel
RUN pip wheel -w /wheelhouse -r /tmp/requirements.txt

FROM python:3.7-alpine3.10

WORKDIR /queue-tools/src

RUN mkdir -p /queue-tools/src

COPY . /queue-tools/src

COPY --from=base /wheelhouse /wheelhouse
COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt --no-index --find-links /wheelhouse
RUN chmod u+x entrypoint.sh

ENV APP_COMPONENT "queue-tools-cli"
ENV APP_NAME "queue-tools"
ENV AWS_REGION "eu-west-1"
ENV ENVIRONMENT "dev"
ENV VERSION "local"

ENTRYPOINT [ "./entrypoint.sh" ]

CMD [ "--help" ]
