from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL для имитации запроса в Jivo (имитируем обычный браузерный POST-запрос)
JIVO_URL = "https://www.jivo.ru/chat_api"  # Используй реальный URL из браузера

@app.route('/proxy', methods=['POST'])
def proxy_to_jivo():
    try:
        data = request.json  # Получаем данные от Telegram-бота
        user_message = data.get("message", "Без сообщения")  # Получаем текст

        # Эмулируем запрос, как если бы он отправлялся из браузера
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",  # Маскируем запрос под браузер
            "Content-Type": "application/json"
        }

        payload = {
            "event_name": "chat_accepted",
            "data": {
                "visitor": {
                    "name": f"Telegram User",
                    "phone": "N/A",
                    "email": "N/A"
                },
                "message": user_message
            }
        }

        response = requests.post(JIVO_URL, json=payload, headers=headers)

        return jsonify({
            "status": response.status_code,
            "response": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)