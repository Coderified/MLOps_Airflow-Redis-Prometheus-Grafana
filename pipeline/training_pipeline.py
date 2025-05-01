from src.data_ingestion import Data_Ingestion
from src.data_processing import DataProcessing
from src.model_training import RedisFeatureStore, ModelTraining
from config.paths_config import *
from config.database_config import *

if __name__ == '__main__':
    dataingestionobject = Data_Ingestion(DB_CONFIG, RAW_DIR)
    dataingestionobject.run()  

    featurestore = RedisFeatureStore()

    dataprocessing = DataProcessing(
        train_data_path=TRAIN_PATH,
        test_data_path=TEST_PATH,
        feature_store=featurestore
    )

    dataprocessing.run()

    feature_store = RedisFeatureStore()
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()
