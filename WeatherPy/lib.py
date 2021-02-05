import pandas as pd
import numpy as np
import requests
import json
from config import weather_api_key
from citipy import citipy

'''
Generate DataFrame for city-weather
Receives a number of rows to randomly generate lat and lon.
Once generated, the file will be cached to avoid unnecessary requests.
To force a new generation and request, pass argument force_new as true.
'''
def get_city_weather_df(n_rows=10, force_new=False):
  cache_data_file_path = '.cache.csv'
  coords_df = None
  # see if there is a cache file to use
  try:
      coords_df = pd.read_csv(cache_data_file_path, index_col=0)
      print("Data loaded from cache")
  except OSError as err:
      print("No cache file found")

  # If no cache file was found or a new one is forced
  # generate the data
  if (coords_df is None or force_new):
      # Generate latitudes(-90 to 90) and longitudes(-180 to 180)
      # using random number generator and multiply by 100
      coords_df = pd.DataFrame({
          "Lng": np.random.uniform(-180, 180, n_rows), # -180 | 180
          "Lat": np.random.uniform(-90, 90, n_rows) # -90 | 90
      })

      # Now lets get the cities name and countries
      city_names = []
      country_codes = []
      temperature = []
      humidity = []
      cloudiness = []
      wind_speed = []
      date = []

      for i in range(0, len(coords_df['Lat'])):
          lat = coords_df.iloc[i]['Lat']
          lon = coords_df.iloc[i]["Lng"]

          # get the city data
          city = citipy.nearest_city(lat, lon)

          city_names.append(city.city_name)
          country_codes.append(city.country_code)

          # get the weather data
          weather = get_weather_by_coords(lat, lon)

          temperature.append(weather["main"]["temp_max"])
          humidity.append(weather["main"]["humidity"])
          cloudiness.append(weather["clouds"]["all"])
          wind_speed.append(weather["wind"]["speed"])
          date.append(weather["dt"])
      
      # add values to the DataFrame
      coords_df['City']=city_names
      coords_df['Country']=country_codes
      coords_df['Max Temp']=temperature
      coords_df['Humidity']=humidity
      coords_df['Cloudiness']=cloudiness
      coords_df['Wind Speed']=wind_speed
      coords_df['Date']=date

      # cache the file for later...
      coords_df.to_csv(cache_data_file_path)

  # lets peek at our data frame
  return coords_df

'''
Get the data from the weather api
'''
def get_weather_by_coords(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}"

    try:
        print(f"Requesting for ({lat}, {lon})")
        response = requests.get(url)
        response.raise_for_status()

        return json.loads(
            response.text
        )
    except requests.exceptions.HTTPError as err:
        print("Request Error:", err)
        raise SystemExit(err)
