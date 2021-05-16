### Hard skill test for a Data Engineer position at Shape Digital

#### Questions

On January 2020 considering GMT time zone:

1. Total equipment failures that happened?
asdas
2. Which equipment code had most failures?
asdasd
3. Average amount of failures across equipment group, ordering by the amount of failures in ascending order?
adsasd

#### Solution

The solution uses [Google Cloud Platform](https://cloud.google.com/) services.

###### Processing
For parsing the data, the chosen processing engine was [PySpark](https://spark.apache.org/docs/latest/api/python/), running on [Dataproc](https://cloud.google.com/dataproc) in a [Workflow Template](https://cloud.google.com/dataproc/docs/concepts/workflows/overview). Dataproc is a GCP service for running PySpark jobs. Dataproc Workflow Templates is a mechanism for executing Workflows in Dataproc, which consists of creating a cluster, running a graph of jobs, and deleting the cluster.
The PySpark job reads the provided files from Cloud Storage buckets, and creates a table in [BigQuery](https://cloud.google.com/bigquery), which is a serverless Data Warehouse.

###### Automation
For automating this workflow, [Cloud Functions](https://cloud.google.com/functions) was used in conjunction with [Cloud Composer](https://cloud.google.com/composer). Cloud Functions is a service to run stand-alone functions in response to events. Cloud Composer is a managed deployment of [Apache Airflow](http://airflow.apache.org/). As a new file arrives in the specified GCS bucket, a python function is executed to trigger a DAG in Airflow, using its REST API. This DAG has tasks that execute the Dataproc Workflow Template and then moves the file to a different bucket.

###### Infrastructure
[Terraform](https://www.terraform.io/) was used to manage all the different services and resources used in this project. Terraform is a Infrastucture as Code tool that facilitates the management of resources in the Cloud. The following tasks are performed by Terraform:

1. Creation of GCS Buckets.
2. Upload of equipments_sensors.csv and equipment.json to one of the buckets.
3. Deployment of the Cloud Componser environment.
4. Deployment of the Cloud Function.
5. Creation of the BigQuery dataset.

__Note__: The Dataproc workflow template could also be imported using Terraform, but I prefer to do it using a YAML configuration file.

__Note2__: The functions file has its content commented out. The reason for this is that the composer environment must be created before the function, as information about the Airflow Webserver must be filled in the function code before deployment. More on this in the instructions section.

###### Architecture
The developed solution follows this diagram:

![solution_diagram](solution_diagram.png)
1 - The log file is uploaded to a GCS Bucket.
2 - The object creation event triggers a Cloud Function.
3 - The Cloud Function triggers an Airflow DAG on Cloud Composer.
4 - The Airflow DAG runs a task to instantiate a Dataproc Workflow Template, which runs a PySpark Job to parse the log file, join it with the other two provided tables and load the results to BigQuery.
5 - After processing, the file is moved to another bucket, prefixed by success or failure tags, depending on whether the processing step succeeded or failed.
#### Folders description

- __terraform__
Contains the terraform files responsible for creating all the GCP resources.

- __dataproc__
Contains files related to the Dataproc Workflow Template.

- __cloud-functions__
Contains files related to the Cloud Function responsible for triggering the Airflow DAG whenever a new file is uploaded to the logs bucket in GCS.

- __composer__
Contains the DAG file and a script for fetching the Airflow Client ID, which is needed by the Cloud Function.

- __scripts__
Contains utility bash scripts.

#### Instructions for running the code

###### GCP Setup
1. Create a new project in GCP and take note of its ID.
2. Run the script __replace_project_id.sh__ passing your project id as an argument.
```bash
./replace_project_id.sh YOUR_PROJECT_ID
```
This will replace a placeholder string in all the files where the project ID is used.

3. Download and install the Cloud SDK, instructions [here](https://cloud.google.com/sdk/docs/install).
4. Setup GCP authentication, instructions [here](https://cloud.google.com/docs/authentication/getting-started).

###### Terraform Setup

1. Download and install terraform, instructions [here](https://learn.hashicorp.com/tutorials/terraform/install-cli).
2. Run the __setup_terraform_backend.sh__ script in the scripts folder, which will create the Storage Bucket that serves as the backend for storing Terraform's state.
3. In the terraform directory, run:

```bash
terraform init && terraform apply
```
and type in __yes__ when prompted. Wait for the process to be completed, which can take up to 40 minutes.

###### Cloud Function Setup

1. Run:

```bash
scripts/get_composer_info.sh
```
which will print the Client ID from the IAM Proxy that protects the Airflow Webserver, and the name of the tenant project used by Cloud Composer.

2. Open the main.py file in the __cloud-functions__ directory.
Replace the variable __client_id__ with the first line from the previous command, and __webserver_id__ with the second, for example:

```python
client_id = '570589106480-bqjmtqmp32khjcg4ik45fmtcdc9iuvu9.apps.googleusercontent.com'
webserver_id = 'p1f155accc9a34acfp-tp'
```

3. Run:

```bash
scripts/zip_cloud_function.sh
```
which will create a zip file in the scripts for creating the Cloud Function.

4. Uncomment the code in __terraform/functions.tf__, and from the terraform folder run __terraform apply__ once again. Now only the Cloud Function will be deployed.

###### Deploy and Trigger the DAG
From the root folder:

1. Run:

```bash
scripts/deploy_dag.sh
```
which will import the dag file from the __composer__ folder to Cloud Composer.

2. Run:

```bash
scripts/upload_error_logs.sh
```
which will upload the error logs file to the GCS bucket being monitored by the Cloud Function.

After the DAG runs, the table will be available in BigQuery.
