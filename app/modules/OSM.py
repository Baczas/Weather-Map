import requests
import folium
import polyline
import datetime
import csv
import os
from modules.db import connect_to_database

# Weather icons and descriptions mapping
weather_icons_test = {
    '01d': ['sun', 'clear sky'],
    '01n': ['moon', 'clear sky'],
    '02d': ['cloud-sun', 'few clouds'],
    '02n': ['cloud-moon', 'few clouds'],
    '03d': ['cloud', 'scattered clouds'],
    '03n': ['cloud', 'scattered clouds'],
    '04d': ['cloud', 'broken clouds'],
    '04n': ['cloud', 'broken clouds'],
    '09d': ['cloud-showers-heavy', 'shower rain'],
    '09n': ['cloud-showers-heavy', 'shower rain'],
    '10d': ['cloud-rain', 'rain'],
    '10n': ['cloud-rain', 'rain'],
    '11d': ['thunderstorm', 'thunderstorm'],
    '11n': ['thunderstorm', 'thunderstorm'],
    '13d': ['snowflake', 'snow'],
    '13n': ['snowflake', 'snow'],
    '50d': ['smog', 'mist'],
    '50n': ['smog', 'mist']
}

# Function to retrieve travel time between points
def get_travel_time(point1, point2):
    api_url = f"http://router.project-osrm.org/route/v1/driving/{point1[1]},{point1[0]};{point2[1]},{point2[0]}?overview=false"
    response = requests.get(api_url)
    data = response.json()
    if 'routes' in data and len(data['routes']) > 0:
        route = data['routes'][0]
        return route['duration']
    return 0

# Geocoding function for addresses
def geocode_address(address):
    nominatim_url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    response = requests.get(nominatim_url)
    data = response.json()
    
    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return (lat, lon)
    else:
        return None

# Function to retrieve the API key from a file
def get_api_key():
    with open('API_KEY', 'r') as file:
        return file.read()

# Function to get weather icons from a CSV file
def get_weather_icons(file_path):
    icon_dict = {}
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ow_id = row['ow_id']
            fa_id = row['fa_id']
            description = row['description']
            icon_dict[ow_id] = {'fa_id': fa_id, 'description': description}
   
    return icon_dict

# Function to get weather information using the OpenWeatherMap API
def get_weather(latitude, longitude, datetime):
    base_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

    timestamp = int(datetime.timestamp())
    api_key = get_api_key()
    
    query_params = {
        "lat": latitude,
        "lon": longitude,
        "dt": timestamp,  # Unix timestamp for the desired time
        "appid": api_key,
    }

    response = requests.get(base_url, params=query_params)
    data = response.json()

    if response.status_code == 200:
        current_weather = data["data"][0]
        temperature = round(float(current_weather["temp"]) - 273.15, 2)
        weather_description = current_weather["weather"]
        humidity = current_weather["humidity"]
        wind_speed = current_weather["wind_speed"]

        print(f"Weather checked for {latitude}, {longitude}")

        return {
            "temperature": temperature,
            "weather_description": weather_description[0]["description"],
            "weather_icon": current_weather["weather"][0]["icon"],
            "humidity": humidity,
            "wind_speed": wind_speed,
        }
    else:
        return None

