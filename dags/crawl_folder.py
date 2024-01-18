################################################################
# This is an example DAG to crawl over a folder, and for every
# subfolder trugger a new DAG execution.
#
# It currently expects a folder /data where there are subfolders
# (e.g. for individual patients), like the following tree:
# /data
#   - 00001
#   - 00002
#   - 00003
#   - 00004
#   - 00005
################################################################

from airflow import DAG
from airflow.api.client.local_client import Client
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

dag = DAG("crawl_folder",
  schedule_interval=None,
  is_paused_upon_creation=False,
  catchup=False)


def crawl(ds, **kwargs):
    folder_contents = os.listdir("/data")
    airflow_client = Client(None, None)
    for folder_item in folder_contents:
        fullPath = os.path.join("/data", folder_item)
        if os.path.isdir(fullPath):
            print(f"TRIGGER {fullPath}")
            my_run_id = f"{folder_item}_{datetime.now().isoformat()}"
            # Replace microseconds is needed to be disabled. Otherwise the run_id will fail
            airflow_client.trigger_dag(dag_id='dicom_import', run_id=my_run_id, conf={"processId": folder_item}, replace_microseconds=False)
    return True

crawl_folder = PythonOperator(
    task_id='crawl',
    provide_context=True,
    python_callable=crawl,
    dag=dag,
    priority_weight=5,
)

crawl_folder