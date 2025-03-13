from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Токен бота
TELEGRAM_TOKEN = "7552421757:AAGgXf_YQ23TnoA8td1wiks9BorGNdXKrzM"
@app.route('/jivo_webhook', methods=['POST'])
def jivo_webhook():
    """Обработка вебхуков от Jivo"""
    data = request.json
    print(f"📥 Вебхук от Jivo: {data}")

    event = data.get("event_name", "")
    message = data.get("data", {}).get("message", "Сообщение отсутствует")
    client_name = data.get("data", {}).get("visitor", {}).get("name", "Неизвестный пользователь")

    if event == "chat_message":
        text = f"💬 **Новое сообщение в Jivo**\n👤 От: {client_name}\n📩 Сообщение: {message}"
        send_to_telegram(text)

    elif event == "chat_accepted":
        operator = data.get("data", {}).get("agent", {}).get("name", "Оператор")
        text = f"✅ **Оператор {operator} принял чат**"
        send_to_telegram(text)

    return jsonify({"status": "ok"})

def send_to_telegram(text):
    """Отправка сообщений в Telegram-группу операторов"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": OPERATOR_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print(f"📤 Отправлено в Telegram: {response.status_code}, {response.text}")

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
