# Opentracing Tutorial

## Reference
https://github.com/opentracing-contrib/python-flask/tree/master/example

## Local setup
pipenv install -r path/to/requirements.txt
pipenv shell

## Run locally
*Run jaeger usign docker image
JAEGER_HOST=localhost python3 server.py
JAEGER_HOST=localhost WEBSERVER_HOST=localhost python3 client.py

### Server
http://localhost:5000/log