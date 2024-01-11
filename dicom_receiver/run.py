import os
import uuid
import time
import json
import requests
from pydicom.dataset import Dataset

from pynetdicom import (
    AE, evt,
    StoragePresentationContexts,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)

with open("config.json") as f:
    config = json.load(f)

dataDir = os.path.join(config["dataFolder"])
os.makedirs(dataDir, exist_ok=True)

assocFolderDict = { }

# Implement a handler evt.EVT_C_STORE
def handle_store(event):
    """Handle a C-STORE request event."""
    # Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
    ds = event.dataset

    # Add the File Meta Information
    ds.file_meta = event.file_meta

    # Save the dataset using the SOP Instance UID as the filename
    filePath = os.path.join(assocFolderDict[event.assoc]["dicom_in"]["directory"], ds.SOPInstanceUID + ".dcm")
    ds.save_as(filePath, write_like_original=False)
    assocFolderDict[event.assoc]["dicom_in"]["files"].append(filePath)

    # Return a 'Success' status
    return 0x0000

def handle_assoc_open(event):
    assocId = str(uuid.uuid4())
    assocFolderDict[event.assoc] = {
        "uuid": assocId,
        "directory": os.path.join(dataDir, assocId),
        "dicom_in": {
            "directory": os.path.join(dataDir, assocId, "original"),
            "files": [ ]
        }
    }
    print("association opened " + assocFolderDict[event.assoc]["uuid"])
    os.makedirs(assocFolderDict[event.assoc]["dicom_in"]["directory"])

def handle_assoc_close(event):
    print("association closed: " + str(assocFolderDict[event.assoc]["uuid"]))
    with open(os.path.join(assocFolderDict[event.assoc]["directory"], "output.json"), "w") as f:
        json.dump(assocFolderDict[event.assoc], f)

    os.system("chmod -R 777 %s" % assocFolderDict[event.assoc]["directory"])
    
    if "airflow" in config:
        fullUrl = config["airflow"]["url"] + "/api/experimental/dags/" + config["airflow"]["workflow"] + "/dag_runs"
        response = requests.post(fullUrl,
            json={"conf": json.dumps({"processId": str(assocFolderDict[event.assoc]["uuid"])})},
            headers={
                "Cache-Control": "no-cache",
                "Content-Type": "application/json"
            })
        if response.status_code != 200:
            print(response.text)

handlers = [(evt.EVT_C_STORE, handle_store), (evt.EVT_CONN_OPEN, handle_assoc_open), (evt.EVT_CONN_CLOSE, handle_assoc_close)]

# Initialise the Application Entity
ae = AE()

# Add the supported presentation contexts
ae.supported_contexts = StoragePresentationContexts

print("Starting DICOM SCP on port 104")

# Start listening for incoming association requests
ae.start_server(('', 104), evt_handlers=handlers)
