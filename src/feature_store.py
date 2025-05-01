import redis
import json
import os
import sys


class RedisFeatureStore:
    #constructor to connect to docker where redis is running, redis needs a linus to run and docker provides that
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, 
                                              port=port, 
                                              db=db, 
                                              decode_responses=True)
    
    # Method used to store a single row using entity_id
    # it stores the features in a JSON format
    def store_features(self, entity_id, features):
        """
        Store features for a given entity in the Redis database.
        """
        key = f"entity:{entity_id}:features"
        self.client.set(key, json.dumps(features))
        #data is stored in JSON format for easy retrieval and manipulation.


    '''
    Method used to get features one by one    '''
    def get_features(self, entity_id):
        """
        Retrieve features for a given entity from the Redis database.
        """
        key = f"entity:{entity_id}:features"
        features = self.client.get(key)
        if features:
            return json.loads(features)
        else:
            return None
    
# Instead of storing and retrieve one by one, we combine with the next 2 methods
    #for storing all the rows using the sotre one row function
    def store_batch_features(self, batch_data):

        for entity_id,features in batch_data.items():
            self.store_features(entity_id, features)
       
        #Store features for multiple entities in the Redis database.

    
    #for storing all the rows using the sotre one row function
    def get_batch_features(self, entity_ids):
        batch_features = {}

        for entity_id in entity_ids:
            batch_features[entity_id] = self.get_features(entity_id)
        
        return batch_features
        #Store features for multiple entities in the Redis database.


# Entity ids stored in redis clinet in the form of keys, that is retrieved here

    def get_all_entity_ids(self):
        # * means all entity ids and feats
        keys = self.client.keys("entity:*:features")

        # splitting gives the format 
        # entity:entity_id:features, 
        # we only want entity_id
        entity_ids = [key.split(":")[1] for key in keys]
        return entity_ids
        
        