from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7552421757:AAGgXf_YQ23TnoA8td1wiks9BorGNdXKrzM"
JIVO_API_URL = "https://api.jivosite.com/integration/webhooks"

# Частые вопросы и автоответы
FAQ = {
    "цены": "Вы можете ознакомиться с тарифами на нашем сайте: https://example.com/pricing",
    "функционал": "Вот список возможностей нашего сервиса: https://example.com/features",
    "поддержка": "Свяжитесь с нашей поддержкой через кнопку 'Связаться с оператором'."
}

# Главная функция обработки сообщений от Telegram
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()
        
        if text == "/start":
            send_welcome_message(chat_id)
            return jsonify({"status": "ok"})
        
        # Если вопрос есть в FAQ, отправляем автоответ
        for keyword, answer in FAQ.items():
            if keyword in text:
                send_message(chat_id, answer)
                return jsonify({"status": "ok"})
        
        # Если не нашли автоответ, предлагаем обратиться к оператору
        send_operator_button(chat_id)
    
    # Обработка нажатия кнопки "Связаться с оператором"
    elif "callback_query" in data:
        if data["callback_query"]["data"] == "ask_jivo":
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            user_message = data["callback_query"]["message"]["text"]
            send_to_jivo(user_message)
            send_message(chat_id, "Ваш запрос отправлен оператору. Ожидайте ответа!")
    
    return jsonify({"status": "ok"})

# Функция отправки приветственного сообщения с кнопками
def send_welcome_message(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Добро пожаловать! Выберите действие:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Частые вопросы", "callback_data": "faq"}],
                [{"text": "Связаться с оператором", "callback_data": "ask_jivo"}]
            ]
        }
    }
    requests.post(url, json=payload)

# Функция отправки сообщений в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Функция отправки кнопки "Связаться с оператором"
def send_operator_button(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Не нашли ответ? Свяжитесь с оператором.",
        "reply_markup": {
            "inline_keyboard": [[{"text": "Связаться с оператором", "callback_data": "ask_jivo"}]]
        }
    }
    requests.post(url, json=payload)

# Функция отправки сообщений в Jivo
def send_to_jivo(message):
    payload = {"text": message}
    requests.post(JIVO_API_URL, json=payload)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

