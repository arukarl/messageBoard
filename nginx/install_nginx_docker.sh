sudo yum update -y

sudo yum install yum-utils -y

sudo aws s3 cp s3://mb-conf-folder/nginx.repo /etc/yum.repos.d/nginx.repo

sudo yum-config-manager --enable nginx-mainline

sudo yum install nginx -y

sudo aws s3 cp s3://mb-conf-folder/nginx.conf /etc/nginx/nginx.conf

sudo aws s3 cp s3://mb-conf-folder/SectigoSSL.crt /etc/ssl/certs/SectigoSSL.crt
sudo mkdir -p /etc/ssl/private
sudo aws s3 cp s3://mb-conf-folder/SectigoSSL.key /etc/ssl/private/SectigoSSL.key

sudo aws s3 cp s3://mb-conf-folder/dhparam.pem /etc/nginx/dhparam.pem

sudo nginx

sudo amazon-linux-extras install docker -y

sudo service docker start

sudo systemctl enable docker

sudo aws s3 cp s3://mb-conf-folder/conf.cfg .

sudo docker run -dit \
    -p 5000:5000 --name mb \
    --mount type=bind,source="$(pwd)"/conf.cfg,target=/messageBoard/conf.cfg,readonly \
    karlaru/message-board
