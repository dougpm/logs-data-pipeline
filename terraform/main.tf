terraform {
  backend "gcs" {
    bucket = "YOUR_PROJECT_ID_HERE-terraform"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = local.project
  region  = local.region
  zone    = local.zone
}
