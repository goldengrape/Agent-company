import subprocess
import sys

# Ensure requests is installed
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import json

cities = ["Beijing", "Shanghai", "Shenzhen"]
results = {}

for city in cities:
    print(f"Fetching weather for {city}...")
    try:
        # Using wttr.in with format=j1 for JSON output
        response = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract 7 days of forecast
            forecast = []
            for day in data.get('weather', [])[:7]:
                forecast.append({
                    'date': day['date'],
                    'max_temp': day['maxtempC'],
                    'min_temp': day['mintempC'],
                    'desc': day['hourly'][4]['weatherDesc'][0]['value'] # Mid-day description roughly
                })
            results[city] = forecast
        else:
            results[city] = f"Error: Status code {response.status_code}"
    except Exception as e:
        results[city] = f"Error: {str(e)}"

with open("weather_report.json", "w") as f:
    json.dump(results, f, indent=4)
print("Weather data saved to weather_report.json")
