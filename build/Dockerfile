FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        binutils \
        upx-ucl \
        libssl-dev \
        liblz4-dev \
        build-essential \
        libacl1-dev \
        pkg-config \
        python3-virtualenv \
        virtualenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists \
    && pip3 install pip --upgrade \
    && pip3 install setuptools \
    && pip3 install pyinstaller \
    && mkdir /dist \
    && mkdir /data \
    && chmod 0777 /dist /data

VOLUME /dist

ARG UID
RUN adduser --uid $UID builder

USER root
COPY . /data
WORKDIR /data
RUN chown builder.builder -R /data

USER builder

RUN pip3 install --user -e .

ENTRYPOINT ["pyinstaller", "--distpath=/dist"]
