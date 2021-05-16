resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "RAW_LOGS"
  description                 = "Raw equipment logs"
}