#!/usr/bin/env bash
#!/bin/bash

set -e

docker build -t micro-weather-forecast:latest ./Microservice-Weather-App/forecast-service
docker build -t micro-weather-current:latest ./Microservice-Weather-App/current-service