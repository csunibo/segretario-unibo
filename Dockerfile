FROM python:3.9-alpine
LABEL MAINTAINER="Angelo Huang <huangelo02@gmail.com>"

ENV GROUP_ID=1000 \
    USER_ID=1000
ENV TZ=Europe/Rome

WORKDIR /usr/src/app
COPY requirements.txt .
COPY main.py .
COPY config.ini .
COPY lib .

RUN apk update 
RUN apk add gcc libc-dev python3-dev
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
