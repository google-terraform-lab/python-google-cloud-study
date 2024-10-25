
variable name {
  type        = string
  description = "description"
}

variable subscriptions {
  type        = list(string)
  default     = []
  description = "description"
}


resource "google_pubsub_topic" "default" {
  name = var.name
}

resource "google_pubsub_subscription" "subscriptions" {
  for_each = toset(var.subscriptions)

  name  = each.value
  topic = google_pubsub_topic.default.id

  ack_deadline_seconds = 60

  labels = {
    foo = "bar"
  }
}