from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Токен бота
BOT_TOKEN = "8074002738:AAGNAAHE9sdUDRl7EVwLGYYPrnZK48cxBf4"

# Хранение данных пользователей (временно в памяти)
user_sessions = {}

@app.route('/')
def home():
    return "🤖 UAE Property Bot (@ivandubai_signal_bot) is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.json
        
        if update and update.get('message'):
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            first_name = update['message']['from'].get('first_name', 'друг')
            
            # Получить сессию пользователя
            if chat_id not in user_sessions:
                user_sessions[chat_id] = {'stage': 'start', 'data': {'name': first_name}}
            
            session = user_sessions[chat_id]
            
            # Обработка команды /start
            if text == '/start':
                handle_start(chat_id)
            # Выбор языка
            elif session['stage'] == 'language_select':
                handle_language_selection(chat_id, text, session)
            # Определение роли
            elif session['stage'] == 'role_select':
                handle_role_selection(chat_id, text, session)
            # Ввод бюджета
            elif session['stage'] == 'budget_input':
                handle_budget_input(chat_id, text, session)
            # Выбор приоритетов
            elif session['stage'] == 'priority_select':
                handle_priority_selection(chat_id, text, session)
            # Показ локаций
            elif session['stage'] == 'show_locations':
                handle_location_selection(chat_id, text, session)
            # Обработка других сообщений
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
            ['🇷🇺 Русский', '🇬🇧 English']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    send_message(chat_id, "🏠 Выберите язык / Choose language:", keyboard)

def handle_language_selection(chat_id, text, session):
    """Обработка выбора языка"""
    if '🇷🇺' in text or 'Русский' in text:
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
        text_msg = f"Привет, {name}. Иван. Цифровой напарник в эфире.\n\nХочу услышать твой текущий фокус: жить, инвестировать, управлять активом?"
        
        send_message(chat_id, text_msg, keyboard)
        
    elif '🇬🇧' in text or 'English' in text:
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
        text_msg = f"Hi, {name}. Ivan. Digital partner online.\n\nWhat's your current focus: live, invest, manage property?"
        
        send_message(chat_id, text_msg, keyboard)
    else:
        send_message(chat_id, "Пожалуйста, выберите язык из предложенных вариантов")

def handle_role_selection(chat_id, text, session):
    """Обработка выбора роли"""
    lang = session['data'].get('language', 'ru')
    
    # Определяем роль
    if text in ['🏠 Жить', '🏠 Live']:
        session['data']['role'] = 'live'
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'sell'
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
    else:
        # Если неверный выбор
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)
        return
    
    # Переход к вводу бюджета
    session['stage'] = 'budget_input'
    
    if lang == 'ru':
        msg = "Отлично! Каков ориентир по бюджету?\n\n💰 Например: 2-3M AED, 1.5M AED, 5M+ AED"
    else:
        msg = "Great! What's your budget range?\n\n💰 For example: 2-3M AED, 1.5M AED, 5M+ AED"
    
    send_message(chat_id, msg)

