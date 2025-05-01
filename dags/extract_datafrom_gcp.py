from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
#helps extract data from gc to local system

from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
# Object in GCS -the Bucket - this operator helps list all files in the bukcet
 
from airflow.operators.python import PythonOperator

from airflow.hooks.base_hook import BaseHook
# hook - helps to connect to the ID in connections mentioned in airflow

from datetime import datetime

import pandas as pd
import sqlalchemy
#to connect to databse 

def load_to_sql(file_path):
    conn = BaseHook.get_connection('postgres_default')  
    # psycopg2 is a PostgreSQL adapter for Python
    # conn login,conn.password - connection login and pwd for postgres we mentioned 
    #@ml-ops-airflow-redis-prometheus-grafana_cff277-postgres-1 is docke container name
    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{conn.login}:{conn.password}@ml-ops-airflow-redis-prometheus-grafana_cff277-postgres-1:{conn.port}/{conn.schema}")
    
    # we convert csv to df and then df to SQL
    
    df = pd.read_csv(file_path)
    df.to_sql(name="titanic", con=engine, if_exists="replace", index=False)

# Define the DAG
with DAG(
    dag_id="extract_titanic_data",
    schedule_interval=None, 
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # EXTRACTS the data from GCS bucket 
    
    list_files = GCSListObjectsOperator(
        task_id="list_files",
        bucket="thirdprojbucket_001", 
    )

    # downloads the file from GCS bucket to local system
    download_file = GCSToLocalFilesystemOperator(
        task_id="download_file",
        bucket="thirdprojbucket_001", 
        object_name="Titanic-Dataset.csv", #FILENAME IN BUCKET
        filename="/tmp/Titanic-Dataset.csv", 
    )

    #TRANSFORMS AND LOADS the data after the downloading

    load_data = PythonOperator(
        task_id="load_to_sql", #Transformation step TO SQL 
        python_callable=load_to_sql, 
        op_kwargs={"file_path": "/tmp/Titanic-Dataset.csv"}
    )


    #WorkFlow to be followed - first list the files in the bucket, then download the file and finally load the data to SQL
    list_files >> download_file >> load_data 
