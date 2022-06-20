# Update installed packages
sudo yum update -y

# Install prerequisites
sudo yum install yum-utils -y

# Add Nginx repo
sudo aws s3 cp s3://mb-conf-folder/nginx.repo /etc/yum.repos.d/nginx.repo

# Enable nginx mainline
sudo yum-config-manager --enable nginx-mainline

# Install nginx
sudo yum install nginx -y

# Add nginx Server conf file
sudo aws s3 cp s3://mb-conf-folder/nginx.conf /etc/nginx/nginx.conf

# Add GeoTrust SSL cert and private key
sudo aws s3 cp s3://mb-conf-folder/nginx_GeoTrust.crt /etc/ssl/certs/nginx_GeoTrust.crt
sudo mkdir -p /etc/ssl/private
sudo aws s3 cp s3://mb-conf-folder/nginx_GeoTrust.key /etc/ssl/private/nginx_GeoTrust.key
sudo aws s3 cp s3://mb-conf-folder/karlaru_com.pem /etc/ssl/certs/karlaru_com.pem

# Add set of Diffie-Hellman parameters
sudo aws s3 cp s3://mb-conf-folder/dhparam.pem /etc/nginx/dhparam.pem

# Run nginx
sudo nginx

# Install Docker
sudo amazon-linux-extras install docker -y

# Start Docker service
sudo service docker start

# Run Docker after each reboot
sudo systemctl enable docker

# Add user to docker group to execute commands without sudo
sudo usermod -a -G docker ec2-user

# Activate changes to groups
sudo newgrp docker

# Run webapp
docker run -dit -p 5000:5000 --name mb  karlaru/message-board
