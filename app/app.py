from flask import Flask, render_template, request, flash, redirect, url_for
from modules.OSM import route_search
from modules.db import *

app = Flask(__name__, template_folder='templates/')
app.debug = True

app.secret_key = 'moj3R3j3strow3K1ocejh3439Tik^$!skxUIP3mOJen'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_tables')
def tables_create():
    text = create_tables()
    return render_template('create_tables.html', text=text)

@app.route('/ip')
def get_client_ip():
    client_ip = request.remote_addr
    return f'Adres IP klienta: {client_ip}'

@app.route('/table_schema/<table_name>', methods=['GET', 'POST'])
def tables_schema(table_name):
    records = ""
    text = table_schema(table_name)

    if request.method == 'POST':
        if 'show_all' in request.form:
            records = print_table_content(table_name, 0)  # Zaimplementuj funkcję get_all_records
        elif 'show_x' in request.form:
            count = request.form['count']
            if count == "":
                error_message = '<div class="alert alert-danger"><h5 class="text-center">Podaj liczbe rekordów do wyśwetlenia!</h5></div>'
                return render_template('table_schema.html', table_name=table_name, text=text, records=str(error_message + records))

            records = print_table_content(table_name, count)  # Zaimplementuj funkcję get_x_records
        elif 'delete_all' in request.form:
            truncate_table(table_name)  # Funkcja do usuwania danych (zaimplementuj ją)

            # Dodałem komunikat potwierdzający usunięcie danych
            flash(f'Usunięto wszystkie dane z tabeli "{table_name}"', 'success')

            # Przekierowanie z powrotem na stronę z potwierdzeniem usunięcia
            return redirect(url_for('tables_schema', table_name=table_name))
        
        elif 'recreate_table' in request.form:
            records = recreate_table(table_name)  # Funkcja do usuwania danych (zaimplementuj ją)

            # Dodałem komunikat potwierdzający usunięcie danych
            flash(f'Usunięto i stworzono pustą tabele "{table_name}"', 'success')

            return render_template('table_schema.html', table_name=table_name, text=text, records=records)


    return render_template('table_schema.html', table_name=table_name, text=text, records=records)


@app.route('/search')
def search():
    start_location = request.args.get('startLocation')
    end_location = request.args.get('endLocation')
    departure_time = request.args.get('departureTime')
    client_ip = request.remote_addr


    # Przetwórz dane, np. wyznacz trasę z wykorzystaniem podanych informacji
    route_search(start_location, end_location, date=departure_time, ip=client_ip, path='routes/route_map.html')
    # Przygotuj wyniki    
    with open('routes/route_map.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0')
