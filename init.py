import psycopg2
import os
import pandas as pd

from app.modules.db import connect_to_database

def create_tables(conn, cursor):
    path = "table_schema/"
    tables = os.listdir(path)
    print(tables)
    for table in tables:
        with open(path + table, 'r') as file:
            sql_create = file.read()
            
        cursor.execute(sql_create)
        conn.commit()
        print(f"Table {table.replace('.sql', '')} created.")
    


def import_data_sample(conn, cursor):
    path = "sample_data/"
    tables = os.listdir(path)
    
    for table in tables:
       
        table_name = table.replace("_sample.csv", "")
        file_path = os.path.join(path, table)
        
        # Wczytaj dane z pliku CSV za pomocą Pandas
        df = pd.read_csv(file_path)
        
        # Zamień kolumny DataFrame na listy, które można wstawić do bazy danych
        data_values = df.values.tolist()
        
        # Tworzenie odpowiedniej kwerendy SQL
        insert_query = f"INSERT INTO {table_name} (location, temperature, humidity, precipitation, wind_speed, wind_direction, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        print(insert_query)
        # Wstawianie danych do bazy danych
        try:
            print(data_values)
            cursor.executemany(insert_query, data_values)
            conn.commit()
            print(f"Dane z pliku {table} zostały zaimportowane do tabeli {table_name}.")
        except Exception as e:
            print(f"Błąd podczas importowania danych z pliku {table}: {str(e)}")
    
class DBSession:

    def __init__(self):
        


    def create_tables(conn, cursor):
        path = "table_schema/"
        tables = os.listdir(path)
        print(tables)
        for table in tables:
            with open(path + table, 'r') as file:
                sql_create = file.read()
                
            cursor.execute(sql_create)
            conn.commit()
            print(f"Table {table.replace('.sql', '')} created.")
        


# def import_data_sample(conn, cursor):
#     path = "init/sample_data/"
#     tables = os.listdir(path)
    
#     for table in tables:
#         with open(path + table, 'r') as file:
#             if table == "weather_online_sample.csv":
#                 insert_query = f"INSERT INTO device_data (location,temperature,humidity,precipitation,wind_speed,wind_direction,timestamp) VALUES "
            
            
#             insert_query = insert_query + "('{i}', '{phrase}')"
#             cursor.execute(insert_query)
#             conn.commit()

#         cursor.execute(sql_create)
#         conn.commit()
#         print(f"Table {table.replace('.sql', '')} created.")

# Nawiązanie połączenia z bazą danych
conn, cursor = connect_to_database()

# Tworzenie tabeli i wstawianie danych (jeśli nie istnieje)
create_tables(conn, cursor)
import_data_sample(conn, cursor)

# Wstawianie przykładowych danych
sample_data = [
    "Twoje ograniczenia sa tylko w twojej glowie.",
    "Sukces to nie końcówka, ale droga.",
    "Zaczynaj tam, gdzie jesteś. Użyj tego, co masz. Zrób, co możesz.",
    "Wiara w siebie jest pierwszym sekretem sukcesu.",
    "Najlepszym czasem na rozpoczęcie jest teraz.",
    "Sukces to suma małych wysiłków powtarzanych dzień po dniu.",
    "Nie oglądaj się wstecz. Idź naprzód, osiągniesz swoje cele.",
    "Wierzę w siebie i w swoje możliwości.",
    "Zmiany prowadzą do postępu.",
    "Nie poddawaj się. Nigdy nie wiesz, jak blisko jesteś do sukcesu.",
    "Marzenia nie pracują, dopóki nie zaczynasz działać.",
    "Twój czas jest teraz.",
    "Sukces to kwestia wyboru.",
    "Życie jest krótkie. Złap każdą okazję.",
    "Czasami musisz pokonać swoje obawy, aby osiągnąć swoje cele.",
    "Sukces to suma małych wysiłków powtarzanych dzień po dniu.",
    "Zawsze warto dążyć do doskonałości.",
    "Praca jest kluczem do sukcesu.",
    "Wierz w siebie i osiągniesz wiele.",
    "Twoje cele są możliwe do osiągnięcia."
]

for i, phrase in enumerate(sample_data):
    insert_query = f"INSERT INTO device_data (device_id, content) VALUES ('{i}', '{phrase}');"
    cursor.execute(insert_query)
    conn.commit()

# Wykonanie zapytania do tabeli i wyświetlenie wyników
select_query = "SELECT * FROM device_data;"
cursor.execute(select_query)
results = cursor.fetchall()

for row in results:
    print(f"ID: {row[0]}, device_id: {row[1]}, Content: {row[2]}")

# Zamknięcie połączenia

# create_weather_table(conn, cursor)
# print("Weather table crated")
# LOCATION = 'Gdansk'  # Zmień na swoje miasto
# update_weather_data(conn, cursor, LOCATION)
# print("Weather data updated")

conn.close()


