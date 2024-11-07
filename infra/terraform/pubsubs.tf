
module pubsub-users {
  source        = "./modules/pubsub"
  name          = "pubsubpoc-users"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "pubsubpoc-users-sub.1"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}

module pubsub-movies {
  source        = "./modules/pubsub"
  name          = "pubsubpoc-movies"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "pubsubpoc-movies-sub.1"
  ]

  depends_on = [
    google_storage_bucket.pubsub-storage
  ]
}

module pubsub-sessions {
  source        = "./modules/pubsub"
  name          = "pubsubpoc-sessions"
  bucket_name   = google_storage_bucket.pubsub-storage.name
  from_date     = "2024-10-26"
  subscriptions = [
    "pubsubpoc-session-sub.1"
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