#!/usr/bin/env sh
docker build -t kabachok:latest .
docker build playground
docker-compose build --parallel
