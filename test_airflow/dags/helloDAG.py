from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pymongo import MongoClient
from datetime import datetime
from Utils.postgres_tool import PostgresTool
from Utils.random_data import load_data, save_processed_indices
from Utils.process_data import process_emails
import yaml
import pandas as pd
import json

with open("/opt/airflow/dags/config/configs.yaml", "r") as file:
    config = yaml.safe_load(file)

config_postgres = config['database-postgres']
config_mongo = config['database-mongodb']
url_csv = config['url']['url_csv']

def push_data_mongo(config_mongo, url_csv):
    try:
        client = MongoClient(**config_mongo)
        db = client['test']
        df_sample, processed_indices = load_data(url_csv)
        df_json = json.loads(df_sample.to_json(orient='records'))
        db.emails.insert_many(df_json)
        print("Success MongoDB")
        save_processed_indices(processed_indices)
    except Exception as e:
        print(f"Connect failed MongoDB: {e}")
        raise

def ETL_data(config_mongo,config_postgres):
    try:
        client = MongoClient(**config_mongo)
        db = client['test']
        collection = db["emails"]
        data = collection.find()
        df = pd.DataFrame(list(data))
        df = df.drop(columns=['_id'])
        emails_data, addresses_data, email_addresses_data = process_emails(df)
        
        emails_df = pd.DataFrame(emails_data)
        addresses_df = pd.DataFrame(addresses_data)
        email_addresses_df = pd.DataFrame(email_addresses_data)
        
        conn = PostgresTool(**config_postgres)
        conn.insert_multiple_tables(emails_df, addresses_df, email_addresses_df)
        conn.close()
        print("Success Postgres")
        
        # Drop collection
        collection.drop()
        print("Drop collection")
        
    except Exception as e:
        print(f"Connect failed Postgres: {e}")
        raise

default_args = {
    'start_date': datetime(2024, 1, 1),
}

with DAG('kytranmoi', default_args=default_args, schedule_interval='*/5 * * * *', max_active_runs=1, concurrency=1, catchup=False) as dag:
    push_data_mongo = PythonOperator(
        task_id='push_data_mongo',
        python_callable=push_data_mongo,
        op_kwargs={'config_mongo': config_mongo, 'url_csv': url_csv},
    )


    task_postgres = PythonOperator(
        task_id='ETL_data',
        python_callable=ETL_data,
        op_kwargs={'config_mongo': config_mongo, 'config_postgres': config_postgres},
    )

push_data_mongo >> task_postgres