## Build de image
docker build -t flask-backend:latest .

## Run de container
docker run -d -p 5000:5000 flask-backend:latest

## Url
http://localhost:5000/api/counter

## Hacer funcionar de forma local Jaeger (aqui voy 23/11)
https://github.com/jaegertracing/jaeger-client-python

---

#Run locally
pipenv install --dev 
pipenv shell
flask --app backend run