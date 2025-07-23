from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
BOT_TOKEN = "8074002738:AAGNAAHE9sdUDRl7EVwLGYYPrnZK48cxBf4"

@app.route('/')
def home():
    return "🤖 UAE Property Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.json
        if update and update.get('message'):
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text == '/start':
                send_message(chat_id, 'Привет! Бот работает! Полная версия скоро вернется.')
            else:
                send_message(chat_id, f'Получил: {text}')
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error'})

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
