import psycopg2
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
import os
from sklearn.model_selection import train_test_split
import sys
from config.database_config import DB_CONFIG
from config.paths_config import *


logger =  get_logger(__name__)

class Data_Ingestion:
    def __init__(self,dbparams,output_dir):
        self.dbparams = dbparams
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                host = self.dbparams['host'],
                port = self.dbparams['port'],
                dbname = self.dbparams['dbname'],
                user = self.dbparams['user'],
                password = self.dbparams['password']
            )

            logger.info("DB CONNECTION - SUCCESS.")
            return conn
        except Exception as e:
            logger.error(f"DB CONNECTION - FAILED. {e}")
            raise CustomException(str(e),sys)
        
    def extract_data(self):
        try:
            
            conn = self.connect_to_db()
            query = "SELECT * FROM public.titanic"
            df = pd.read_sql_query(query, conn)
            conn.close()
            logger.info("DATA EXTRACTION - SUCCESS.")
            return df
        except Exception as e:
            logger.error(f"DATA EXTRACTION - FAILED. {e}")
            raise CustomException(str(e),sys)
        
    def df_to_csv(self,df):
        try:
            train_df,test_df = train_test_split(df, test_size=0.2, random_state=42)
            train_df.to_csv(TRAIN_PATH, index=False)
            test_df.to_csv(TEST_PATH, index=False)

            logger.info("Data split and save done")

        except Exception as e:
            logger.error(f"DATA SPLIT AND SAVE - FAILED. {e}")
            raise CustomException(str(e),sys)
        
    def run(self):
        try:
            logger.info("DATA INGESTION PIPELINE- STARTED.")
            df = self.extract_data()
            self.df_to_csv(df)
            logger.info("DATA INGESTION PIPELINE- COMPLETED.")
        except Exception as e:
            logger.error(f"DATA INGESTION PIPELINE - FAILED. {e}")
            raise CustomException(str(e),sys)


if __name__ == '__main__':
    dataingestionobject = Data_Ingestion(DB_CONFIG, RAW_DIR)
    dataingestionobject.run()  