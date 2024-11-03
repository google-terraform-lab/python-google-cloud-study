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
  users = [
    "helenaneves.br@gmail.com"
  ]
}

resource "google_project_iam_custom_role" "basic-role" {
  role_id     = "RegularRole"
  title       = "Project Role"
  description = "Terraformad Role to regular users"
  permissions = [
    "cloudasset.assets.searchAllResources",
    "storage.buckets.get",
    "storage.buckets.getObjectInsights",
    "storage.buckets.listEffectiveTags",
    "storage.buckets.list", 
    "storage.objects.list", 
    "storage.objects.get",
    "storage.objects.delete",
    "storage.objects.create",
    "storage.folders.get",
    "storage.folders.list",

    "pubsub.topics.list",
    "pubsub.topics.get",
    "pubsub.subscriptions.get",
    "serviceusage.services.list",
  ]
}

resource "google_project_iam_member" "members" {
  for_each = toset(local.users)

  project = local.project_id
  role    = "roles/viewer"
  member  = "user:${each.key}"
}


resource "google_project_iam_binding" "project" {
  project = local.project_id
  role    = google_project_iam_custom_role.basic-role.name

  members = [
    for user in local.users : "user:${user}"
  ]

  condition {
    title       = "bucket and pubsub"
    description = "Allow just inside target bucket"
    expression  = "resource.name.startsWith(\"projects/_/topics/pubsubpoc-\") || resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.pubsub-storage.name}/\")"
  }
}

resource "google_storage_bucket" "pubsub-storage" {
  name  = "pubsub-store"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

# resource "google_storage_bucket_iam_member" "bucket_members" {
#   for_each = toset(local.users)
#   bucket   = google_storage_bucket.pubsub-storage.name
#   role     = google_project_iam_custom_role.basic-role.name
#   member   = "user:${each.key}"
#   condition  {
#     title       = "bucket_permission"
#     description = "Allow just inside target bucket"
#     expression  = "resource.name.startsWith(\"projects/_/buckets/${google_storage_bucket.pubsub-storage.name}/\")"
#   }

#   lifecycle {
#     replace_triggered_by = [
#       null_resource.always_run
#     ]
#   }
# }

resource "google_artifact_registry_repository" "redrive-repo" {
  repository_id = "pubsub-redrive"
  location      = "us"
  description   = "docker repository for redrive job"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false # true is better, in a real CI
  }
}

module pubsub-1 {
  source        = "./modules/pubsub"
  name          = "pubsubpoc-first"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "pubsubpoc-first-sub"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}

module pubsub-not-allowed {
  source        = "./modules/pubsub"
  name          = "notallower"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "notallower-sub"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}

