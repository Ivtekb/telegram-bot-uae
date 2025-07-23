from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Используем токен от @ivandubai_signal_bot
BOT_TOKEN = "8074002738:AAGNAAHE9sdUDRl7EVwLGYYPrnZK48cxBf4"

print("=" * 50)
print(f"CURRENT BOT TOKEN: {BOT_TOKEN}")
print("Signal bot token loaded successfully!")
print("=" * 50)

@app.route('/')
def home():
    return f"🤖 UAE Property Bot (@ivandubai_signal_bot) is running! Token: {BOT_TOKEN[:15]}..."

@app.route('/webhook', methods=['POST'])
def webhook():
    print("=" * 50)
    print("WEBHOOK RECEIVED!")
    print(f"Using @ivandubai_signal_bot token: {BOT_TOKEN[:20]}...")
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
                result = send_message(chat_id, '🏠 Привет! UAE Property Navigator (@ivandubai_signal_bot) работает!')
                print(f"Send result: {result}")
            else:
                result = send_message(chat_id, f'Получил: {text}')
                print(f"Send result: {result}")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"ERROR in webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

def send_message(chat_id, text):
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
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
