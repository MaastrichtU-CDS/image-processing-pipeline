# Image Processing Pipeline template repository

This repository is a template for using Apache Airflow for image processing tasks. The repository is currently based on Airflow version 2.8.0 where the following modifications to the original docker-compose have been made:

- Reducing the resource footprint based on instructions explained [here](https://datatalks.club/blog/how-to-setup-lightweight-local-version-for-airflow.html)
- Installed a dicom_receiver to accept DICOM images using a Service Class Provider (SCP) which accepts C_STORE. All images are triggered into airflow based on association-close.

## Prerequisites
- Docker for Windows/macOS/Linux. For instructions how to install Docker, please see [here](https://docs.docker.com/get-docker/).

## How to use this repository?
1. Download or fork the repository
2. Open the downloaded folder in the terminal, and run `docker-compose up -d`
    - This will take a few minutes
3. Go to [http://localhost:8080](http://localhost:8080) using the default airflow username/password (airflow/airflow).

You can now send images using DICOM protocol (port 104) to the `receive_dicom` DAG. For this, you will need to install the (dcmtk toolkit)[https://dcmtk.org/en/]. This can be done by the following command:
```
storescu +r +sd localhost 104 <folder_path>
```