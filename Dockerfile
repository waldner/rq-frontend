FROM python:3.8-alpine3.12

RUN apk --update add bash vim libxslt && \
    apk --no-cache --update --virtual build-dependencies add libxml2-dev libxslt-dev gcc musl-dev &&\
    pip install lxml rq flask &&\
    apk del build-dependencies

CMD [ "python3", "/app/app.py" ]
