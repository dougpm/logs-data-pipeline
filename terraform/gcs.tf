resource "google_storage_bucket" "artifacts" {
  name     = "${local.project}-artifacts"
  location = local.region
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket" "logs" {
  name     = "${local.project}-logs"
  location = local.region
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket" "processed_logs" {
  name     = "${local.project}-processed-logs"
  location = local.region
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket" "staging" {
  name     = "${local.project}-staging"
  location = local.region
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket_object" "equipment_sensors" {
  name   = "tables/equipment_sensors.csv"
  bucket = google_storage_bucket.artifacts.name
  source = "../data/equipment_sensors.csv"
}

resource "google_storage_bucket_object" "equipment" {
  name   = "tables/equipment.json"
  bucket = google_storage_bucket.artifacts.name
  source = "../data/equipment.json"
}


