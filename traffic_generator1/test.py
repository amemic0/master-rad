import requests
import time
import json
import os
import random
from datetime import datetime

SERVER_URL = "http://server2-service:8080/data"
WAIT_INTERVAL = int(os.getenv("WAIT_INTERVAL", 70))  # Default je 70 sekundi

# Osnovni podaci o prosječnim vremenskim prilikama za određeni grad
SEASONAL_WEATHER = {
    "winter": {"temp_range": (-5, 5), "humidity_range": (60, 90), "visibility_range": (500, 5000)},
    "spring": {"temp_range": (5, 15), "humidity_range": (50, 80), "visibility_range": (2000, 10000)},
    "summer": {"temp_range": (20, 35), "humidity_range": (30, 60), "visibility_range": (5000, 15000)},
    "autumn": {"temp_range": (10, 20), "humidity_range": (50, 80), "visibility_range": (2000, 10000)},
}

def get_season():
    """Određuje godišnje doba na osnovu trenutnog mjeseca."""
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

def adjust_for_time_of_day(temp, humidity, visibility):
    """Prilagođava podatke prema dobu dana."""
    hour = datetime.now().hour
    if 6 <= hour <= 18:  # Dan
        return temp, humidity, visibility
    else: 
        return temp - 3, min(humidity + 10, 100), max(visibility - 2000, 500)

def generisi_weather_podatke():
    """Generiše realistične podatke za vremenske prilike."""
    season = get_season()
    weather = SEASONAL_WEATHER[season]
    
    temp = round(random.uniform(*weather["temp_range"]), 2)
    humidity = round(random.uniform(*weather["humidity_range"]), 2)
    visibility = round(random.uniform(*weather["visibility_range"]), 2)

    temp, humidity, visibility = adjust_for_time_of_day(temp, humidity, visibility)

    air_pressure_kPa = round(random.uniform(95.0, 105.0), 2)  
    return {
        "intersection_id": 11283,  
        "Result": {
            "temperature_c": temp,
            "air_pressure_kPa": air_pressure_kPa,
            "humidity_percent": humidity,
            "visibility_meters": visibility
        }
    }



print(SEASONAL_WEATHER[get_season()])