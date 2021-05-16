resource "google_composer_environment" "composer" {
  name   = "composer01"
  region = local.region

  config {
    node_count = 3

    node_config {
        zone         = local.zone
        machine_type = "n2-standard-2"
        network    = "network-datalabs-develop"
        subnetwork = "subnet-cluster-services"
    }

    software_config {
      airflow_config_overrides = {
        "api-auth_backend"	= "airflow.api.auth.backend.default"
      }

      pypi_packages = {
        apache-airflow-backport-providers-google = "==2021.3.3"
      }
    }

  }
}
