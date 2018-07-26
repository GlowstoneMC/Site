FROM python:3.6-alpine3.7

RUN apk add --update libxslt libxslt-dev postgresql-client postgresql postgresql-dev libffi libffi-dev libxml2 libxml2-dev git build-base gcc cmake autoconf automake libtool

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["sh", "/app/docker/celery/start.sh"]
