from flask import Flask, request, render_template
from MLModel import RFModel, LRModel
import pandas as pd
import urllib.parse
from flask_cors import CORS
from pymongo import MongoClient
# Weahter
import python_weather
import asyncio
import os
import datetime
# Weather END
import redis

redisClient = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

MONGO_URL = 'mongodb://localhost:27017/'
if 'MONGO_URL' in os.environ:
   MONGO_URL = os.environ['MONGO_URL']
DB_NAME = 'weather'
mongodb_client = MongoClient(MONGO_URL)
database = mongodb_client[DB_NAME]
print("Connected to the MongoDB database!")

app = Flask(__name__)
CORS(app)

rfModel = RFModel(model_path="./MLModels/rfModel")
lrModel = LRModel(model_path="./MLModels/lrModel")



async def getweather(cityName="Luetzelbach Hessen Germany"): # Return (temp, sunset_delta / 86400 []) -> AMBIENT_TEMPERATURE, IRRADIATION[] => Today, Tommorow, Day after Tommorow
    urlEncodedCityName = urllib.parse.quote(cityName) # "Luetzelbach%20Hessen%20Germany" for Weather API
    cityName = cityName.replace(" ", "_") # "Luetzelbach_Hessen_Germany" for Redis
    
    
    # Check if weather is in MongoDB
    # Find in MongoDB for day after tomorrow => implicit that today and tomorrow are also in MongoDB
    dayAfterTommorow = datetime.datetime.now() + datetime.timedelta(days=2)
    weatherAfterTommorw = database.weather.find_one({"city": cityName, "date": dayAfterTommorow.strftime("%Y-%m-%d")})
    if weatherAfterTommorw is not None:
        print("Found in MongoDB")
        weatherTommrow = database.weather.find_one({"city": cityName, "date": (dayAfterTommorow - datetime.timedelta(days=1)).strftime("%Y-%m-%d")})
        weatherToday = database.weather.find_one({"city": cityName, "date": (dayAfterTommorow - datetime.timedelta(days=2)).strftime("%Y-%m-%d")})
        return (weatherToday["weatherData"], weatherTommrow["weatherData"], weatherAfterTommorw["weatherData"]), weatherToday["format"]

        

    print("Not found in MongoDB, fetching from Weather API")
    
    
    # declare the client. format defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(format=python_weather.METRIC) as client:
        # https://wttr.in/Luetzelbach%20Hessen?format=j1

        # fetch a weather forecast from a city
        weather = await client.get(urlEncodedCityName) # TODO: Check if encoding is needed
        
        
        weathers = []
    
        # get the weather forecast for a few days
        for forecast in weather.forecasts:
            # sun_set = forecast.astronomy.sun_set - forecast.astronomy.sun_rise
            # datetime.time to datetime.datetime
            # dateKey = redisKey + ":" + forecast.date.strftime("%Y%m%d")
            # sun_delta = dateKey + ":sun_delta"
            sun_set = datetime.datetime.combine(datetime.date.today(), forecast.astronomy.sun_set)
            sun_rise = datetime.datetime.combine(datetime.date.today(), forecast.astronomy.sun_rise)
            sun_delta = sun_set - sun_rise
            # Get a value between 0 and 1
            # irradiations.append(sunset_delta.total_seconds() / 86400)
            weathers.append({
                "date": forecast.date,
                "sunrise": forecast.astronomy.sun_rise,
                "sunset": forecast.astronomy.sun_set,
                "sun_delta": sun_delta,
                "irradiation": sun_delta.total_seconds() / 86400,
                "temperature": forecast.temperature,
            })
            # temperatures.append(forecast.temperature)
            # redisClient.set(sun_delta, str(sunset_delta))
            print(forecast.date, forecast.astronomy.sun_set, "-",  forecast.astronomy.sun_rise, "=", sun_delta)
            # sunset_delta = forecast.astronomy.sun_set - forecast.astronomy.sun_rise
            # print(forecast.date, sunset_delta)
        #   print(forecast.date, forecast.astronomy.)
    
        for i in range(0, len(weathers)):
            # insert = {
            #     'city': cityName,
            #     'date': weathers[i]["date"].strftime("%Y%m%d"),
            #     'format': weather.format,
            #     'weatherData' : {
            #         'date': weathers[i]["date"].strftime("%Y%m%d"),
            #     'sunrise': weathers[i]["sunrise"].strftime("%H:%M:%S"),
            #     'sunset': weathers[i]["sunset"].strftime("%H:%M:%S"),
            #     'sun_delta': weathers[i]["sun_delta"].total_seconds(),
            #     'irradiation': weathers[i]["irradiation"],
            #     'temperature': weathers[i]["temperature"],
            #     }
            # }
            weathers[i]["date"] = weathers[i]["date"].strftime("%Y-%m-%d")
            weathers[i]["sunrise"] = weathers[i]["sunrise"].strftime("%H:%M:%S")
            weathers[i]["sunset"] = weathers[i]["sunset"].strftime("%H:%M:%S")
            weathers[i]["sun_delta"] = weathers[i]["sun_delta"].total_seconds()
            insert = {
                'city': cityName,
                'date': weathers[i]["date"],
                'format': weather.format,
                'weatherData' : weathers[i]
            }
            # Delete weatherData.date
            # del insert['weatherData']['date']
            database.weather.insert_one(insert)
            
        return weathers, weather.format




