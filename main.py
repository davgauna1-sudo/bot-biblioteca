import os
import unicodedata
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN")
SHEET_ID_STATS = "1PNXqQydlsgggBBXFbCfulLBKheHs9sOh_VMTWkINmx0"

CREDS_DICT = {
    "type": "service_account",
    "project_id": "n8n-bot-490417",
    "private_key_id": "374e534551588e730c2e6f342db703687a41cde9",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCXEN75kpv4rq1p\nnxvjdFt4ZOrFl2QJaj3k29QXPFdwHthmCxbfXtHL0oDrq7Op0xEFk3VF+FM6S3sN\nreGBu6a9HlOuDn271YG5RJdFL0tmYVVb2cg8/y6dA5Tavcvsa5gN+pm4OZpkg/sh\nwjsAEdPMRKIYR+J6ulfRKwmTSDGNNUsoFm55f7+MuOLy9OXAr4ZECJsIm+QpeZT6\n8wQgn8wNptbaORV9Xo9awqT6PXjPPK/SjhSQ7N1oVA0gv5RTKJ7n1KhMS3HldKEK\nXWt/kvOQD7CNt2synC0o3/DQTgdHQWelZ/FJr4++p4OxuxTUpL11YHxZ/L2lFDkC\nhbeIlLXlAgMBAAECggEAKyBUX5BkuZ54gDY9mnYt5NV+lpEtLGjpqYu+ZTHDTo1n\nvt38liE2KId8aYtXm6xXaC2cJbEKZZKF2zZgMg61v7jIL+EQMQ73XUJBIy2oy14P\nJc0rForNLmMG3FmhvWlL+/Wma8r6EicBizYtbMwqGF8hnWfsNpg7GMo+Dg9mogZ8\nF/a2qsP8fXFLE58Zoln3FmGoAQA/6I2qv9Nt4794LaempLJYpFYtTyO3detpqir2\ngU193T+Ljyb5QE7++j41guNcSNu0jMFvL6yjVF1WPaU/WsW9a9s+gDDVeEo3LPhZ\nqOLJdo1qztS+Zkqi0P4OhlgEvzx0bWiskw1Ht6TLmpMc3xhN5euPZo5ecC4RJtfJrJu8\nTRlhlNld5pUGsSsHE1ZB/LqI9mKrnke4nBPsvlIStIwnK3+HCdi2RckGbXwJaX+f\nLPHI3Btl+/gnfPBgbRHH8XrDxKFYfl/2qp881y2cKB+eRybByndh+G/P/nY7JUei\nZpyGO5KARpRsFMA4GWBvGCbAowKBgQDC0/Zo1U6/yjmhVNvT9LsoBmjb6DFPiH/g\ngih6bP+RhP3gNMQrogD6bG0WdDPYfX5U+6LfpfRen1pMJi/zmY7zT+oCQRww4GSC\nRvH2EBYjwQL88D73jqY7c+f1ZR5xVKu7i9UyNSAfeQwxWUwILjCBN6YjjCY94D+d\nxKx1zlkv1wKBgDyWe9gFI5eEk96nuH3cYrbqXD7RNwPH6D5MpLOXlMhhjFSeB35O\nBbbpkNusyGrcWBy74K4iNu4DVSz6Sr4nVdXdeW9zrZdAB48nO5owFyzSQ/1i9Z+x\nDNHhTEax6JTDWw0j47S/xEFUhnofMvJbJ8PBQ0JsSLmEy/dTp5/BW3LJAoGAcK2E\nModDfzqm7/6TENfWskRauuxkMHpicub0IDIP8Qp4hgYeepm8dRjmUnksTwXtXZsX\nTL+/QEZrQ+VGEF38Rg4u6dTcSAxPNOVxJP2SwGTtpHoSALz4uSPEwLEV1TfCBrrN\nt7bv+CPbAGODzK8SjFSqSJ6DYAcBJrNGN76hEhcij5vtyJK5G819CvV7Fm/sVcra\niGGezcPy4w9YBUazKsdORigQDzgotR/Eftm6bZP0MmJyosJYCgw5B804OmzShb34\nGNow/jcH8m0esdGN3W6jyYpsV5uAd7PoYPtxA+BNFufEcPR/YgxeRbXAbGz8jJc9\nFiTaYAYl/VfgNqzeBmu2ws0=\n-----END PRIVATE KEY-----\n",
    "client_email": "bot-biblioteca@n8n-bot-490417.iam.gserviceaccount.com",
    "client_id": "109179526280123846959",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-biblioteca%40n8n-bot-490417.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

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

def registrar_estadistica(categoria):
    try:
        creds = Credentials.from_service_account_info(CREDS_DICT, scopes=[
            "https://www.googleapis.com/auth/spreadsheets"
        ])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID_STATS).sheet1
        ahora = datetime.now()
        fecha = ahora.strftime("%d/%m/%Y")
        hora = ahora.strftime("%H:%M")
        semana = ahora.strftime("%V")
        mes = ahora.strftime("%m/%Y")
        sheet.append_row([fecha, hora, semana, mes, categoria])
    except Exception as e:
        print(f"Error al registrar estadistica: {e}")

def buscar_respuesta(user_text):
    user_text = normalizar(user_text)
    for clave, respuesta in RESPUESTAS.items():
        if clave in user_text:
            registrar_estadistica(clave)
            return respuesta
    registrar_estadistica("otros")
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
