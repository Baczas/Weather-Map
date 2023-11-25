    CREATE TABLE IF NOT EXISTS weather (
        id SERIAL PRIMARY KEY,
        ride_id INTEGER,
        lat NUMERIC,
        long NUMERIC,
        search_date TIMESTAMP,
        temperature VARCHAR(255),
        humidity VARCHAR(255),
        wind_speed VARCHAR(255),
        wind_direction VARCHAR(255),
        weather_description VARCHAR(255),
        weather_icon  VARCHAR(255),
        timestamp TIMESTAMP DEFAULT now()
    );





