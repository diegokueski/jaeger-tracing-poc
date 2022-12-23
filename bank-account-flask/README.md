## Local setup
pipenv install -r requirements.txt
pipenv shell

## Run locally
*Run jaeger usign docker image
JAEGER_HOST=localhost USER_API=localhost:5001 python3 account.py
JAEGER_HOST=localhost python3 user.py

### Services
http://localhost:5000/create-account
http://localhost:5001/save-user