def handle_budget_input(chat_id, text, session):
    """Обработка ввода бюджета"""
    lang = session['data'].get('language', 'ru')
    session['data']['budget'] = text
    session['stage'] = 'priority_select'
    
    keyboard = {
        'keyboard': [
            ['🌊 Утро у воды', '🏙️ Доступ к центру'] if lang == 'ru' else ['🌊 Water morning', '🏙️ City access'],
            ['⚖️ Баланс'] if lang == 'ru' else ['⚖️ Balance']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = f"Бюджет {text} принят!\n\n🤔 Что важнее: утреннее спокойствие у воды или быстрый доступ к деловому центру?"
    else:
        msg = f"Budget {text} noted!\n\n🤔 What's more important: peaceful morning by water or quick access to business center?"
    
    send_message(chat_id, msg, keyboard)

def handle_priority_selection(chat_id, text, session):
    """Обработка выбора приоритетов"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🌊 Утро у воды', '🌊 Water morning']:
        session['data']['priority'] = 'water'
    elif text in ['🏙️ Доступ к центру', '🏙️ City access']:
        session['data']['priority'] = 'center'
    elif text in ['⚖️ Баланс', '⚖️ Balance']:
        session['data']['priority'] = 'balance'
    else:
        msg = "Пожалуйста, выберите один из вариантов" if lang == 'ru' else "Please choose one of the options"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'show_locations'
    show_location_pulse(chat_id, session)

def show_location_pulse(chat_id, session):
    """Показ пульса локаций"""
    lang = session['data'].get('language', 'ru')
    priority = session['data'].get('priority')
    role = session['data'].get('role')
    
    if lang == 'ru':
        msg = "🌊 <b>Пульс локаций под твой профиль</b>\n\n"
        
        if priority == 'water' or priority == 'balance':
            msg += "🏝️ <b>Palm Jumeirah</b>\n"
            msg += "Ранний свет, частный ритуал утра\n"
            msg += "Якоря: тишина фронта, панорама\n\n"
            
            msg += "🌊 <b>Dubai Marina</b>\n"
            msg += "Водный ритм, динамика яхт\n"
            msg += "Атмосфера: активная жизнь у воды\n\n"
        
        if priority == 'center' or priority == 'balance':
            msg += "🏙️ <b>Downtown Dubai</b>\n"
            msg += "Энергия центра, вертикальная панорама\n"
            msg += "Фокус: динамика города, престиж высоты\n\n"
            
            msg += "🏛️ <b>Business Bay</b>\n"
            msg += "Бизнес-пульс, инвестиционный фокус\n"
            msg += "Профиль: деловой центр, ликвидность\n\n"
        
        keyboard = {
            'keyboard': [
                ['📞 Связаться с брокером'],
                ['🔄 Начать заново']
            ],
            'resize_keyboard': True
        }
        
        msg += "🎯 <b>Готов к детальному разбору?</b>"
        
    else:
        msg = "🌊 <b>Location Pulse for Your Profile</b>\n\n"
        
        if priority == 'water' or priority == 'balance':
            msg += "🏝️ <b>Palm Jumeirah</b>\n"
            msg += "Early light, private morning ritual\n"
            msg += "Anchors: front serenity, panorama\n\n"
            
            msg += "🌊 <b>Dubai Marina</b>\n"
            msg += "Water rhythm, yacht dynamics\n"
            msg += "Atmosphere: active waterfront life\n\n"
        
        if priority == 'center' or priority == 'balance':
            msg += "🏙️ <b>Downtown Dubai</b>\n"
            msg += "City energy, vertical panorama\n"
            msg += "Focus: urban dynamics, height prestige\n\n"
            
            msg += "🏛️ <b>Business Bay</b>\n"
            msg += "Business pulse, investment focus\n"
            msg += "Profile: business center, liquidity\n\n"
        
        keyboard = {
            'keyboard': [
                ['📞 Contact broker'],
                ['🔄 Start over']
            ],
            'resize_keyboard': True
        }
        
        msg += "🎯 <b>Ready for detailed analysis?</b>"
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_location_selection(chat_id, text, session):
    """Обработка финальных действий"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📞 Связаться с брокером', '📞 Contact broker']:
        handle_broker_contact(chat_id, session)
    elif text in ['🔄 Начать заново', '🔄 Start over']:
        handle_start(chat_id)
    else:
        msg = "Выберите действие из предложенных" if lang == 'ru' else "Choose an action from the suggested options"
        send_message(chat_id, msg)

def handle_broker_contact(chat_id, session):
    """Обработка запроса на связь с брокером"""
    lang = session['data'].get('language', 'ru')
    
    # Сохраняем данные пользователя (в реальности - в базу данных)
    user_data = session['data']
    print(f"New lead: {user_data}")  # Для отладки
    
    if lang == 'ru':
        msg = "✅ <b>Запрос отправлен!</b>\n\n"
        msg += "Свяжусь с тобой в течение дня для уточнения деталей и подбора вариантов под твой сценарий.\n\n"
        msg += "📱 <b>Контакты:</b>\n"
        msg += "• Telegram: @ivandubai_signal_bot\n"
        msg += "• WhatsApp: +971502778021\n"
        msg += "• Website: ivandubai.xyz\n\n"
        msg += "🏠 <i>Ivan Tyrtyshnyy | Dubai Real Estate</i>"
    else:
        msg = "✅ <b>Request sent!</b>\n\n"
        msg += "I'll contact you within a day to clarify details and find options for your scenario.\n\n"
        msg += "📱 <b>Contacts:</b>\n"
        msg += "• Telegram: @ivandubai_signal_bot\n"
        msg += "• WhatsApp: +971502778021\n"
        msg += "• Website: ivandubai.xyz\n\n"
        msg += "🏠 <i>Ivan Tyrtyshnyy | Dubai Real Estate</i>"
    
    keyboard = {
        'keyboard': [
            ['🔄 Начать заново'] if lang == 'ru' else ['🔄 Start over']
        ],
        'resize_keyboard': True
    }
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

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
        return response.json()
    except Exception as e:
        print(f"Send message error: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
