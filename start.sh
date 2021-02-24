#!/bin/bash
app="exercise-app"

docker stop ${app}
docker rm ${app}

docker build -t ${app} .
docker run -t -i -v ~:/usr/files -p 8000:8000 ${app}