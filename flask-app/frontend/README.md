## Build de image
docker build -t flask-frontend:latest .

## Run de container
docker run -p 8000:8000 -p 5000:5000 flask-frontend:latest
¿Como le hago para que pueda ver el puerto 5000?

http://localhost:8000/