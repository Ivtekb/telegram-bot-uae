from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
BOT_TOKEN = "8074002738:AAGNAAHE9sdUDRl7EVwLGYYPrnZK48cxBf4"

# Хранение данных пользователей (временно в памяти)
user_sessions = {}

@app.route('/')
def home():
    return "🤖 UAE Property Bot (@ivandubai_signal_bot) Stage 2 - Language & Roles"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.json
        
        if update and update.get('message'):
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            first_name = update['message']['from'].get('first_name', 'друг')
            
            # Получить или создать сессию пользователя
            if chat_id not in user_sessions:
                user_sessions[chat_id] = {'stage': 'start', 'data': {'name': first_name}}
            
            session = user_sessions[chat_id]
            
            # Маршрутизация сообщений
            if text == '/start':
                handle_start(chat_id)
            elif session['stage'] == 'language_select':
                handle_language_selection(chat_id, text, session)
            elif session['stage'] == 'role_select':
                handle_role_selection(chat_id, text, session)
            else:
                send_message(chat_id, "Используйте /start для начала работы с ботом")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error'})

def handle_start(chat_id):
    """Начало работы - выбор языка"""
    user_sessions[chat_id] = {'stage': 'language_select', 'data': {}}
    
    keyboard = {
        'keyboard': [
            ['Русский', 'English']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    text = "🏠 <b>UAE Property Navigator</b>\n\nВыберите язык / Choose language:"
    send_message(chat_id, text, keyboard, parse_mode='HTML')

def handle_language_selection(chat_id, text, session):
    """Обработка выбора языка"""
    if 'Русский' in text:
        session['data']['language'] = 'ru'
        session['stage'] = 'role_select'
        
        keyboard = {
            'keyboard': [
                ['🏠 Жить', '📈 Инвестировать'],
                ['🔄 Продать/Сдать', '🎯 Смешанный']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        name = session['data'].get('name', 'друг')
        text_msg = f"Привет, {name}. Иван, цифровой напарник в эфире.\n\nХочу услышать твой текущий фокус: жить, инвестировать, управлять активом?"
        
        send_message(chat_id, text_msg, keyboard)
        
    elif 'English' in text:
        session['data']['language'] = 'en'
        session['stage'] = 'role_select'
        
        keyboard = {
            'keyboard': [
                ['🏠 Live', '📈 Invest'],
                ['🔄 Sell/Rent', '🎯 Mixed']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        name = session['data'].get('name', 'friend')
        text_msg = f"Hi, {name}. Ivan, digital partner online.\n\nWhat's your current focus: live, invest, manage property?"
        
        send_message(chat_id, text_msg, keyboard)
    else:
        send_message(chat_id, "Пожалуйста, выберите язык из предложенных вариантов")

def handle_role_selection(chat_id, text, session):
    """Обработка выбора роли"""
    lang = session['data'].get('language', 'ru')
    
    # Определяем роль
    if text in ['🏠 Жить', '🏠 Live']:
        session['data']['role'] = 'live'
        role_name = 'Жить' if lang == 'ru' else 'Live'
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
        role_name = 'Инвестировать' if lang == 'ru' else 'Invest'
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'owner'
        role_name = 'Продать/Сдать' if lang == 'ru' else 'Sell/Rent'
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
        role_name = 'Смешанный' if lang == 'ru' else 'Mixed'
    else:
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)
        return
    
    # Подтверждение выбора и временное завершение
    if lang == 'ru':
        msg = f"✅ <b>Профиль создан!</b>\n\n"
        msg += f"🗣 Язык: Русский\n"
        msg += f"🎯 Фокус: {role_name}\n\n"
        msg += f"📊 <b>Этап 2 завершен!</b>\n"
        msg += f"Следующие этапы: бюджет, приоритеты, локации, контакты.\n\n"
        msg += f"🔄 Нажмите /start для нового теста"
    else:
        msg = f"✅ <b>Profile created!</b>\n\n"
        msg += f"🗣 Language: English\n"
        msg += f"🎯 Focus: {role_name}\n\n"
        msg += f"📊 <b>Stage 2 completed!</b>\n"
        msg += f"Next stages: budget, priorities, locations, contacts.\n\n"
        msg += f"🔄 Press /start for new test"
    
    keyboard = {
        'keyboard': [
            ['/start']
        ],
        'resize_keyboard': True
    }
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')
    
    # Логируем для отладки
    print(f"Stage 2 completed for user {chat_id}: {session['data']}")

def send_message(chat_id, text, keyboard=None, parse_mode=None):
    """Отправка сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    
    if keyboard:
        payload['reply_markup'] = keyboard
    
    if parse_mode:
        payload['parse_mode'] = parse_mode
    
    try:
        response = requests.post(url, json=payload)
        print(f"Message sent to {chat_id}: {text[:50]}...")
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
