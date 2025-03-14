import os
import smtplib
import telebot
from email.mime.text import MIMEText
from flask import Flask, request

# 🔹 Telegram Bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🔹 Email (Mail.ru)
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 587
SMTP_LOGIN = "unityspace2024@mail.ru"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
JIVO_EMAIL = "idmurgpsfrtnjivosite@jivo-mail.com"

# 🔹 Flask-сервер для Webhook
app = Flask(__name__)

# Храним пользователей, которые начали писать вопрос
user_states = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    """Приветствие"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton("✉ Написать в поддержку")
    keyboard.add(button_support)
    bot.send_message(message.chat.id, "Привет! Чем могу помочь?", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "✉ Написать в поддержку")
def ask_question(message):
    """Пользователь нажал кнопку 'Написать в поддержку'"""
    bot.send_message(message.chat.id, "✍ Напишите ваш вопрос:")
    user_states[message.chat.id] = "waiting_for_question"

@bot.message_handler(func=lambda message: message.chat.id in user_states)
def receive_question(message):
    """Получаем вопрос пользователя и отправляем его в Jivo"""
    user_text = message.text

    # Удаляем пользователя из списка ожидания
    del user_states[message.chat.id]

    # Отправляем сообщение на почту
    send_to_jivo_email(user_text)

    bot.send_message(message.chat.id, "✅ Ваш вопрос отправлен в поддержку!")

def send_to_jivo_email(user_message):
    """Отправка сообщения в Jivo через Email"""
    msg = MIMEText(user_message)
    msg["Subject"] = "🔹 Новый запрос из Telegram"
    msg["From"] = SMTP_LOGIN
    msg["To"] = JIVO_EMAIL
    msg["Reply-To"] = SMTP_LOGIN  # Это важно!

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_LOGIN, SMTP_PASSWORD)
            server.sendmail(SMTP_LOGIN, JIVO_EMAIL, msg.as_string())
        print("✅ Email отправлен в Jivo")
    except Exception as e:
        print(f"🚨 Ошибка отправки Email: {str(e)}")

@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    """Обработка входящих сообщений Telegram"""
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)