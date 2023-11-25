    CREATE TABLE IF NOT EXISTS rides (
        id SERIAL PRIMARY KEY,
        address_a VARCHAR(255),
        address_b VARCHAR(255),
        lat_a NUMERIC,
        long_a NUMERIC,
        lat_b NUMERIC,
        long_b NUMERIC,
        search_date TIMESTAMP,
        ip  VARCHAR(255),
        timestamp TIMESTAMP DEFAULT now()
    );