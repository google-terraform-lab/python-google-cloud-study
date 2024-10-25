terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
  }
}

provider "google" {
  project = "personal-433817"
}

locals {
  project_id = "personal-433817"
}


module pubsub-1 {
  source = "./modules/pubsub"
  name  = "bye"

  subscriptions = [
    "bye-1"
  ]
}