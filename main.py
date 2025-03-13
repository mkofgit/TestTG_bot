import smtplib
import os
from flask import Flask, request, jsonify
from email.mime.text import MIMEText

app = Flask(__name__)

# 🔹 ДАННЫЕ ДЛЯ EMAIL (Хранить в Railway Variables)
SMTP_SERVER = "smtp.mail.ru"  
SMTP_PORT = 587
SMTP_LOGIN = "unityspace2024@mail.ru"  
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Пароль приложения
JIVO_EMAIL = "idmurgpsfrtnjivosite@jivo-mail.com"  

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    """Обработка сообщений из Telegram и пересылка в Jivo через Email"""
    data = request.json

    if "message" in data:
        user_text = data["message"].get("text", "")

        # 🔹 Отправляем в Jivo
        send_to_jivo_email(user_text)

    return jsonify({"status": "ok"})

def send_to_jivo_email(user_message):
    """Отправка сообщения в Jivo через Email"""
    subject = "🔔 Новый клиентский запрос в Jivo"
    email_body = f"📩 Новое сообщение от клиента:\n\n{user_message}"

    msg = MIMEText(email_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_LOGIN
    msg["To"] = JIVO_EMAIL
    msg["Reply-To"] = SMTP_LOGIN  # Добавляем, чтобы Jivo не игнорировал

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_LOGIN, SMTP_PASSWORD)

            # 🔹 Логируем отправленное сообщение
            print("🔹 Отправляем Email в Jivo...")
            print(msg.as_string())

            server.sendmail(SMTP_LOGIN, JIVO_EMAIL, msg.as_string())
        print("✅ Email успешно отправлен в Jivo!")
    except Exception as e:
        print(f"🚨 Ошибка при отправке Email: {str(e)}")

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)