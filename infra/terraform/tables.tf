

module "users_table" {
    source = "./modules/table"
    name       = "users"
    compressed = true
    dataset_id = google_bigquery_dataset.dataset.dataset_id
    path       = "gs://pubsub-storage-poc/pubsubpoc-users_raw_partitioned_and_compressed"
}