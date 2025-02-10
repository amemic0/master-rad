import psycopg2
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TrafficControl (
                intersection_id INTEGER,
                event_time TIMESTAMP,
                north_side INTEGER, 
                south_side INTEGER, 
                east_side INTEGER, 
                west_side INTEGER
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Inicijalizacija baze uspješna: TrafficControl tabela kreirana.")
    except Exception as e:
        print(f"Greška prilikom inicijalizacije baze: {e}")


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

        north_side = result.get("north_side", 0)
        south_side = result.get("south_side", 0)
        east_side = result.get("east_side", 0)
        west_side = result.get("west_side", 0)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO TrafficControl (intersection_id, event_time, north_side, south_side, east_side, west_side)
            VALUES (%s, NOW(), %s, %s, %s, %s)
        ''', (intersection_id, north_side, south_side, east_side, west_side))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Podaci su uspješno smješteni u tabelu TrafficControl"}), 200
    except Exception as e:
        return jsonify({"error": "Neuspješno smještanje podataka u bazu", "detalji": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server radi"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
