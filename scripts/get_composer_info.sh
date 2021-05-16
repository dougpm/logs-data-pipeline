AIRFLOW_URL=$(gcloud composer environments describe composer01 \
    --location us-central1 \
    --format='value(config.airflowUri)')
curl -v $AIRFLOW_URL 2>&1 >/dev/null | grep "location:" | grep -oP "client_id=(\K.*.apps.googleusercontent.com)(?=&)"
echo $AIRFLOW_URL | grep -oP "https://(\K.*)(?=.appspot.com)"