import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from src.logger import get_logger
from src.custom_exception import CustomException
from src.feature_store import RedisFeatureStore 
from config.paths_config import *
import sys


logger=get_logger(__name__)

class DataProcessing:
    def __init__(self, train_data_path, test_data_path, feature_store:RedisFeatureStore):
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        
        self.train_data = None
        self.test_data = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None

        self.X_resampled = None
        self.y_resampled = None

        self.feature_store = feature_store

        logger.info("DataProcessing class initialized")

    def load_data(self):
        try:
            self.train_data = pd.read_csv(self.train_data_path)
            self.test_data = pd.read_csv(self.test_data_path)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException(str(e),sys)
        
    def preprocess_data(self):
        try:
            self.train_data['Age'] = self.train_data['Age'].fillna(self.train_data['Age'].median())
            self.train_data['Embarked'] = self.train_data['Embarked'].fillna(self.train_data['Embarked'].mode()[0])
            self.train_data['Fare'] = self.train_data['Fare'].fillna(self.train_data['Fare'].median())
            self.train_data['Sex'] = self.train_data['Sex'].map({'male': 0, 'female': 1})
            self.train_data['Embarked'] = self.train_data['Embarked'].astype('category').cat.codes

            self.train_data['Familysize'] = self.train_data['SibSp'] + self.train_data['Parch'] + 1
            self.train_data['Isalone'] = (self.train_data['Familysize'] == 1).astype(int)
            self.train_data['HasCabin'] = self.train_data['Cabin'].notnull().astype(int)
            self.train_data['Title'] = self.train_data['Name'].str.extract(' ([A-Za-z]+)\.', expand=False).map(
                {'Mr': 0, 'Miss': 1, 'Mrs': 2, 'Master': 3, 'Rare': 4} ).fillna(4)
            self.train_data['Pclass_Fare'] = self.train_data['Pclass'] * self.train_data['Fare']
            self.train_data['Age_Fare'] = self.train_data['Age'] * self.train_data['Fare']

            logger.info("Data preprocessing done successfully")

        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            raise CustomException(str(e),sys)
        
    def split_handle_data(self):

        try:
            X = self.train_data[['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'Familysize', 'Isalone', 'HasCabin', 'Title', 'Pclass_Fare', 'Age_Fare']]
            y = self.train_data['Survived']

            smote = SMOTE(random_state=42)
            self.X_resampled, self.y_resampled = smote.fit_resample(X, y)

            logger.info("Data resampling done successfully")

            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            logger.info("Data split into training and testing sets")
        except Exception as e:
            logger.error(f"Error in imbal handling: {e}")
            raise CustomException(str(e),sys)
    '''
    Store featue in redis 
    '''    
    def store_features(self):
        try:
            batch_data = {} # this is the input to store_batch_features method in featurestore Class
            for index, row in self.train_data.iterrows():
                entity_id = row['PassengerId'] # this is the primary key in the dataset - used as entity_id in redis
                # if that was not there, we can use the index as entity_id
                features = {
                    'Pclass': row['Pclass'],
                    "Sex": row['Sex'],
                    "Age": row['Age'],
                    "Fare": row['Fare'],
                    "Embarked": row['Embarked'],
                    "Familysize": row['Familysize'],
                    "Isalone": row['Isalone'],
                    "HasCabin": row['HasCabin'],
                    "Title": row['Title'],
                    "Pclass_Fare": row['Pclass_Fare'],
                    "Age_Fare": row['Age_Fare'],
                    "Survived": row['Survived']
                }

                batch_data[entity_id] = features


            self.feature_store.store_batch_features(batch_data)
            logger.info("Features stored in FeatureStore successfully")
        except Exception as e:  
            logger.error(f"Error storing features: {e}")
            raise CustomException(str(e),sys)   
        
    def retrieve_features(self, entity_ids):
        try:
            batch_features = self.feature_store.get_batch_features(entity_ids)
            if batch_features:
                return batch_features
            else:   
                logger.warning("No features found for the given entity IDs")
                return None           
        except Exception as e:
            logger.error(f"Error retrieving features: {e}")
            raise CustomException(str(e),sys)
        
    def run(self):
        try:
            logger.info("Starting data processing pipeline")
            self.load_data()
            self.preprocess_data()
            self.split_handle_data()
            self.store_features()
            logger.info("Data processing pipeline completed successfully")
        except Exception as e:
            logger.error(f"Error in data processing pipeline: {e}")
            raise CustomException(str(e),sys)
        
if __name__ == "__main__":
    featurestore = RedisFeatureStore()

    dataprocessing = DataProcessing(
        train_data_path=TRAIN_PATH,
        test_data_path=TEST_PATH,
        feature_store=featurestore
    )

    dataprocessing.run()

    print(dataprocessing.retrieve_features(entity_ids=[332, 734]))# Example entity IDs to retrieve features for



