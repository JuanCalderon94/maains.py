from flask import Flask, request, jsonify
from flask_cors import CORS
import pusher

app = Flask(_name_)
CORS(app)

pusher_client = pusher.Pusher(
  app_id = "2068346",
  key = "5398827de005ac67b6b2",
  secret = "342442a921382d60170b",
  cluster = "us2",
  ssl = True
)

@app.route('/', methods=['POST'])  # Cambiar a ruta raíz
def send_message():
    data = request.get_json()
    message = data.get('message')
    sender_id = data.get('senderId')
    channel = data.get('channel', 'my-channel')  # Agregar soporte para canal

    # Usar el mismo formato que el otro backend
    pusher_client.trigger(channel, 'my-event', {
        'message': message,
        'senderId': sender_id
    })
    
    return jsonify({'status': 'success'})

if _name_ == '_main_':
    app.run(debug=True)