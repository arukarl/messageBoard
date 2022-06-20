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

# Add SSL cert and private key
sudo aws s3 cp s3://mb-conf-folder/SectigoSSL.crt /etc/ssl/certs/SectigoSSL.crt
sudo mkdir -p /etc/ssl/private
sudo aws s3 cp s3://mb-conf-folder/SectigoSSL.key /etc/ssl/private/SectigoSSL.key

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
