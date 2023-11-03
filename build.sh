#!/usr/bin/env sh
docker build -t kabachok:latest .
docker-compose build --parallel
