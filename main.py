import os
import unicodedata
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")

RESPUESTAS = {
    "horario": "La biblioteca está abierta de 7 a 23 hs de lunes a viernes y sábados 9 a 15 hs.",
    "sala": "La sala de lectura está abierta de 7 a 23 hs de lunes a viernes y sábados 9 a 15 hs.",
    "reserva": "Las reservas de libros para alumnos de grado se reservan por WhatsApp y en Referencia.",
    "programa": "Necesitás mandar a la Biblioteca referencias de materias aprobadas, tipo de trámite e información por email.",
    "usuario": "Necesitás Nombre, apellido, email @campus y un documento para registrarte.",
    "plataforma": "Necesitás Nombre, apellido, email @campus y un documento para registrarte.",
    "digital": "Necesitás Nombre, apellido, email @campus y un documento para registrarte.",
    "libre": "Necesitás mandar a la Biblioteca referencias de materias aprobadas, tipo de trámite e información por email.",
    "tad": "Necesitás mandar a la Biblioteca referencias de materias aprobadas, tipo de trámite e información por email.",
}

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def buscar_respuesta(user_text):
    user_text = normalizar(user_text)
    for clave, respuesta in RESPUESTAS.items():
        if clave in user_text:
            return respuesta
    return "Lo siento, no tengo información sobre eso. Podés preguntar sobre: horarios, sala, reservas, programas o usuario de plataforma."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    if not update.get("message") or not update["message"].get("text"):
        return jsonify({"ok": True})
    chat_id = update["message"]["chat"]["id"]
    user_text = update["message"]["text"]
    respuesta = buscar_respuesta(user_text)
    send_message(chat_id, respuesta)
    return jsonify({"ok": True})

@app.route("/")
def index():
    return "Bot activo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
