aws s3 cp cloud-formation/nginx s3://mb-conf-folder/ --recursive


# If stack doesn't already exist - create new
if ! aws cloudformation describe-stacks --stack-name messageBoard --output yaml ; then

  echo "Creating new stack!"

  aws cloudformation create-stack --stack-name messageBoard \
                                  --template-body file://cloud-formation/base_stack.yaml \
                                  --capabilities CAPABILITY_IAM \
                                  --output yaml

# If stack already exists - update
else

  echo "Updating existing stack!"

  aws cloudformation update-stack --stack-name messageBoard \
                                  --template-body file://cloud-formation/base_stack.yaml \
                                  --capabilities CAPABILITY_IAM \
                                  --output yaml

fi