from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

TELEGRAM_TOKEN = "7552421757:AAGgXf_YQ23TnoA8td1wiks9BorGNdXKrzM"
JIVO_API_URL = "https://api.jivosite.com/webhooks"
PROXY_SERVER_URL = "https://testtgbot-production.up.railway.app/proxy"  # Замените на свой URL

# Частые вопросы и автоответы
FAQ = {
    "цены": "Вы можете ознакомиться с тарифами на нашем сайте: https://example.com/pricing",
    "функционал": "Вот список возможностей нашего сервиса: https://example.com/features",
    "поддержка": "Свяжитесь с нашей поддержкой через кнопку 'Связаться с оператором'."
}

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()
        
        if text == "/start":
            send_welcome_message(chat_id)
            return jsonify({"status": "ok"})
        
        for keyword, answer in FAQ.items():
            if keyword in text:
                send_message(chat_id, answer)
                return jsonify({"status": "ok"})
        
        send_operator_button(chat_id)
    
    elif "callback_query" in data:
        if data["callback_query"]["data"] == "ask_jivo":
            chat_id = data["callback_query"]["message"]["chat"]["id"]
            user_message = data["callback_query"]["message"].get("text", "Сообщение отсутствует")
            send_to_jivo_proxy(chat_id, user_message)
            send_message(chat_id, "Ваш запрос отправлен оператору. Ожидайте ответа!")
    
    return jsonify({"status": "ok"})

@app.route('/proxy', methods=['POST'])
def proxy_to_jivo():
    try:
        data = request.json
        print(f"📥 Получен запрос: {data}")

        user_message = data.get("message", "Без сообщения")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/json"
        }

        payload = {
            "event_name": "chat_accepted",
            "data": {
                "visitor": {
                    "name": "Telegram User",
                    "phone": "N/A",
                    "email": "N/A"
                },
                "message": user_message
            }
        }

        response = requests.post(JIVO_API_URL, json=payload, headers=headers, timeout=5)
        print(f"✅ Отправлено в Jivo: {payload}")
        print(f"🔄 Ответ Jivo: {response.status_code}, {response.text}")

        return jsonify({"status": response.status_code, "response": response.text})

    except requests.Timeout:
        print("⏳ Ошибка: Превышено время ожидания ответа от Jivo")
        return jsonify({"error": "Превышено время ожидания ответа от Jivo"}), 504
    except Exception as e:
        print(f"🚨 Ошибка в прокси: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Функция отправки сообщений в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

# Функция отправки кнопки "Связаться с оператором"
def send_operator_button(chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "Не нашли ответ? Свяжитесь с оператором.",
        "reply_markup": {
            "inline_keyboard": [[{"text": "📞 Связаться с оператором", "callback_data": "ask_jivo"}]]
        }
    }
    requests.post(url, json=payload)

# Функция отправки запроса в прокси-сервер для Jivo
def send_to_jivo_proxy(user_id, message):
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(PROXY_SERVER_URL, json=payload, headers=headers, timeout=5)
        response_data = response.json() if response.status_code == 200 else response.text
        print(f"✅ Отправлено в прокси: {json.dumps(payload, ensure_ascii=False)}")
        print(f"🔄 Ответ прокси: {response.status_code}, {response_data}")
    except requests.Timeout:
        print("⏳ Ошибка: Превышено время ожидания ответа от прокси")
    except requests.RequestException as e:
        print(f"🚨 Ошибка отправки в прокси: {str(e)}")

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
