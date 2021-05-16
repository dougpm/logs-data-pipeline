PROJECT_ID="YOUR_PROJECT_ID_HERE"
REGION="us-central1"
BUCKET_NAME="YOUR_PROJECT_ID_HERE-artifacts"

TEMPLATE_FILE="process_logs.yaml"
TEMPLATE_NAME="process-logs"
PY_FILES_BUCKET=gs://$BUCKET_NAME/dataproc-templates/
PY_FILE="process_logs.py"

gsutil cp $PY_FILE $PY_FILES_BUCKET
yes | gcloud dataproc workflow-templates import $TEMPLATE_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --source=$TEMPLATE_FILE
