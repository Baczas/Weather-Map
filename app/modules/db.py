import psycopg2
import os
import time

# Fetching PostgreSQL environment variables
postgres_host = os.environ.get('POSTGRES_HOST')
postgres_port = os.environ.get('POSTGRES_PORT')
postgres_db = os.environ.get('POSTGRES_DB')
postgres_user = os.environ.get('POSTGRES_USER')
postgres_password = os.environ.get('POSTGRES_PASSWORD')

# Database connection parameters
db_params = {
    'host': postgres_host,
    'port': postgres_port,
    'database': postgres_db,
    'user': postgres_user,
    'password': postgres_password
}

def connect_to_database():
    while True:
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()
            return conn, cursor
        except psycopg2.OperationalError as e:
            print(f"Failed to connect to the database. Error: {e}")
            print("Retrying connection in 1 second...")
            time.sleep(1)

def insert_test_data():
    conn, cursor = connect_to_database()

    # Sample test data
    test_data = [
        (123.456, 789.012, 456.789, 123.456, '2023-11-06 12:00:00', '192.168.1.1'),
        (456.789, 123.456, 789.012, 123.456, '2023-11-06 14:00:00', '192.168.1.2'),
        # Add more test data as needed
    ]

    # SQL query to insert data into the 'rides' table
    insert_query = "INSERT INTO rides (lat_a, long_a, lat_b, long_b, search_date, ip) VALUES (%s, %s, %s, %s, %s, %s)"

    # Execute the query for each set of test data
    for data in test_data:
        cursor.execute(insert_query, data)

    # Commit the changes and end the transaction
    conn.commit()

    print("Test data successfully added to the 'rides' table.")

    cursor.close()
    conn.close()

def print_table_content(table_name, number):
    conn, cursor = connect_to_database()
    number = int(number)
    if number > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {number};")
    else:
        cursor.execute(f"SELECT * FROM {table_name};")

    rows = cursor.fetchall()
    if rows:
        html = f"<h3>Contents of the '{table_name}' table:</h3>"
        html += "<table>"
        # Headers
        html += "<tr>"
        for desc in cursor.description:
            html += f"<th>{desc.name}</th>"
        html += "</tr>"
        # Rows with data
        for row in rows:
            html += "<tr>"
            for value in row:
                html += f"<td>{value}</td>"
            html += "</tr>"
        html += "</table>"
    else:
        html = "No records in the table."
    cursor.close()
    conn.close()

    return html

def truncate_table(table_name):
    conn, cursor = connect_to_database()
    cursor.execute(f"TRUNCATE {table_name};")
    conn.commit()
    cursor.close()
    conn.close()

def recreate_table(table_name):
    conn, cursor = connect_to_database()
    cursor.execute(f"DROP TABLE {table_name};")
    conn.commit()
    path = "table_schema/"
    with open(path + table_name + '.sql', 'r') as file:
        sql_create = file.read()
        cursor.execute(sql_create)
        conn.commit()
    cursor.close()
    conn.close()

    return f"Table {table_name} created."

def table_schema(table_name):
    conn, cursor = connect_to_database()

    # Get the list of tables in the database
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [table[0] for table in cursor.fetchall()]

    # Check if the table with the given name exists
    if table_name not in tables:
        return f"Table '{table_name}' does not exist in the database."

    # Get the column structure for the given table
    cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
    columns = cursor.fetchall()

    # Build an HTML string with the table name, columns, and their types
    html = f"<h3>Schema of '{table_name}':</h3>"
    html += "<table>"
    html += "<tr><th>Column Name</th><th>Data Type</th></tr>"
    for column in columns:
        html += f"<tr><td>{column[0]}</td><td>{column[1]}</td></tr>"
    html += "</table>"

    cursor.close()
    conn.close()

    return html

def create_tables():
    try:
        conn, cursor = connect_to_database()
        path = "table_schema/"
        tables = os.listdir(path)
        print(tables)
        text = ""
        for table in tables:
            with open(path + table, 'r') as file:
                sql_create = file.read()
                
            cursor.execute(sql_create)
            conn.commit()
            print(f"Table {table.replace('.sql', '')} created.")
            text += f"Table {table.replace('.sql', '')} created.<br><br>"
        cursor.close()
        conn.close()
        return text
    except Exception as e:
        return e
