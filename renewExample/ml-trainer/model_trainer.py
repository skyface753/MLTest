
import pandas as pd 
from sklearn.preprocessing import LabelEncoder
import warnings
from sklearn.model_selection import train_test_split
import time
from MLModel import RFModel, LRModel
import matplotlib.pyplot as plt


mlModelsFolder = "./MLModels/"

warnings.filterwarnings("ignore")

generation_data = pd.read_csv('./solar-power-generation-data/Plant_1_Generation_Data.csv')
weather_data = pd.read_csv('./solar-power-generation-data/Plant_1_Weather_Sensor_Data.csv')

# print(generation_data.head())
# print(weather_data.head())

# print(generation_data['SOURCE_KEY'].unique().size)
# print(weather_data['SOURCE_KEY'].unique().size)

# print(generation_data['PLANT_ID'].unique().size)
# print(weather_data['PLANT_ID'].unique().size)

generation_data.info()

generation_data['DATE_TIME'] = pd.to_datetime(generation_data["DATE_TIME"]) # Convert to datetime
weather_data['DATE_TIME'] = pd.to_datetime(weather_data["DATE_TIME"]) # Convert to datetime

df = pd.merge(generation_data.drop(columns=['PLANT_ID']), weather_data.drop(columns=['PLANT_ID', 'SOURCE_KEY']), on='DATE_TIME') # Merge the two dataframes on the date_time column and drop the plant_id column from both dataframes as it is the same for both dataframes 

# Check for null values
# print(df.head())
# print(df.isnull().sum())
# print(df.describe())
# print(df.count())

# Plotting
# pd.plotting.scatter_matrix(df, figsize=(15,15))
# plt.show()

corr = df.corr() # Correlation matrix
# corr.style.background_gradient(cmap='coolwarm') # Heatmap

encoder = LabelEncoder() # Encode the source key column
df['SOURCE_KEY_NUMBER'] = encoder.fit_transform(df['SOURCE_KEY']) # Fit and transform the source key column
# df.info()

# print("Date unique", df['DATE_TIME'].unique().size) 

# df_ml = df.copy() 
X = df[['DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE', 'IRRADIATION']] # Features
y = df['AC_POWER'] # Label

# sns.displot(data=df, x="AMBIENT_TEMPERATURE", kde=True, bins = 100,color = "red", facecolor = "#3F7F7F",height = 5, aspect = 3.5) # Histogram
# plt.show()

corr = X.corr() # Correlation matrix of features
# corr.style.background_gradient(cmap='coolwarm') # Heatmap

# Hyperparameter
trainTestSplit = 0.2

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=trainTestSplit, random_state=42, shuffle=True) # Split the data into training and testing sets
# print("Shape of X_train: ", X_train.shape)


# *** Linear Regression ***

# lrModel = LRModel(model_path=mlModelsFolder +"lrModel") # Load Modell from file
lrModel = LRModel() # New Full Modell with auto train, test and evaluation

lrModel.testModel(X_train, y_train, X_test, y_test)
lrModel.safe(model_path=mlModelsFolder + "lrModel")


# *** Random Forest ***

# rfModel = RFModel(model_path=mlModelsFolder +"rfModel") # Load Modell
rfModel = RFModel()

rfModel.testModel(X_train, y_train, X_test, y_test)
rfModel.safe(model_path=mlModelsFolder + "rfModel.pkl")