from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from tensorflow import keras
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import r2_score

from tensorflow.keras import layers
import matplotlib.pyplot as plt


import time
import joblib
import os

class MLModel:
    def test(self, X_train, y_train, X_test, y_test):
        self.train(X_train, y_train)
        modelScore = self.evaluate(X_test, y_test)
        print(f"Score is {modelScore*100:.4f} % ")
        predictions = self.predict(X_test)
        cross_check = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
        cross_check["Error"] = cross_check["Actual"] - cross_check["Predicted"]
        print(cross_check.head(10))
        L2Error = np.sqrt(np.mean(np.square(cross_check["Error"])))
        print("L2 Error: ", L2Error) 
        
    def train(self, X_train,y_train):
        self.model.fit(X_train,y_train)

    def safe(self, model_path):
        joblib.dump(self.model, model_path)
        
    def predict(self, X_test):
        return self.model.predict(X_test)
    
    def evaluate(self, X_test, y_test):
        return self.model.score(X_test, y_test)

   


    
class LRModel(MLModel):
    def __init__(self, model_path=None):
        if model_path:
            self.model = joblib.load(model_path)
        elif os.environ.get("LR_MODEL_PATH"):
            self.model = joblib.load(os.environ.get("LR_MODEL_PATH"))
        else:
            self.model = LinearRegression()
    
            
    def testModel(self, X_train, y_train, X_test, y_test):
        currTime = time.time()
        print("**** LR Model ****")
        super().test(X_train, y_train, X_test, y_test)
        print("Time: ", time.time() - currTime)
    

class RFModel(MLModel):
    def __init__(self, model_path=None):
        if model_path:
            self.model = joblib.load(model_path)
        elif os.environ.get("RF_MODEL_PATH"):
            self.model = joblib.load(os.environ.get("RF_MODEL_PATH"))
        else:
            self.model = RandomForestRegressor()
    
    def testModel(self, X_train, y_train, X_test, y_test):
        print("**** RF Model ****")
        currTime = time.time()
        super().test(X_train, y_train, X_test, y_test)  
        print("Time: ", time.time() - currTime)
    

# # kNN
# currTime = time.time()

# score_list = []
# n_neighbors_list = []

# # for loop to find best fitting n_neighbor value
# for i in range(1, 100):
#     knn = neighbors.KNeighborsRegressor(n_neighbors=i)
#     knn.fit(X_train, y_train)

#     knn_score = knn.score(X_test, y_test)

#     score_list.append(knn_score)
#     n_neighbors_list.append(i)

# best_n_neighbor = n_neighbors_list[score_list.index(max(score_list))]
# print(f"kNN Best n_neighbor at {best_n_neighbor} with {max(score_list)*100:.4f} % - Time: {time.time() - currTime:.4f} s")
# # Predict a example
# print(f"\tPredict: {knn.predict([[daily_yield, total_yield, ambient_temperature, irradiation]])[0]:.4f} - Should be ca. 512.1125\n")


# # Decision Tree
# currTime = time.time()

# dtr = DecisionTreeRegressor()
# dtr.fit(X_train,y_train)

# dtr_score = dtr.score(X_test, y_test)
# print(f"DT Score is {dtr_score*100:.4f} % - Time: {time.time() - currTime:.4f} s")
# print(f"\tPredict: {dtr.predict([[daily_yield + 1000, total_yield, ambient_temperature, irradiation]])[0]:.4f} - Should be ca. 512.1125\n")
