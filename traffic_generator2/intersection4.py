import requests
import time
import json
import os
import random
from datetime import datetime

SERVER3_URL = "http://server3-service:8080/data"  # URL servera3
WAIT_INTERVAL = int(os.getenv("WAIT_INTERVAL", 70))  # Default je 70 sekundi

# Osnovni podaci za vremenske prilike
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
    """Prilagođava vremenske podatke prema dobu dana."""
    hour = datetime.now().hour
    if 6 <= hour <= 18:  # Dan
        return temp, humidity, visibility
    else:
        return temp - 3, min(humidity + 10, 100), max(visibility - 2000, 500)

def generisi_weather_podatke():
    """Generiše podatke za vremenske prilike."""
    season = get_season()
    weather = SEASONAL_WEATHER[season]
    
    temp = round(random.uniform(*weather["temp_range"]), 2)
    humidity = round(random.uniform(*weather["humidity_range"]), 2)
    visibility = round(random.uniform(*weather["visibility_range"]), 2)

    temp, humidity, visibility = adjust_for_time_of_day(temp, humidity, visibility)
    air_pressure_kPa = round(random.uniform(95.0, 105.0), 2)

    rul = random.choice(["Y", "N"]) 
    if rul == "Y":
        int_id = 111
    else:
        int_id = 222
    return {
        "forwarding_action": rul,
        "intersection_id": int_id,  
        "Result": {
            "temperature_c": temp,
            "air_pressure_kPa": air_pressure_kPa,
            "humidity_percent": humidity,
            "visibility_meters": visibility
        },
        "param_type": "weather"
    }

def generisi_traffic_podatke():
    """Generiše podatke za promet."""
    trenutno_vrijeme = datetime.now()
    sat = trenutno_vrijeme.hour
    osnovne_maksimalne_vrijednosti = [
        10, 10, 5, 5, 10, 40, 50, 60, 70, 50, 50, 40, 
        40, 30, 60, 70, 75, 40, 30, 30, 30, 10, 20, 10
    ]
    maksimalan_broj = int(osnovne_maksimalne_vrijednosti[sat] * 0.8)
    minimalan_broj = 1
    brojevi = [random.randint(minimalan_broj, maksimalan_broj) for _ in range(4)]


    rul = random.choice(["Y", "N"]) 
    if rul == "Y":
        int_id = 111
    else:
        int_id = 222
    return {
        "forwarding_action": rul,
        "intersection_id": int_id,
        "Result": {
            "north_side": brojevi[0],
            "south_side": brojevi[1],
            "east_side": brojevi[2],
            "west_side": brojevi[3]
        },
        "param_type": "traffic"
    }

def send_request():
    """Generiše i šalje zahtjev prema serveru3."""
    try:
        param_type = random.choice(["weather", "traffic"])
        if param_type == "weather":
            data = generisi_weather_podatke()
        else:
            data = generisi_traffic_podatke()

        print(f"Slanje podataka ({param_type}):", json.dumps(data, indent=2))

        # Slanje zahtjeva prema serveru3
        response = requests.post(SERVER3_URL, json=data)
        if response.status_code == 200:
            print("Podaci su uspješno poslani:", response.json())
        else:
            print(f"Greška prilikom slanja podataka: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Došlo je do greške: {e}")

if __name__ == "__main__":
    print(f"Početak slanja zahtjeva prema serveru3 na svakih {WAIT_INTERVAL} sekundi...")
    while True:
        send_request()
        print(f"Čekanje {WAIT_INTERVAL} sekundi...")
        time.sleep(WAIT_INTERVAL)
