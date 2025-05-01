from src.logger import get_logger
from src.custom_exception import CustomException
import pandas as pd
import numpy as np
from src.feature_store import RedisFeatureStore
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import sys
import pickle

logger = get_logger(__name__)

class ModelTraining():
    def __init__(self, feature_store:RedisFeatureStore, model_save_path="artifacts/models/"):
        self.feature_store = feature_store
        self.model_save_path = model_save_path
        self.model = None

        os.makedirs(self.model_save_path, exist_ok=True)

        logger.info("Model Training class initialized")

    def load_data_from_redis(self, entity_ids):
        """
        Load data from Redis feature store for given entity IDs.
        """
        try:
            logger.info("Loading data from Redis...")
            data = []

            for entityid in entity_ids:
                features = self.feature_store.get_features(entityid)
                if features:
                    data.append(features)
                else:
                    logger.warning("Features not found")
            return data

        except Exception as e:
            logger.error(f"Error loading data from Redis: {e}")
            raise CustomException(str(e))
        
    def prepare_data(self):
        try:
            entity_ids = self.feature_store.get_all_entity_ids()

            train_entity_ids,test_entity_ids = train_test_split(entity_ids,test_size=0.2)

            train_data = self.load_data_from_redis(train_entity_ids)
            test_data = self.load_data_from_redis(test_entity_ids)

            """ 
            Lets convert to df format, redis gives in JSON format
            """

            train_df = pd.DataFrame(train_data)
            test_df = pd.DataFrame(test_data)

            X_train = train_df.drop("Survived",axis=1)
            logger.info(X_train.columns)
            X_test = test_df.drop("Survived",axis=1)
            logger.info(X_test.columns)
            y_train = train_df["Survived"]
            y_test = test_df["Survived"]

            logger.info("Prep for model training completed")
            return X_train,X_test,y_train,y_test

        except Exception as e:
            logger.error(f"Error preparing data (model_training file): {e}")
            raise CustomException(str(e))
        
    def param_tuning(self,X_train,y_train):
        try:
            param_distributions = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
                }
            
            rf = RandomForestClassifier(random_state=42)
            random_search = RandomizedSearchCV(rf, param_distributions, n_iter=10, cv=3, scoring='accuracy', random_state=42)
            random_search.fit(X_train, y_train)
            logger.info(f"Returning best params after param tuning: {random_search.best_params_}")
            return random_search.best_estimator_ 

        except Exception as e:
            logger.error(f"Error during parameter tuning (model_training file): {e}")
            raise CustomException(str(e))
        
    def train_and_eval(self,X_train,X_test,y_train,y_test):
        try:
            best_rf = self.param_tuning(X_train,y_train)

            y_pred = best_rf.predict(X_test)

            logger.info(f"Accuracy score for best rf model is :{accuracy_score(y_true=y_test,y_pred=y_pred)}")

            self.save_model(best_rf)

        except Exception as e:
            logger.error(f"Error during training and evaluating (model_training file): {e}")
            raise CustomException(str(e))
        
    def save_model(self,model):
        try:
            model_filename = f"{self.model_save_path}random_forest_model.pkl"

            with open(model_filename,'wb') as model_file:
                pickle.dump(model,model_file)

            logger.info(f"Model saved at{model_filename}")

        except Exception as e:
            logger.error(f"Error while saving model {e}")
            raise CustomException(str(e))
        
    def run(self):
        try:
            logger.info("Starting model training pipeline")

            X_train,X_test,y_train,y_test = self.prepare_data()

            self.train_and_eval(X_train,X_test,y_train,y_test)
            logger.info("End of Model Training pipeline...")

        except Exception as e:
            logger.error(f"Error while model training pipeline {e}")
            raise CustomException(str(e))
        
        
if __name__ == "__main__":
    feature_store = RedisFeatureStore()
    model_trainer = ModelTraining(feature_store)
    model_trainer.run()

    


             