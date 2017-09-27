#!/bin/bash

docker-compose up -d
docker build -t test_dockertools .
docker run -d -v /bla --name test_dockertools test_dockertools
