from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
print(f"Bot token loaded: {BOT_TOKEN[:10]}..." if BOT_TOKEN else "No token!")

@app.route('/')
def home():
    return "🤖 UAE Property Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("=" * 50)
    print("WEBHOOK RECEIVED!")
    print("=" * 50)
    
    try:
        update = request.json
        print(f"Full update: {update}")
        
        if update and update.get('message'):
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            print(f"Chat ID: {chat_id}")
            print(f"Message: {text}")
            
            if text == '/start':
                result = send_message(chat_id, '🏠 Привет! UAE Property Navigator работает!')
                print(f"Send result: {result}")
            else:
                result = send_message(chat_id, f'Получил: {text}')
                print(f"Send result: {result}")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"ERROR in webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def send_message(chat_id, text):
    if not BOT_TOKEN:
        print("No bot token available!")
        return None
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    
    try:
        print(f"Sending to: {url}")
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
