from flask import Flask, request, jsonify
import psycopg2
import requests

app = Flask(__name__)

SERVER2_URL = "http://server2-service:8080/data"
SERVER1_URL = "http://server-service:8080/data"

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

@app.route('/data', methods=['POST'])
def forward_request():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Zahtjev ne sadrži podatke"}), 400

        param_type = data.get("param_type")
        forw_is = data.get("forwarding_action")

        if not param_type:
            return jsonify({"error": "Polje 'param_type' nedostaje"}), 400

        if forw_is == 'Y':

            if param_type == "weather":
                target_url = SERVER2_URL
            elif param_type == "traffic":
                target_url = SERVER1_URL
            else:
                return jsonify({"error": f"Nepoznata vrijednost 'param_type': {param_type}"}), 400

            response = requests.post(target_url, json=data)
        
        else:

            if param_type == "weather":

                result = data.get("Result")

                if not result:
                    return jsonify({"error": "Polje 'Result' nedostaje"}), 400

                intersection_id = data.get("intersection_id")
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
            
            if param_type == "traffic": 

                result = data.get("Result")
                if not result:
                    return jsonify({"error": "Polje 'Result' nedostaje"}), 400
                intersection_id = data.get("intersection_id")
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

    except Exception as e:
        return jsonify({"error": "Došlo je do greške prilikom prosljeđivanja zahtjeva", "details": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server3 radi"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
