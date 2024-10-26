terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "google" {
  project = "personal-433817"
}

locals {
  project_id = "personal-433817"
}


resource "google_storage_bucket" "pubsub-storage" {
  name  = "pubsub-store"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_artifact_registry_repository" "redrive-repo" {
  repository_id = "pubsub-redrive"
  location = "us"
  description   = "docker repository for redrive job"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }
}

module pubsub-1 {
  source = "./modules/pubsub"
  name  = "bye"
  bucket_name = google_storage_bucket.pubsub-storage.name

  subscriptions = [
    "bye-1"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}


