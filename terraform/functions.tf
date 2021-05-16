/* resource "google_storage_bucket_object" "trigger_process_dag" {
  name   = "cloud-functions/trigger_process_logs.zip"
  bucket = google_storage_bucket.artifacts.name
  source = "../scripts/trigger_process_logs.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "trigger-process-logs-dag"
  runtime     = "python38"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.trigger_process_dag.name
  entry_point           = "trigger_dag"
  event_trigger {
    event_type = "google.storage.object.finalize"
    resource = google_storage_bucket.logs.name

  }
} */