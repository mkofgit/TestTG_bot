import os
import smtplib
import requests
from flask import Flask, request, jsonify
from email.mime.text import MIMEText

# 🔹 Принудительно задаем переменные окружения
os.environ["TELEGRAM_TOKEN"] = "7552421757:AAGgXf_YQ23TnoA8td1wiks9BorGNdXKrzM"
os.environ["SMTP_PASSWORD"] = "hhdgbymlgtocqcsy"

# 🔹 Загружаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# 🔹 Выводим значения для проверки
print(f"Загруженный Telegram Token: {TELEGRAM_TOKEN}")
print(f"Загруженный SMTP Password: {SMTP_PASSWORD}")

app = Flask(__name__)

# 🔹 ДАННЫЕ ДЛЯ ТЕЛЕГРАМА
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Хранить в переменных окружения!

# 🔹 ДАННЫЕ ДЛЯ EMAIL (Хранить в Railway Variables)
SMTP_SERVER = "smtp.mail.ru"  # Используем Mail.ru
SMTP_PORT = 587
SMTP_LOGIN = "unityspace2024@mail.ru"  # Твоя почта
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Пароль приложения
JIVO_EMAIL = "idmurgpsfrtnjivosite@jivo-mail.com"  # Email-канал Jivo

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    """Обработка сообщений из Telegram и пересылка в Jivo через Email"""
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # 🔹 Отправляем в Jivo
        send_to_jivo_email(user_text)

    return jsonify({"status": "ok"})

def send_to_jivo_email(user_message):
    """Отправка сообщения в Jivo через Email"""
    msg = MIMEText(f"🔔 Новый клиентский запрос:\n\n{user_message}")
    msg["Subject"] = "🔹 Новый запрос из Telegram"
    msg["From"] = SMTP_LOGIN
    msg["To"] = JIVO_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_LOGIN, SMTP_PASSWORD)
            server.sendmail(SMTP_LOGIN, JIVO_EMAIL, msg.as_string())
        print("✅ Email отправлен в Jivo")
    except Exception as e:
        print(f"🚨 Ошибка отправки Email: {str(e)}")

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)