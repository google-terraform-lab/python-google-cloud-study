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

data "google_project" "project" {
}

locals {
  project_id = data.google_project.project.id
  users = [
    "helenaneves.br@gmail.com"
  ]
}