
TERRAFORM_IMAGE_NAME=hashicorp/terraform:1.9
BUCKET_NAME=pubsub-store
PUBSUB_TOPIC=projects/personal-433817/topics/bye


# TRACE, DEBUG, INFO, WARN or ERROR
BASE_TERRAFORM=docker run --rm \
	-v $(shell pwd)/infra/terraform/:/workspace/ \
	-v $(shell pwd)/credential.json:/credential.json \
	-w /workspace \
	-e TF_LOG=ERROR \
	-e GOOGLE_APPLICATION_CREDENTIALS=/credential.json \
	${TERRAFORM_IMAGE_NAME}

-include .env

build-and-push-redrive-image:
	yes | gcloud auth configure-docker us-docker.pkg.dev
	cd examples/pubsub && docker build --no-cache -t pubsub-redrive:latest --platform linux/amd64 .
	docker tag pubsub-redrive:latest us-docker.pkg.dev/personal-433817/pubsub-redrive/pubsub-redrive:latest
	docker push us-docker.pkg.dev/personal-433817/pubsub-redrive/pubsub-redrive:latest

echo:
	${BASE_TERRAFORM}

init:
	${BASE_TERRAFORM} init

plan: init
	${BASE_TERRAFORM} plan

deploy-basics: init
	${BASE_TERRAFORM} apply \
		-target=google_storage_bucket.pubsub-storage \
		-target=google_artifact_registry_repository.redrive-repo \
		-target=google_project_iam_custom_role.initial-role \
		-target=google_project_iam_custom_role.basic-role \
		-target=google_project_iam_member.members \
		-target=google_storage_bucket_iam_member.bucket-members \
		-target=google_project_iam_binding.project \
		-target=google_bigquery_dataset.dataset \
		-target=google_bigquery_table.bye \
		--auto-approve


deploy-all: deploy-basics build-and-push-redrive-image
	${BASE_TERRAFORM} apply --auto-approve

deploy:
	${BASE_TERRAFORM} apply --auto-approve

destroy: init
	${BASE_TERRAFORM} destroy --auto-approve

pubsub-produce:
	cd examples/pubsub && \
	TOPIC_NAME=${PUBSUB_TOPIC} \
	python pubsub/producer.py

pubsub-compact:
	cd examples/pubsub && \
	BUCKET_NAME=${BUCKET_NAME} \
	TOPIC_NAME=${PUBSUB_TOPIC} \
	START_DATE=2024-10-29 \
	python pubsub/compact.py