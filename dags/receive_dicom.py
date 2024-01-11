from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os
import json

dag = DAG("dicom_import",
  schedule_interval=None,
  is_paused_upon_creation=False,
  catchup=False)

def _readConfig(processId):
    dataGiven = None
    with open(os.path.join("/data", processId, "output.json")) as f:
        dataGiven = json.load(f)
    return dataGiven

def receive(ds, **kwargs):
    processId = kwargs['dag_run'].conf['processId']
    dataGiven = _readConfig(processId)
    print(json.dumps(dataGiven, indent=2))
    return True

receive_data = PythonOperator(
    task_id='receive',
    provide_context=True,
    python_callable=receive,
    dag=dag,
    priority_weight=5,
)

receive_data