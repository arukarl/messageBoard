cd message-board || true
# Create docker image
docker build -t karlaru/message-board .

# DockerHub login
docker login

# Push image to DockerHub
docker push karlaru/message-board:latest

# Copy static files to S3 and set browser cache control
aws s3 cp static/ s3://karlaru-mb/static/ --cache-control max-age=2592000 --recursive

kubectl rollout restart deployment/mb

# shasum -b -a 384 static/form-script.js | awk '{ print $1 }' | xxd -r -p | base64
# shasum -b -a 384 static/back.js | awk '{ print $1 }' | xxd -r -p | base64
# shasum -b -a 384 static/custom.css | awk '{ print $1 }' | xxd -r -p | base64
