#!/usr/bin/env bash

set -ex

cd ${0%/*}

mkdir -p dist
docker build --build-arg UID=$UID -t docker-tools_build -f build/Dockerfile .
docker run --rm -u $UID -v $PWD/dist:/dist --name docker-tools_build docker-tools_build --clean --onefile -n docker-tools docker_tools/main.py
