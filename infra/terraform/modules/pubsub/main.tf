
variable name {
  type        = string
  description = "description"
}

variable subscriptions {
  type        = list(string)
  default     = []
  description = "description"
}

variable bucket_name {
  type = string
  default = ""
}

variable labels {
  type = map(string)
  default = {}
}

variable from_date {
  type = string
  default = "2024-10-26"
}


resource "google_pubsub_topic" "default" {
  name = var.name
}

resource "google_pubsub_subscription" "subscriptions" {
  for_each = toset(var.subscriptions)

  name  = each.value
  topic = google_pubsub_topic.default.id

  ack_deadline_seconds = 60

  labels = var.labels
}



resource "google_pubsub_subscription" "storage" {
  count = var.bucket_name != "" ? 1 : 0

  name = "${var.name}-storage"

  topic = google_pubsub_topic.default.id

  ack_deadline_seconds = 60
  
  cloud_storage_config {
    bucket = var.bucket_name

    filename_prefix = "${var.name}/"
    filename_datetime_format = "YYYY-MM-DD/hh_mm_ssZ"
    # filename_suffix = "-%{random_suffix}"

    max_bytes = 1000
    max_duration = "300s"
    max_messages = 1000
  }

  filter = <<EOF
    NOT attributes:redrive
  EOF

  depends_on = [
    data.google_storage_bucket.target,
    google_storage_bucket_iam_member.admin,
  ]

  labels = var.labels
}

data "google_storage_bucket" "target" {
  name = var.bucket_name
}

data "google_project" "project" {
}

resource "google_storage_bucket_iam_member" "admin" {
  count = var.bucket_name != "" ? 1 : 0
  bucket = var.bucket_name
  role   = "roles/storage.admin"
  member = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_cloud_run_v2_job" "redrive-job" {
  count = var.bucket_name != "" ? 1 : 0

  name     = "redrive-job-for-${var.name}"
  location = "us-central1"
  deletion_protection = false
  template {
    template {
      containers {
        image = "us-docker.pkg.dev/personal-433817/pubsub-redrive/pubsub-redrive:latest"
        env {
          name = "BUCKET_NAME"
          value = var.bucket_name
        }
        env {
          name = "TOPIC_NAME"
          value = google_pubsub_topic.default.id
        }
        env {
          name = "FROM_DATE"
          value = var.from_date
        } 
      }
    }
  }
}