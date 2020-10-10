FROM python:3.8-alpine3.12

RUN apk --update add bash vim && \
    pip install rq flask

CMD [ "python3", "/app/app.py" ]
