FROM tiangolo/uwsgi-nginx:python3.6-alpine3.7

RUN apk add --update libxslt libxslt-dev postgresql-client postgresql postgresql-dev libffi libffi-dev libxml2 libxml2-dev git build-base gcc cmake autoconf automake libtool
RUN mv /app/uwsgi.ini /
RUN rm -rf /app/*
RUN mv /uwsgi.ini /app/

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "/app/docker/site/start.sh"]
