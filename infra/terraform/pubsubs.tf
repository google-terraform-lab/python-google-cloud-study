
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
  name          = "not-allowerd"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "not-allowed-sub"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}