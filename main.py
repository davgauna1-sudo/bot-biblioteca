import os
import unicodedata
import requests
import json
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def get_sheet_data():
   creds_json = os.environ.get("GOOGLE_CREDS")

   creds_dict = json.loads(creds_json)
    creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet.get_all_values()

def buscar_respuesta(user_text, data):
    user_text = normalizar(user_text)
    mejor_respuesta = "Lo siento, no tengo información sobre eso. Podés preguntar sobre: horarios, sala, reservas, programas o usuario de plataformas."
    mejor_puntaje = 0

    for i in range(1, len(data)):
        if len(data[i]) < 3:
            continue
        keywords = normalizar(data[i][2])
        lista = [k.strip() for k in keywords.split(",") if k.strip()]
        puntaje = sum(1 for k in lista if k and k in user_text)
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejor_respuesta = data[i][1]

    return mejor_respuesta

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
    
    data = get_sheet_data()
    respuesta = buscar_respuesta(user_text, data)
    send_message(chat_id, respuesta)
    
    return jsonify({"ok": True})

@app.route("/")
def index():
    return "Bot activo"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
