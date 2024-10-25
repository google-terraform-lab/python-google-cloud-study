
TERRAFORM_IMAGE_NAME=hashicorp/terraform:1.9

# TRACE, DEBUG, INFO, WARN or ERROR
BASE_TERRAFORM=docker run --rm \
	-v $(shell pwd)/infra/terraform/:/workspace/ \
	-v $(shell pwd)/credential.json:/credential.json \
	-w /workspace \
	-e TF_LOG=ERROR \
	-e GOOGLE_APPLICATION_CREDENTIALS=/credential.json \
	${TERRAFORM_IMAGE_NAME}

-include .env


echo:
	${BASE_TERRAFORM}

init:
	${BASE_TERRAFORM} init

plan: init
	${BASE_TERRAFORM} plan

deploy: init
	${BASE_TERRAFORM} apply --auto-approve

destroy: init
	${BASE_TERRAFORM} destroy --auto-approve