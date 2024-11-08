

module "users_table" {
    source = "./modules/table"
    name       = "users"
    compressed = true
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-users_raw_partitioned_and_compressed/"
}

module "users_table_raw" {
    source = "./modules/table"
    name       = "users_raw"
    compressed = false
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-users_raw/"
}

module "sessions_table" {
    source = "./modules/table"
    name       = "sessions"
    compressed = true
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-sessions_raw_partitioned_and_compressed/"
}

module "sessions_table_raw" {
    source = "./modules/table"
    name       = "sessions_raw"
    compressed = false
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-sessions_raw/"
}

module "movies_table" {
    source = "./modules/table"
    name       = "movies"
    compressed = true
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-movies_raw_partitioned_and_compressed/"
}

module "movies_table_raw" {
    source = "./modules/table"
    name       = "movies_raw"
    compressed = false
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-movies_raw/"
}