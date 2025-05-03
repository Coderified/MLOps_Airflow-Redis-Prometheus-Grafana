import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify, request
import pickle

from src.logger import get_logger

from alibi_detect.cd import KSDrift
from src.feature_store import RedisFeatureStore # to import reference data for drift comparison
from sklearn.preprocessing import StandardScaler #for scaling the data fo comparison - not mandatory


from prometheus_client import start_http_server, Counter, Gauge #starts prometheus server



logger = get_logger(__name__)

app = Flask(__name__, template_folder = "templates")
#specifies the templates folder which flask by default searches for 

#select customer mterics with counter
prediction_count = Counter('prediction_count',"Number of prediction counts")
drift_count = Counter("drift_count","Number of times data drift is detected")



MODEL_PATH = "artifacts/models/random_forest_model.pkl"

with open(MODEL_PATH,'rb') as model_file:
    model = pickle.load(model_file)

#List feature names

FEATURE_NAMES = ['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'Familysize', 'Isalone',
       'HasCabin', 'Title', 'Pclass_Fare', 'Age_Fare']

feature_store = RedisFeatureStore()
scaler = StandardScaler()

def fit_scaler_on_refdata():
    #retireve data from feature_store

    entity_ids = feature_store.get_all_entity_ids()
    all_features = feature_store.get_batch_features(entity_ids=entity_ids)

    #converting JSON to pandas df
    all_features_df = pd.DataFrame.from_dict(all_features,orient='index')[FEATURE_NAMES]

    scaler.fit(all_features_df)

    return scaler.transform(all_features_df)


# Get reference historical data

historical_data = fit_scaler_on_refdata()

# Applying KSDrift to identify the drift

ksd = KSDrift(x_ref = historical_data,p_val = 0.05)


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/predictor", methods=['POST'])

def predict():
    try:
        data =request.form
        Age = float(data["Age"])
        Fare = float(data['Fare'])
        Pclass = int(data['Pclass'])
        Sex = int(data['Sex'])
        Embarked = int(data['Embarked'])
        Familysize = int(data['Familysize'])
        Isalone = int(data['Isalone'])
        HasCabin = int(data['HasCabin'])
        Title = int(data['Title'])
        Pclass_Fare = float(data['Pclass_Fare'])
        Age_Fare = float(data['Age_Fare'])

        features = pd.DataFrame([[Pclass, Sex,Age, Fare,Embarked, Familysize, Isalone,
        HasCabin, Title, Pclass_Fare, Age_Fare]], columns = FEATURE_NAMES)

        # Data Drift Detection  

        # scaling the current data stored in the features in 2 lines above

        features_scaled = scaler.transform(features)

        # KSD IS TRAINED ON HISTORICAL / REF DATA AND IT PREDICTS THE CURRENT / NEW DATA

        drift = ksd.predict(features_scaled)

        print("Drift predicted by ksdrift :", drift)

        
        # Drift predicted by ksdrift : 

        #     {'data': {'is_drift': 0, 
        #         'distance': array([0.55898875, 0.34410113, 0.869382  , 0.5828652 , 0.8244382 ,
        #           0.3974719 , 0.3974719 , 0.7766854 , 0.58848315, 0.98174155,
        #           0.9719101 ], dtype=float32), 'p_val': array([0.8820225 , 1.        , 0.26123595, 0.83426964, 0.3511236 ,
        #            1.        , 1.        , 0.44662923, 0.8230337 , 0.03651685,0.05617978], dtype=float32), 
        #       'threshold': 0.004545454545454546}, 'meta': {'name': 'KSDrift', 'online': False, 
        #          'data_type': None, 'version': '0.12.0', 'detector_type': 'drift'}}
       

        drift_response = drift.get('data',{})

        is_drift = drift_response.get('is_drift',None)

        if is_drift is not None and is_drift == 1:

            print("DRIFT DETECTED")
            logger.info("DRIFT DETECTED")

            drift_count.inc(1)
    

        
        prediction = model.predict(features)[0]
        prediction_count.inc(1)

        if prediction==1:
            result = "Survived"
        else:
            result = "Rest in Peace"

        return render_template('index.html',prediction_text = f"Prediction : {result}")

    except Exception as e:
        return jsonify({'Error is' :str(e)})


#to access inbuilt metricin prometheus we set route

@app.route('/metrics')

def metric():

    #to send all metrics to the route defined
    from prometheus_client import generate_latest
    from flask import Response

    return Response(generate_latest(),content_type='text/plain')


if __name__ == '__main__':
    start_http_server(8000)
    app.run(debug = True, host = '0.0.0.0', port = 5000) 



