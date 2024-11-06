resource "google_storage_bucket" "pubsub-storage" {
  name  = "pubsub-store"
  location = "US"
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_artifact_registry_repository" "redrive-repo" {
  repository_id = "pubsub-redrive"
  location      = "us"
  description   = "docker repository for redrive job"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false # true is better, in a real CI
  }
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "pubsubs"
  friendly_name               = "pubsubs"
  description                 = "pubsub tables"
}

resource "google_bigquery_table" "bye" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "bye"


  external_data_configuration {
    autodetect    = true
    source_format = "NEWLINE_DELIMITED_JSON"

    hive_partitioning_options {
      mode = "AUTO"
      source_uri_prefix = "gs://pubsub-store/processed-messages/"
    }


    source_uris = [
      "gs://pubsub-store/processed-messages/*",
    ]
  }
}