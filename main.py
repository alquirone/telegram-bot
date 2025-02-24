import os
os.system("pip install pyTelegramBotAPI")
import telebot
import time
from flask import Flask, request

# Cargar el token de entorno (Railway lo manejará como variable de entorno)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Debe ser tu URL en Railway (HTTPS obligatorio)
bot = telebot.TeleBot(TOKEN)

# Diccionario para control de rate limiting
user_rate_limit = {}

# Configurar Flask para Webhooks
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Bot funcionando correctamente", 200

# Configurar Webhook en Railway
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# 📌 Bloquear el bot en grupos públicos
@bot.message_handler(func=lambda message: message.chat.type != "private")
def block_public_groups(message):
    bot.reply_to(message, "🚫 Este bot solo funciona en mensajes privados.")

# 📌 Protección contra SPAM (Rate Limiting)
@bot.message_handler(func=lambda message: True)
def rate_limit(message):
    user_id = message.chat.id
    current_time = time.time()

    if user_id in user_rate_limit and (current_time - user_rate_limit[user_id]) < 2:  # 2 segundos de cooldown
        bot.reply_to(message, "⚠️ ¡No envíes mensajes tan rápido!")
    else:
        user_rate_limit[user_id] = current_time
        bot.reply_to(message, f"Mensaje recibido: {message.text}")

# 📌 Protección contra comandos maliciosos
@bot.message_handler(func=lambda message: message.text.startswith("/"))
def block_commands(message):
    bot.reply_to(message, "⚠️ Los comandos no están permitidos en este bot.")

# Ejecutar en Railway
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
