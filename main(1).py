from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pusher

app = Flask(__name__)
CORS(app)

# 🔹 Conexión a la base de datos de AlwaysData
# Reemplaza los datos con los de tu cuenta en AlwaysData
DB_HOST = "mysql-juancalderon.alwaysdata.net"   # Dominio del servidor MySQL de AlwaysData
DB_USER = "436156_juan"                        # Tu usuario de base de datos
DB_PASSWORD = "juanito600"              # <-- pon aquí tu contraseña real
DB_NAME = "juancalderon_new_base"               # Nombre exacto de la base de datos

# Crear conexión
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print("❌ Error de conexión a la base de datos:", e)
        return None

# 🔹 Configuración de Pusher (usa tus claves correctas)
pusher_client = pusher.Pusher(
  app_id = "2068346",
  key = "5398827de005ac67b6b2",
  secret = "342442a921382d60170b",
  cluster = "us2",
  ssl = True
)

@app.route("/", methods=["POST"])
def handle_message():
    data = request.get_json()
    message = data.get("message")
    sender_id = data.get("senderId")
    channel = data.get("channel")

    # Guardar el mensaje en la base de datos
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO mensajes (sender_id, mensaje, canal) VALUES (%s, %s, %s)"
                cursor.execute(sql, (sender_id, message, channel))
                conn.commit()
        except Exception as e:
            print("❌ Error al guardar mensaje:", e)
        finally:
            conn.close()

    # Enviar mensaje al canal Pusher
    pusher_client.trigger(channel, "my-event", {
        "message": message,
        "senderId": sender_id
    })

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
