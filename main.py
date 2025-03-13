import smtplib
from flask import Flask, request, jsonify
from email.mime.text import MIMEText

app = Flask(__name__)

# 🔹 ДАННЫЕ ДЛЯ ТЕЛЕГРАМА
TELEGRAM_TOKEN = "7552421757:AAGgXf_YQ23TnoA8td1wiks9BorGNdXKrzM"
ADMIN_CHAT_ID = -1001234567890  # ID группы операторов (узнать через @userinfobot)

# 🔹 ДАННЫЕ ДЛЯ EMAIL
SMTP_SERVER = "smtp.gmail.com"  # Указать нужный SMTP-сервер
SMTP_PORT = 587
SMTP_LOGIN = "your_email@gmail.com"  # Твоя почта
SMTP_PASSWORD = "your_password"  # Пароль приложения (НЕ обычный пароль!)
JIVO_EMAIL = "support@jivo.com"  # Почта, куда слать в Jivo

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    """Обработка сообщений из Telegram и пересылка в Jivo через Email"""
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # 🔹 Отправляем в Jivo
        send_to_jivo_email(user_text)

        # 🔹 Оповещаем операторов в Telegram
        send_to_telegram_group(f"📨 Запрос клиента отправлен в Jivo:\n\n{user_text}")

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

def send_to_telegram_group(text):
    """Оповещение операторов в Telegram-группе"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)