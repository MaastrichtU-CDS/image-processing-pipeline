from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import os
import json
from LinkedDicom import LinkedDicom

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
    print(f"Received DICOM session with ID {processId} including a valid file")
    return True

receive_data = PythonOperator(
    task_id='receive',
    provide_context=True,
    python_callable=receive,
    dag=dag,
    priority_weight=5,
)

#############################################################################

def ldcm_parse(ds, **kwargs):
    processId = kwargs['dag_run'].conf['processId']
    dataGiven = _readConfig(processId)
    folderPath = dataGiven["dicom_in"]["directory"]
    liDcm = LinkedDicom.LinkedDicom(None)
    liDcm.processFolder(folderPath)
    output_path = os.path.join(dataGiven["directory"], "dicom_in.ttl") 
    liDcm.saveResults(output_path)

parse_linked_dicom = PythonOperator(
    task_id='parse_linked_dicom',
    provide_context=True,
    python_callable=ldcm_parse,
    dag=dag,
    priority_weight=5,
)

#############################################################################

receive_data >> parse_linked_dicom