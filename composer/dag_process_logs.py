import os
import datetime
import logging

from airflow import models
from airflow.utils.trigger_rule import TriggerRule
from airflow.contrib.hooks import gcs_hook
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocInstantiateWorkflowTemplateOperator,
)
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

DEFAULT_DAG_ARGS = {
    "owner": "Douglas Martins",
    "start_date": datetime.datetime(2021, 5, 14),
}

PROJECT_ID = "YOUR_PROJECT_ID_HERE"
ARTIFACTS_BUCKET = f"{PROJECT_ID}-artifacts"
#The cloud function used to trigger this dag provides a dag_run.conf
#dictionary containing information about the GCS object that triggered it
LOGS_BUCKET = "{{ dag_run.conf['bucket'] }}"
LOG_FILE = "gs://{{ dag_run.conf['bucket'] }}/{{ dag_run.conf['name'] }}"
PROCESSED_LOGS_BUCKET = f"{PROJECT_ID}-processed-logs"
STAGING_BUCKET = f"{PROJECT_ID}-staging"
# Tags used for moving the files to the right path after processing
SUCCESS_TAG = "processed"
FAILURE_TAG = "failed"

def move_to_completion_bucket(target_bucket, target_infix, **kwargs):
    """An utility method to move an object to a target location in GCS."""

    conn = gcs_hook.GoogleCloudStorageHook()

    source_bucket = kwargs['dag_run'].conf['bucket']
    source_object = kwargs['dag_run'].conf['name']
    completion_ds = kwargs['ds']
    target_object = os.path.join(target_infix, completion_ds, source_object)

    conn.copy(source_bucket, source_object, target_bucket, target_object)
    logging.info(f"Copying {source_bucket}/{source_object} to {target_bucket}/{target_object}.")
    conn.delete(source_bucket, source_object)
    logging.info(f"Deleting {source_bucket}/{source_object}.")


with models.DAG(
    dag_id="process-logs", default_args=DEFAULT_DAG_ARGS, schedule_interval=None
) as dag:

    begin_dag = DummyOperator(task_id="begin-dag")

    process_logs = DataprocInstantiateWorkflowTemplateOperator(
        task_id="process-logs",
        template_id="process-logs",
        project_id="YOUR_PROJECT_ID_HERE",
        region="us-central1",
        parameters={
            "CLUSTER_NAME": "process-logs",
            "MAIN_PY": f"gs://{ARTIFACTS_BUCKET}/dataproc-templates/process_logs.py",
            "INPUT_URI": LOG_FILE,
            "EQUIPMENT_SENSORS_URI": f"gs://{ARTIFACTS_BUCKET}/tables/equipment_sensors.csv",
            "EQUIPMENT_URI": f"gs://{ARTIFACTS_BUCKET}/tables/equipment.json",
            "OUTPUT_PROJECT_DATASET_TABLE": f"{PROJECT_ID}.RAW_LOGS.equipment_logs",
            "STAGING_BUCKET": STAGING_BUCKET,
        },
    )

    success_move_task = PythonOperator(
        task_id="success-move-to-completion",
        python_callable=move_to_completion_bucket,
        op_args=[PROCESSED_LOGS_BUCKET, SUCCESS_TAG],
        provide_context=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    failure_move_task = PythonOperator(
        task_id="failure-move-to-completion",
        python_callable=move_to_completion_bucket,
        op_args=[PROCESSED_LOGS_BUCKET, FAILURE_TAG],
        provide_context=True,
        trigger_rule=TriggerRule.ALL_FAILED,
    )

    end_dag = DummyOperator(task_id="end-dag")

    begin_dag >> process_logs >> (success_move_task, failure_move_task) >> end_dag