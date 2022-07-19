cd docusaurus|| true

npm run build

# Create docker image
docker build -t karlaru/mbdocs .

# DockerHub login
docker login

# Push image to DockerHub
docker push karlaru/mbdocs:latest

kubectl rollout restart deployment/docs