@app.route("/")
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('index.html', name=name)

@app.route("/predict", methods=['GET'])
async def predict():
    DAILY_YIELD = request.args.get('DAILY_YIELD', default = 0, type = int)
    TOTAL_YIELD = request.args.get('TOTAL_YIELD', default = 0, type = int)
    # AMBIENT_TEMPERATURE = request.args.get('AMBIENT_TEMPERATURE', default = 0, type = float)
    # IRRADIATION = request.args.get('IRRADIATION', default = 0, type = float)
    weathers, format = await getweather()
    predictions = []
    for i in range(0, len(weathers)):
        currTemp = weathers[i]["temperature"]
        currIrradiation = weathers[i]["irradiation"]
        xWithFeatureNames = pd.DataFrame([[DAILY_YIELD, TOTAL_YIELD, currTemp, currIrradiation]], columns=['DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE', 'IRRADIATION'])
        predictionLR = lrModel.predict(xWithFeatureNames)
        predictionRF = rfModel.predict(xWithFeatureNames)
        date = weathers[i]["date"]
        sunrise = weathers[i]["sunrise"]
        sunset = weathers[i]["sunset"]
        sun_delta = weathers[i]["sun_delta"]
        
        predictions.append({
            "Temperature": currTemp,
            "Date": date,
            "Sunrise": sunrise,
            "Sunset": sunset,
            "Sun_Delta": sun_delta,
            "Irradiation": currIrradiation,
            "Prediction_RF": predictionRF[0],
            "Prediction_LR": predictionLR[0],
        })
        
    # xWithFeatureNames = pd.DataFrame([[DAILY_YIELD, TOTAL_YIELD, AMBIENT_TEMPERATURE, IRRADIATION]], columns=['DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE', 'IRRADIATION'])
    # prediction = rfModel.predict(xWithFeatureNames)
    # predictionLR = lrModel.predict(xWithFeatureNames)
    # response = {
    #     "predictionRF": prediction[0],
    #     "predictionLR": predictionLR[0],
    #     "AMBIENT_TEMPERATURE": AMBIENT_TEMPERATURE,
    #     "irradiations": irradiations
    # }
    # # As JSON
    return {
        "Temperature_Format": format,
        "Prediction_unit": "kW",
        "Predictions": predictions
    }
        

    
if __name__ == '__main__':
    asyncio.run(getweather())
    app.run(host='0.0.0.0', port=80)