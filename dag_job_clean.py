import os 
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Get the notebook path from the environment variables
notebook_path = os.getenv('DATABRICKS_NOTEBOOK_PATH')

# set dag_name
dag_name = '0ebb0073c95b'

# Create default arguments for the DAG
default_args = {
    'owner': '0ebb0073c95be',  
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG
with DAG(
    dag_name,
    default_args=default_args,
    description='DAG to trigger a Databricks Notebook daily',
    schedule_interval='@daily',  # Runs daily
    start_date=datetime(2024, 10, 28), 
    catchup=False,
) as dag:

    # Define the configuration for the Databricks notebook as running using an existing cluster
    databricks_notebook_task = {
        'existing_cluster_id': '1108-162752-8okw8dgg',  # The cluster ID of Pinterest Cluster
        'notebook_task': {
            'notebook_path': notebook_path,  
        },
    }

    # DatabricksSubmitRunOperator to trigger the notebook
    run_notebook = DatabricksSubmitRunOperator(
        task_id='run_databricks_notebook',
        databricks_conn_id='databricks_default',  # Connection set up in MWAA
        json=databricks_notebook_task,
    )

    # Define task sequence
    run_notebook