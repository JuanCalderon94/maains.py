from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pusher

app = Flask(__name__)
CORS(app)

# 📦 Datos de AlwaysData
DB_HOST = "mysql-juancalderon.alwaysdata.net"
DB_USER = "436156_juan"
DB_PASSWORD = "juanito600"
DB_NAME = "juancalderon_new_base"

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print("❌ Error de conexión a la base de datos:", e)
        return None

# 🔔 Configuración de Pusher (us2)
pusher_client = pusher.Pusher(
    app_id="2068346",
    key="5398827de005ac67b6b2",
    secret="342442a921382d60170b",
    cluster="us2",
    ssl=True
)

# ✅ Ruta principal — recibir mensaje y reenviar
@app.route("/", methods=["POST"])
def handle_message():
    data = request.get_json()
    message = data.get("message")
    sender_id = data.get("senderId")
    channel = data.get("channel")

    # Guardar mensaje en la base de datos
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO mensajes (sender_id, mensaje, canal) VALUES (%s, %s, %s)"
                cursor.execute(sql, (sender_id, message, channel))
                conn.commit()
                print(f"✅ Mensaje guardado: {message}")
        except Exception as e:
            print("❌ Error al guardar mensaje:", e)
        finally:
            conn.close()

    # Enviar mensaje al canal Pusher
    try:
        pusher_client.trigger(channel, "my-event", {
            "message": message,
            "senderId": sender_id
        })
        print(f"📡 Mensaje enviado a canal {channel}")
    except Exception as e:
        print("❌ Error al enviar mensaje a Pusher:", e)

    return jsonify({"status": "ok"})

# ✅ Nueva ruta para ver historial (opcional)
@app.route("/mensajes", methods=["GET"])
def get_messages():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mensajes ORDER BY fecha DESC LIMIT 20")
            data = cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        print("❌ Error al obtener mensajes:", e)
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

