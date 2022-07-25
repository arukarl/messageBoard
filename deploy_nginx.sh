#!/bin/bash

PS3='Deloy or Remove: '
options=("Deploy stack" "Remove stack")
select opt in "${options[@]}"
do
    case $opt in
        "Deploy stack")
            echo "Creating stack nginx"
            aws s3 cp nginx/ s3://mb-conf-folder/ --recursive --exclude "*.yaml"
            aws s3 cp secrets/ s3://mb-conf-folder/ --recursive
            aws cloudformation create-stack --stack-name nginx \
                                --template-body file://nginx/nginx_stack.yaml \
                                --capabilities CAPABILITY_IAM \
                                --output yaml
            echo "Site will be up in few minutes!"
            echo "Visit https://nginx.karlaru.com"
            break
            ;;
        "Remove stack")
            echo "Removing stack nginx"
            aws cloudformation delete-stack --stack-name nginx
            echo "Stack delete in progress"
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
