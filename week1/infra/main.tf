terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  project = "latin-b62d4"
  region  = "us-central1"
}

resource "google_storage_bucket" "my_bucket" {
  name          = "latin-b62d4-terra-bucket" # Replace with a globally unique bucket name
  location      = "US"                       # Replace with your desired location
  force_destroy = true                       # Replace with your desired storage class

  versioning {
    enabled = true # Enable versioning (optional)
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 3 # Delete objects after 30 days (optional)
    }
  }

}