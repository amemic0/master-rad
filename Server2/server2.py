import psycopg2
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DB_HOST = os.getenv('POSTGRES_HOST', 'baza-podataka-service')
DB_NAME = os.getenv('POSTGRES_DB', 'mydatabase')
DB_USER = os.getenv('POSTGRES_USER', 'admin')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'adminpassword')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.commit()
        cursor.close()
        conn.close()
        print("Inicijalizacija baze uspješna: weatherparams tabela kreirana.")
    except Exception as e:
        print(f"Greška prilikom inicijalizacije tabele WeatherParams: {e}")


@app.route('/data', methods=['POST'])
def save_post_data():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Zahtjev je prazan"}), 400


        intersection_id = data.get("intersection_id")
        if intersection_id is None:
            return jsonify({"error": "Polje 'intersection_id' nedostaje"}), 400


        result = data.get("Result")
        if not result:
            return jsonify({"error": "Polje 'Result' nedostaje"}), 400

        temperature_c = result.get("temperature_c", 0)
        air_pressure_kPa = result.get("air_pressure_kPa", 0)
        humidity_percent = result.get("humidity_percent", 0)
        visibility_meters = result.get("visibility_meters", 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weatherparams (intersection_id, event_time, temperature_c, air_pressure_kPa, humidity_percent, visibility_meters)
            VALUES (%s, NOW(), %s, %s, %s, %s)
        ''', (intersection_id, temperature_c, air_pressure_kPa, humidity_percent, visibility_meters))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Podaci su uspješno smješteni u tabelu weatherparams"}), 200
    except Exception as e:
        return jsonify({"error": "Neuspješno smještanje podataka u bazu", "detalji": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server radi"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
