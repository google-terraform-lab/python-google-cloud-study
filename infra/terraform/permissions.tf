
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
    "pubsub.topics.update",
    "pubsub.topics.publish",

    "pubsub.subscriptions.get",
    "pubsub.subscriptions.create",
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
