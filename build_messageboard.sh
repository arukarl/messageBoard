cd message-board || true
# Create docker image
docker build -t karlaru/message-board .

# DockerHub login
docker login

# Push image to DockerHub
docker push karlaru/message-board:latest

# Copy style file to S3 and set browser cache control
aws s3 cp static/ s3://karlaru-mb/static/ --cache-control max-age=2592000 --acl public-read  --recursive
