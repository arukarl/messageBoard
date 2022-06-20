# If stack doesn't already exist - create new
if ! aws cloudformation describe-stacks --stack-name messageBoard ; then

  echo "Creating new stack!"

  aws cloudformation create-stack --stack-name messageBoard \
                                  --template-body file://cloud-formation/aws_stack.yaml \
                                  --capabilities CAPABILITY_IAM

# If stack already exists - update
else

  echo "Updating existing stack!"

  aws cloudformation update-stack --stack-name messageBoard \
                                  --template-body file://cloud-formation/aws_stack.yaml \
                                  --capabilities CAPABILITY_IAM

fi