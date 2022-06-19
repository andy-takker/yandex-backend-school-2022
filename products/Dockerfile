FROM almalinux:9.0

WORKDIR /products
RUN dnf update && dnf install python39 python3-pip -y
ADD ./requirements.txt /
RUN pip3 install -r /requirements.txt --no-cache-dir


ADD ./backend.service /etc/systemd/system/

RUN set -ex \
    && systemctl enable backend.service

EXPOSE 8081

ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST
ARG POSTGRES_DB
ARG POSTGRES_PORT
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD

ARG DEBUG

ARG SERVER_NAME
ARG PROJECT_NAME

ADD create_env.sh /


RUN /bin/sh /create_env.sh > /etc/sysconfig/backend
CMD ["/sbin/init"]