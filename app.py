from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

@app.route('/')
def home():
    return "🤖 UAE Property Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    
    if update.get('message'):
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        
        if text == '/start':
            send_message(chat_id, '🏠 Привет! UAE Property Navigator работает!')
        else:
            send_message(chat_id, f'Получил: {text}')
    
    return jsonify({'status': 'ok'})

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': text})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
