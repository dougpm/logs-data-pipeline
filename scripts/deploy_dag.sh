cd scripts
gcloud composer environments storage dags import \
    --environment composer01 \
    --location us-central1 \
    --source ../composer/dag_process_logs.py