# Function for route search and mapping
def route_search(city_a, city_b, path='route_map.html', date=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"), ip=None):
    # Coordinates of point A (Warsaw) and point B (Gdansk)
    point_a = geocode_address(city_a)
    point_b = geocode_address(city_b)

    current_time = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M")

    api_url = f"http://router.project-osrm.org/route/v1/driving/{point_a[1]},{point_a[0]};{point_b[1]},{point_b[0]}?overview=full"
    response = requests.get(api_url)
    data = response.json()

    #######################################################
    conn, cursor = connect_to_database()
    insert_query = f"INSERT INTO rides (address_a, address_b, lat_a, long_a, lat_b, long_b, search_date, ip) VALUES ('{city_a}', '{city_b}', {point_a[0]}, {point_a[1]}, {point_b[0]}, {point_b[1]}, '{date}', '{ip}') RETURNING id;"

    print(insert_query)
    cursor.execute(insert_query)
    new_ride_id = cursor.fetchone()[0] 
    conn.commit()

    print(f"new_ride_id: {new_ride_id}")
    #######################################################

    weather_icons = get_weather_icons('icon_map.csv')

    if 'routes' in data and len(data['routes']) > 0:
        route = data['routes'][0]
        geometry = route['geometry']
        total_duration = route['duration']

        decoded_geometry = polyline.decode(geometry)
        m = folium.Map(location=point_a, zoom_start=6)

        font_awesome_css = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.3.0/css/all.min.css'
        folium.Element('<link rel="stylesheet" href="' + font_awesome_css + '">').add_to(m)

        folium.PolyLine(locations=decoded_geometry, color='blue').add_to(m)

        #######################################################
        weather_list = []
        weather_data = get_weather(point_a[0], point_a[1], current_time)
        weather_list.append([new_ride_id, point_a[0], point_a[1], current_time, weather_data["temperature"], weather_data["humidity"], weather_data["wind_speed"], "wind_direction ", weather_data["weather_description"], weather_data["weather_icon"]])
        #######################################################

        popup_text = f"""
                    <div style="white-space: nowrap;">
                        <strong>{city_a}</strong><br>
                        Departure time: {current_time.strftime("%H:%M")}
                        <br><br>
                        {weather_data["weather_description"]}<br>
                        <i class="fas fa-thermometer-half"></i> {weather_data["temperature"]}°C<br>
                        <i class="fas fa-tint"></i> {weather_data["humidity"]}%<br>
                        <i class="fas fa-wind"></i> {weather_data["wind_speed"]} m/s
                    </div>
                """             
        folium.Marker(location=point_a, icon=folium.Icon(icon=weather_icons_test[weather_data["weather_icon"]][0], color='green', prefix='fa'), popup=popup_text).add_to(m)

        km_interval = 100  
        current_distance = 0

        for i in range(len(decoded_geometry) - 1):
            lat1, lon1 = decoded_geometry[i]
            lat2, lon2 = decoded_geometry[i + 1]
            distance = ((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) ** 0.5 * 111.32
            current_distance += distance

            if current_distance >= km_interval:
                time_to_next_point = get_travel_time(point_a, (lat2, lon2))
                at_point_time = current_time + datetime.timedelta(seconds=time_to_next_point)

                weather_data = get_weather(lat2, lon2, at_point_time)

                ot = str(datetime.timedelta(seconds=time_to_next_point)).split(":")[:2]
                popup_text = f"""
                    <div style="white-space: nowrap;">
                        {at_point_time.strftime("%d %b, %H:%M")}<br>
                        ({ot[0]}:{ot[1]}h)
                        <br><br>
                        {weather_data["weather_description"]}<br>
                        <i class="fas fa-thermometer-half"></i> {weather_data["temperature"]}°C<br>
                        <i class="fas fa-tint"></i> {weather_data["humidity"]}%<br>
                        <i class="fas fa-wind"></i> {weather_data["wind_speed"]} m/s
                    </div>
                """                
                folium.Marker(location=(lat1, lon1), icon=folium.Icon(icon=weather_icons[weather_data["weather_icon"]]["fa_id"], color='blue', prefix='fa'), popup=popup_text).add_to(m)
                km_interval += 100

                #######################################################
                weather_list.append([new_ride_id, lat1, lon1, at_point_time, weather_data["temperature"], weather_data["humidity"], weather_data["wind_speed"], "wind_direction ", weather_data["weather_description"], weather_data["weather_icon"]])
                #######################################################

        time_to_next_point = get_travel_time(point_a, point_b)
        at_point_time = current_time + datetime.timedelta(seconds=time_to_next_point)
        weather_data = get_weather(point_b[0], point_b[1], at_point_time)
        ot = str(datetime.timedelta(seconds=time_to_next_point)).split(":")[:2]

        popup_text = f"""
            <div style="white-space: nowrap;">
                <strong>{city_b}</strong><br>
                Arrival time: {at_point_time.strftime("%d %b, %H:%M")}<br>
                Travel time: {ot[0]}:{ot[1]}h
                <br><br>
                {weather_data["weather_description"]}<br>
                <i class="fas fa-thermometer-half"></i> {weather_data["temperature"]}°C<br>
                <i class="fas fa-tint"></i> {weather_data["humidity"]}%<br>
                <i class="fas fa-wind"></i> {weather_data["wind_speed"]} m/s
            </div>
        """  
        folium.Marker(location=point_b, icon=folium.Icon(icon=weather_icons[weather_data["weather_icon"]]["fa_id"], color='red', prefix='fa'), popup=popup_text).add_to(m)

        #######################################################
        weather_insert_query = f"INSERT INTO weather (ride_id, lat, long, search_date, temperature, humidity, wind_speed, wind_direction, weather_description, weather_icon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        weather_list.append([new_ride_id, point_b[0], point_b[1], at_point_time, weather_data["temperature"], weather_data["humidity"], weather_data["wind_speed"], "wind_direction ", weather_data["weather_description"], weather_data["weather_icon"]])
        
        try:
            cursor.executemany(weather_insert_query, weather_list)
            conn.commit()
            print(f"Imported {len(weather_list)} rows to the weather table")
        except Exception as e:
            print(f"Error while importing data to the weather table: {str(e)}")
        #######################################################

        m.save(path)
    else:
        print("Failed to find a route.")

if __name__ == "__main__":
    city_a = "Rakoczego 23, Gdańsk"
    city_b = "Toruń"
    map = route_search(city_a, city_b)
    file_name = "route_map.html"


# with open(file_name, "w", encoding="utf-8") as file:
#     # Write HTML code to the file
#     file.write(map)
