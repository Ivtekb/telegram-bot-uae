from flask import Flask, request, jsonify
import requests
import os
import re
from datetime import datetime

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
        
        # Обработка callback кнопок (inline keyboard)
        if update.get('callback_query'):
            callback = update['callback_query']
            chat_id = callback['from']['id']
            data = callback['data']
            message_id = callback['message']['message_id']
            
            handle_callback(callback)
        
        # Обработка обычных сообщений
        elif update and update.get('message'):
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            first_name = update['message']['from'].get('first_name', 'друг')
            
            # Получить сессию пользователя
            if chat_id not in user_sessions:
                user_sessions[chat_id] = {'stage': 'start', 'data': {'name': first_name}}
            
            session = user_sessions[chat_id]
            
            # Маршрутизация сообщений
            route_message(chat_id, text, session)
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error'})

def route_message(chat_id, text, session):
    """Маршрутизация сообщений по этапам"""
    stage = session.get('stage', 'start')
    
    if text == '/start':
        handle_start(chat_id)
    elif stage == 'language_select':
        handle_language_selection(chat_id, text, session)
    elif stage == 'role_select':
        handle_role_selection(chat_id, text, session)
    elif stage == 'budget_input':
        handle_budget_input(chat_id, text, session)
    elif stage == 'priority_select':
        handle_priority_selection(chat_id, text, session)
    elif stage == 'show_locations':
        handle_location_selection(chat_id, text, session)
    # Модуль владелец (продать/сдать)
    elif stage == 'owner_action_select':
        handle_owner_action_selection(chat_id, text, session)
    elif stage == 'owner_property_type':
        handle_owner_property_type(chat_id, text, session)
    elif stage == 'owner_rooms':
        handle_owner_rooms(chat_id, text, session)
    elif stage == 'owner_features':
        handle_owner_features(chat_id, text, session)
    elif stage == 'owner_occupancy':
        handle_owner_occupancy(chat_id, text, session)
    elif stage == 'owner_price_range':
        handle_owner_price_range(chat_id, text, session)
    elif stage == 'owner_documents':
        handle_owner_documents(chat_id, text, session)
    elif stage == 'owner_additional_params':
        handle_owner_additional_params(chat_id, text, session)
    # Модуль контактов
    elif stage == 'contact_method_select':
        handle_contact_method_selection(chat_id, text, session)
    elif stage == 'phone_input':
        handle_phone_input(chat_id, text, session)
    elif stage == 'email_input':
        handle_email_input(chat_id, text, session)
    elif stage == 'telegram_input':
        handle_telegram_input(chat_id, text, session)
    elif stage == 'contact_confirmation':
        handle_contact_confirmation(chat_id, text, session)
    else:
        send_message(chat_id, msg, parse_mode='HTML')
    else:
        msg = "Выберите способ связи" if lang == 'ru' else "Choose contact method"
        send_message(chat_id, msg)

def handle_phone_input(chat_id, text, session):
    """Обработка ввода телефона"""
    lang = session['data'].get('language', 'ru')
    
    if text == '✍️ Ввести вручную' or text == '✍️ Enter manually':
        if lang == 'ru':
            msg = "📱 Введите номер в международном формате:\n\n<i>Пример: +971501234567</i>"
        else:
            msg = "📱 Enter number in international format:\n\n<i>Example: +971501234567</i>"
        send_message(chat_id, msg, parse_mode='HTML')
        return
    
    # Валидация телефона
    phone_pattern = r'^(\+?\d{9,15})d, "Используйте /start для начала работы с ботом")

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
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'owner'
        session['stage'] = 'owner_action_select'
        start_owner_flow(chat_id, session)
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    else:
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)

def ask_budget(chat_id, session):
    """Запрос бюджета для покупателей/инвесторов"""
    lang = session['data'].get('language', 'ru')
    
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
    """Обработка финальных действий для покупателей"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📞 Связаться с брокером', '📞 Contact broker']:
        session['stage'] = 'contact_method_select'
        start_contact_flow(chat_id, session)
    elif text in ['🔄 Начать заново', '🔄 Start over']:
        handle_start(chat_id)
    else:
        msg = "Выберите действие из предложенных" if lang == 'ru' else "Choose an action from the suggested options"
        send_message(chat_id, msg)

# ==================== МОДУЛЬ ВЛАДЕЛЕЦ (ПРОДАТЬ/СДАТЬ) ====================

def start_owner_flow(chat_id, session):
    """Начало флоу для владельцев"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏡 Продать', '🏠 Сдать в аренду'],
            ['🔄 И то, и другое']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏠 <b>Модуль владельца</b>\n\nЧто планируете с объектом?"
    else:
        msg = "🏠 <b>Owner Module</b>\n\nWhat are your plans with the property?"
        keyboard['keyboard'] = [
            ['🏡 Sell', '🏠 Rent'],
            ['🔄 Both']
        ]
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_owner_action_selection(chat_id, text, session):
    """Выбор действия владельца"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏡 Продать', '🏡 Sell']:
        session['data']['owner_action'] = 'sell'
    elif text in ['🏠 Сдать в аренду', '🏠 Rent']:
        session['data']['owner_action'] = 'rent'
    elif text in ['🔄 И то, и другое', '🔄 Both']:
        session['data']['owner_action'] = 'both'
    else:
        msg = "Выберите один из вариантов" if lang == 'ru' else "Choose one of the options"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_property_type'
    
    keyboard = {
        'keyboard': [
            ['🏘️ Вилла', '🏢 Апартаменты'],
            ['🏬 Коммерческая недвижимость']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏗️ Сцена объекта:"
    else:
        msg = "🏗️ Property type:"
        keyboard['keyboard'] = [
            ['🏘️ Villa', '🏢 Apartment'],
            ['🏬 Commercial']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_property_type(chat_id, text, session):
    """Тип недвижимости"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏘️ Вилла', '🏘️ Villa']:
        session['data']['property_type'] = 'villa'
    elif text in ['🏢 Апартаменты', '🏢 Apartment']:
        session['data']['property_type'] = 'apartment'
    elif text in ['🏬 Коммерческая недвижимость', '🏬 Commercial']:
        session['data']['property_type'] = 'commercial'
    else:
        msg = "Выберите тип недвижимости" if lang == 'ru' else "Choose property type"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_rooms'
    
    keyboard = {
        'keyboard': [
            ['1', '2', '3'],
            ['4', '5+', 'Студия']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🛏️ Количество тихих зон (спален)?"
    else:
        msg = "🛏️ Number of quiet zones (bedrooms)?"
        keyboard['keyboard'] = [
            ['1', '2', '3'],
            ['4', '5+', 'Studio']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_rooms(chat_id, text, session):
    """Количество комнат"""
    session['data']['rooms'] = text
    session['stage'] = 'owner_features'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🌅 Терраса', '🏙️ Панорама'],
            ['🚪 Приватный вход', '🏡 Площадь'],
            ['✅ Все важно']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "✨ Основной акцент объекта:"
    else:
        msg = "✨ Main property highlight:"
        keyboard['keyboard'] = [
            ['🌅 Terrace', '🏙️ Panorama'],
            ['🚪 Private entrance', '🏡 Area'],
            ['✅ All important']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_features(chat_id, text, session):
    """Особенности объекта"""
    session['data']['features'] = text
    session['stage'] = 'owner_occupancy'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏠 Пустой', '👥 Сдан в аренду'],
            ['🏡 Живу сам']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🔍 Объект сейчас:"
    else:
        msg = "🔍 Property status:"
        keyboard['keyboard'] = [
            ['🏠 Vacant', '👥 Rented'],
            ['🏡 Owner occupied']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_occupancy(chat_id, text, session):
    """Статус объекта"""
    session['data']['occupancy'] = text
    lang = session['data'].get('language', 'ru')
    
    # Если сдан в аренду - уточняем детали
    if text in ['👥 Сдан в аренду', '👥 Rented']:
        if lang == 'ru':
            msg = "📅 До какого срока аренда? (например: до марта 2025)"
        else:
            msg = "📅 Rental contract until? (example: until March 2025)"
        
        send_message(chat_id, msg)
        session['stage'] = 'owner_price_range'
        return
    
    session['stage'] = 'owner_price_range'
    
    if lang == 'ru':
        msg = "💰 Диапазон цены, который устроит?\n\n(например: 2.5-3M AED для продажи или 15-18K AED/месяц для аренды)"
    else:
        msg = "💰 Price range that works for you?\n\n(example: 2.5-3M AED for sale or 15-18K AED/month for rent)"
    
    send_message(chat_id, msg)

def handle_owner_price_range(chat_id, text, session):
    """Ценовой диапазон"""
    session['data']['price_range'] = text
    session['stage'] = 'owner_documents'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['✅ Все готово', '📋 Частично'],
            ['❌ Нужна помощь']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📑 Документы готовы? (Title Deed, Passport, etc.)"
    else:
        msg = "📑 Documents ready? (Title Deed, Passport, etc.)"
        keyboard['keyboard'] = [
            ['✅ All ready', '📋 Partially'],
            ['❌ Need help']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_documents(chat_id, text, session):
    """Готовность документов"""
    session['data']['documents'] = text
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    
    # Дополнительные параметры для аренды
    if owner_action in ['rent', 'both']:
        session['stage'] = 'owner_additional_params'
        
        keyboard = {
            'keyboard': [
                ['🛋️ С мебелью', '🏠 Без мебели'],
                ['🔄 На выбор арендатора']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "🪑 Мебель в объекте:"
        else:
            msg = "🪑 Furniture in property:"
            keyboard['keyboard'] = [
                ['🛋️ Furnished', '🏠 Unfurnished'],
                ['🔄 Tenant choice']
            ]
        
        send_message(chat_id, msg, keyboard)
        return
    
    # Переход к AI анализу и контактам
    session['stage'] = 'contact_method_select'
    provide_ai_signal(chat_id, session)

def handle_owner_additional_params(chat_id, text, session):
    """Дополнительные параметры для аренды"""
    session['data']['furniture'] = text
    session['stage'] = 'contact_method_select'
    
    # AI анализ готовности к рынку
    provide_ai_signal(chat_id, session)

def provide_ai_signal(chat_id, session):
    """AI сигнал о готовности к рынку"""
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    documents = session['data'].get('documents')
    
    if lang == 'ru':
        if documents in ['✅ Все готово', '✅ All ready']:
            signal = "🟢 <b>Честный сигнал:</b> можно идти в рынок сразу.\n\n"
            signal += "✅ Документы готовы\n"
            signal += "✅ Рынок активен для вашего сегмента\n"
            signal += "⚡ Рекомендация: качественные фото + правильная цена = быстрая сделка"
        else:
            signal = "🟡 <b>Честный сигнал:</b> лучше подготовиться.\n\n"
            signal += "📋 Завершить документооборот\n"
            signal += "📸 Профессиональные фото\n"
            signal += "🛠️ Возможен легкий refresh интерьера\n"
            signal += "📈 Это повысит цену на 3-7%"
        
        signal += f"\n\n🎯 Готов передать профиль брокеру для {owner_action}?"
    else:
        if documents in ['✅ All ready']:
            signal = "🟢 <b>Honest signal:</b> ready for market now.\n\n"
            signal += "✅ Documents ready\n"
            signal += "✅ Market is active for your segment\n"
            signal += "⚡ Recommendation: quality photos + right price = quick deal"
        else:
            signal = "🟡 <b>Honest signal:</b> better to prepare.\n\n"
            signal += "📋 Complete documentation\n"
            signal += "📸 Professional photos\n" 
            signal += "🛠️ Light interior refresh possible\n"
            signal += "📈 This increases price by 3-7%"
        
        signal += f"\n\n🎯 Ready to pass profile to broker for {owner_action}?"
    
    send_message(chat_id, signal, parse_mode='HTML')
    
    # Переход к сбору контактов
    start_contact_flow(chat_id, session)

# ==================== МОДУЛЬ КОНТАКТОВ ====================

def start_contact_flow(chat_id, session):
    """Начalo сбора контактной информации"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['📱 Телефон', '💬 WhatsApp'],
            ['📧 Email', '📲 Telegram']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📞 <b>Как связаться удобнее?</b>\n\nВыберите предпочтительный способ:"
    else:
        msg = "📞 <b>How to contact you?</b>\n\nChoose preferred method:"
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_contact_method_selection(chat_id, text, session):
    """Выбор способа связи"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📱 Телефон', '💬 WhatsApp', '📱 Phone', '💬 WhatsApp']:
        session['data']['contact_method'] = 'phone'
        session['stage'] = 'phone_input'
        
        keyboard = {
            'keyboard': [
                [{'text': '📱 Поделиться номером', 'request_contact': True}],
                ['✍️ Ввести вручную']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "📱 <b>Номер телефона</b>\n\nМожете поделиться номером или ввести вручную:"
        else:
            msg = "📱 <b>Phone Number</b>\n\nYou can share your number or enter manually:"
            keyboard['keyboard'] = [
                [{'text': '📱 Share number', 'request_contact': True}],
                ['✍️ Enter manually']
            ]
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
        
    elif text in ['📧 Email']:
        session['data']['contact_method'] = 'email'
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = "📧 <b>Email адрес</b>\n\nВведите email для документов и планов:"
        else:
            msg = "📧 <b>Email Address</b>\n\nEnter email for documents and plans:"
        
        send_message(chat_id, msg, parse_mode='HTML')
        
    elif text in ['📲 Telegram']:
        session['data']['contact_method'] = 'telegram'
        session['stage'] = 'telegram_input'
        
        if lang == 'ru':
            msg = "📲 <b>Telegram</b>\n\nВведите ваш @username в Telegram:"
        else:
            msg = "📲 <b>Telegram</b>\n\nEnter your @username in Telegram:"
        
        send_message(chat_i
    clean_phone = re.sub(r'[^\d+]', '', text)
    
    if re.match(phone_pattern, clean_phone):
        session['data']['phone'] = clean_phone
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = f"✅ Телефон сохранен: {clean_phone}\n\n📧 <b>Email (опционально)</b>\n\nОставьте email для документов или нажмите 'Пропустить':"
        else:
            msg = f"✅ Phone saved: {clean_phone}\n\n📧 <b>Email (optional)</b>\n\nLeave email for documents or press 'Skip':"
        
        keyboard = {
            'keyboard': [['⏭️ Пропустить' if lang == 'ru' else '⏭️ Skip']],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
    else:
        if lang == 'ru':
            msg = "❌ Неверный формат номера.\n\nПожалуйста, введите в формате: +971501234567"
        else:
            msg = "❌ Invalid phone format.\n\nPlease enter like: +971501234567"
        send_message(chat_id, msg)

def handle_email_input(chat_id, text, session):
    """Обработка ввода email"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['⏭️ Пропустить', '⏭️ Skip']:
        session['data']['email'] = None
        session['stage'] = 'contact_confirmation'
        show_contact_confirmation(chat_id, session)
        return
    
    # Валидация email
    email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}d, "Используйте /start для начала работы с ботом")

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
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'owner'
        session['stage'] = 'owner_action_select'
        start_owner_flow(chat_id, session)
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    else:
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)

def ask_budget(chat_id, session):
    """Запрос бюджета для покупателей/инвесторов"""
    lang = session['data'].get('language', 'ru')
    
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
    """Обработка финальных действий для покупателей"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📞 Связаться с брокером', '📞 Contact broker']:
        session['stage'] = 'contact_method_select'
        start_contact_flow(chat_id, session)
    elif text in ['🔄 Начать заново', '🔄 Start over']:
        handle_start(chat_id)
    else:
        msg = "Выберите действие из предложенных" if lang == 'ru' else "Choose an action from the suggested options"
        send_message(chat_id, msg)

# ==================== МОДУЛЬ ВЛАДЕЛЕЦ (ПРОДАТЬ/СДАТЬ) ====================

def start_owner_flow(chat_id, session):
    """Начало флоу для владельцев"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏡 Продать', '🏠 Сдать в аренду'],
            ['🔄 И то, и другое']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏠 <b>Модуль владельца</b>\n\nЧто планируете с объектом?"
    else:
        msg = "🏠 <b>Owner Module</b>\n\nWhat are your plans with the property?"
        keyboard['keyboard'] = [
            ['🏡 Sell', '🏠 Rent'],
            ['🔄 Both']
        ]
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_owner_action_selection(chat_id, text, session):
    """Выбор действия владельца"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏡 Продать', '🏡 Sell']:
        session['data']['owner_action'] = 'sell'
    elif text in ['🏠 Сдать в аренду', '🏠 Rent']:
        session['data']['owner_action'] = 'rent'
    elif text in ['🔄 И то, и другое', '🔄 Both']:
        session['data']['owner_action'] = 'both'
    else:
        msg = "Выберите один из вариантов" if lang == 'ru' else "Choose one of the options"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_property_type'
    
    keyboard = {
        'keyboard': [
            ['🏘️ Вилла', '🏢 Апартаменты'],
            ['🏬 Коммерческая недвижимость']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏗️ Сцена объекта:"
    else:
        msg = "🏗️ Property type:"
        keyboard['keyboard'] = [
            ['🏘️ Villa', '🏢 Apartment'],
            ['🏬 Commercial']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_property_type(chat_id, text, session):
    """Тип недвижимости"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏘️ Вилла', '🏘️ Villa']:
        session['data']['property_type'] = 'villa'
    elif text in ['🏢 Апартаменты', '🏢 Apartment']:
        session['data']['property_type'] = 'apartment'
    elif text in ['🏬 Коммерческая недвижимость', '🏬 Commercial']:
        session['data']['property_type'] = 'commercial'
    else:
        msg = "Выберите тип недвижимости" if lang == 'ru' else "Choose property type"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_rooms'
    
    keyboard = {
        'keyboard': [
            ['1', '2', '3'],
            ['4', '5+', 'Студия']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🛏️ Количество тихих зон (спален)?"
    else:
        msg = "🛏️ Number of quiet zones (bedrooms)?"
        keyboard['keyboard'] = [
            ['1', '2', '3'],
            ['4', '5+', 'Studio']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_rooms(chat_id, text, session):
    """Количество комнат"""
    session['data']['rooms'] = text
    session['stage'] = 'owner_features'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🌅 Терраса', '🏙️ Панорама'],
            ['🚪 Приватный вход', '🏡 Площадь'],
            ['✅ Все важно']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "✨ Основной акцент объекта:"
    else:
        msg = "✨ Main property highlight:"
        keyboard['keyboard'] = [
            ['🌅 Terrace', '🏙️ Panorama'],
            ['🚪 Private entrance', '🏡 Area'],
            ['✅ All important']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_features(chat_id, text, session):
    """Особенности объекта"""
    session['data']['features'] = text
    session['stage'] = 'owner_occupancy'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏠 Пустой', '👥 Сдан в аренду'],
            ['🏡 Живу сам']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🔍 Объект сейчас:"
    else:
        msg = "🔍 Property status:"
        keyboard['keyboard'] = [
            ['🏠 Vacant', '👥 Rented'],
            ['🏡 Owner occupied']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_occupancy(chat_id, text, session):
    """Статус объекта"""
    session['data']['occupancy'] = text
    lang = session['data'].get('language', 'ru')
    
    # Если сдан в аренду - уточняем детали
    if text in ['👥 Сдан в аренду', '👥 Rented']:
        if lang == 'ru':
            msg = "📅 До какого срока аренда? (например: до марта 2025)"
        else:
            msg = "📅 Rental contract until? (example: until March 2025)"
        
        send_message(chat_id, msg)
        session['stage'] = 'owner_price_range'
        return
    
    session['stage'] = 'owner_price_range'
    
    if lang == 'ru':
        msg = "💰 Диапазон цены, который устроит?\n\n(например: 2.5-3M AED для продажи или 15-18K AED/месяц для аренды)"
    else:
        msg = "💰 Price range that works for you?\n\n(example: 2.5-3M AED for sale or 15-18K AED/month for rent)"
    
    send_message(chat_id, msg)

def handle_owner_price_range(chat_id, text, session):
    """Ценовой диапазон"""
    session['data']['price_range'] = text
    session['stage'] = 'owner_documents'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['✅ Все готово', '📋 Частично'],
            ['❌ Нужна помощь']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📑 Документы готовы? (Title Deed, Passport, etc.)"
    else:
        msg = "📑 Documents ready? (Title Deed, Passport, etc.)"
        keyboard['keyboard'] = [
            ['✅ All ready', '📋 Partially'],
            ['❌ Need help']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_documents(chat_id, text, session):
    """Готовность документов"""
    session['data']['documents'] = text
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    
    # Дополнительные параметры для аренды
    if owner_action in ['rent', 'both']:
        session['stage'] = 'owner_additional_params'
        
        keyboard = {
            'keyboard': [
                ['🛋️ С мебелью', '🏠 Без мебели'],
                ['🔄 На выбор арендатора']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "🪑 Мебель в объекте:"
        else:
            msg = "🪑 Furniture in property:"
            keyboard['keyboard'] = [
                ['🛋️ Furnished', '🏠 Unfurnished'],
                ['🔄 Tenant choice']
            ]
        
        send_message(chat_id, msg, keyboard)
        return
    
    # Переход к AI анализу и контактам
    session['stage'] = 'contact_method_select'
    provide_ai_signal(chat_id, session)

def handle_owner_additional_params(chat_id, text, session):
    """Дополнительные параметры для аренды"""
    session['data']['furniture'] = text
    session['stage'] = 'contact_method_select'
    
    # AI анализ готовности к рынку
    provide_ai_signal(chat_id, session)

def provide_ai_signal(chat_id, session):
    """AI сигнал о готовности к рынку"""
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    documents = session['data'].get('documents')
    
    if lang == 'ru':
        if documents in ['✅ Все готово', '✅ All ready']:
            signal = "🟢 <b>Честный сигнал:</b> можно идти в рынок сразу.\n\n"
            signal += "✅ Документы готовы\n"
            signal += "✅ Рынок активен для вашего сегмента\n"
            signal += "⚡ Рекомендация: качественные фото + правильная цена = быстрая сделка"
        else:
            signal = "🟡 <b>Честный сигнал:</b> лучше подготовиться.\n\n"
            signal += "📋 Завершить документооборот\n"
            signal += "📸 Профессиональные фото\n"
            signal += "🛠️ Возможен легкий refresh интерьера\n"
            signal += "📈 Это повысит цену на 3-7%"
        
        signal += f"\n\n🎯 Готов передать профиль брокеру для {owner_action}?"
    else:
        if documents in ['✅ All ready']:
            signal = "🟢 <b>Honest signal:</b> ready for market now.\n\n"
            signal += "✅ Documents ready\n"
            signal += "✅ Market is active for your segment\n"
            signal += "⚡ Recommendation: quality photos + right price = quick deal"
        else:
            signal = "🟡 <b>Honest signal:</b> better to prepare.\n\n"
            signal += "📋 Complete documentation\n"
            signal += "📸 Professional photos\n" 
            signal += "🛠️ Light interior refresh possible\n"
            signal += "📈 This increases price by 3-7%"
        
        signal += f"\n\n🎯 Ready to pass profile to broker for {owner_action}?"
    
    send_message(chat_id, signal, parse_mode='HTML')
    
    # Переход к сбору контактов
    start_contact_flow(chat_id, session)

# ==================== МОДУЛЬ КОНТАКТОВ ====================

def start_contact_flow(chat_id, session):
    """Начalo сбора контактной информации"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['📱 Телефон', '💬 WhatsApp'],
            ['📧 Email', '📲 Telegram']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📞 <b>Как связаться удобнее?</b>\n\nВыберите предпочтительный способ:"
    else:
        msg = "📞 <b>How to contact you?</b>\n\nChoose preferred method:"
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_contact_method_selection(chat_id, text, session):
    """Выбор способа связи"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📱 Телефон', '💬 WhatsApp', '📱 Phone', '💬 WhatsApp']:
        session['data']['contact_method'] = 'phone'
        session['stage'] = 'phone_input'
        
        keyboard = {
            'keyboard': [
                [{'text': '📱 Поделиться номером', 'request_contact': True}],
                ['✍️ Ввести вручную']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "📱 <b>Номер телефона</b>\n\nМожете поделиться номером или ввести вручную:"
        else:
            msg = "📱 <b>Phone Number</b>\n\nYou can share your number or enter manually:"
            keyboard['keyboard'] = [
                [{'text': '📱 Share number', 'request_contact': True}],
                ['✍️ Enter manually']
            ]
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
        
    elif text in ['📧 Email']:
        session['data']['contact_method'] = 'email'
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = "📧 <b>Email адрес</b>\n\nВведите email для документов и планов:"
        else:
            msg = "📧 <b>Email Address</b>\n\nEnter email for documents and plans:"
        
        send_message(chat_id, msg, parse_mode='HTML')
        
    elif text in ['📲 Telegram']:
        session['data']['contact_method'] = 'telegram'
        session['stage'] = 'telegram_input'
        
        if lang == 'ru':
            msg = "📲 <b>Telegram</b>\n\nВведите ваш @username в Telegram:"
        else:
            msg = "📲 <b>Telegram</b>\n\nEnter your @username in Telegram:"
        
        send_message(chat_i
    
    if re.match(email_pattern, text):
        session['data']['email'] = text
        session['stage'] = 'contact_confirmation'
        show_contact_confirmation(chat_id, session)
    else:
        if lang == 'ru':
            msg = "❌ Неверный формат email.\n\nПример: name@mail.com"
        else:
            msg = "❌ Invalid email format.\n\nExample: name@mail.com"
        send_message(chat_id, msg)

def handle_telegram_input(chat_id, text, session):
    """Обработка ввода Telegram username"""
    lang = session['data'].get('language', 'ru')
    
    # Валидация Telegram username
    tg_pattern = r'^@[A-Za-z0-9_]{5,32}d, "Используйте /start для начала работы с ботом")

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
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'owner'
        session['stage'] = 'owner_action_select'
        start_owner_flow(chat_id, session)
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    else:
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)

def ask_budget(chat_id, session):
    """Запрос бюджета для покупателей/инвесторов"""
    lang = session['data'].get('language', 'ru')
    
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
    """Обработка финальных действий для покупателей"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📞 Связаться с брокером', '📞 Contact broker']:
        session['stage'] = 'contact_method_select'
        start_contact_flow(chat_id, session)
    elif text in ['🔄 Начать заново', '🔄 Start over']:
        handle_start(chat_id)
    else:
        msg = "Выберите действие из предложенных" if lang == 'ru' else "Choose an action from the suggested options"
        send_message(chat_id, msg)

# ==================== МОДУЛЬ ВЛАДЕЛЕЦ (ПРОДАТЬ/СДАТЬ) ====================

def start_owner_flow(chat_id, session):
    """Начало флоу для владельцев"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏡 Продать', '🏠 Сдать в аренду'],
            ['🔄 И то, и другое']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏠 <b>Модуль владельца</b>\n\nЧто планируете с объектом?"
    else:
        msg = "🏠 <b>Owner Module</b>\n\nWhat are your plans with the property?"
        keyboard['keyboard'] = [
            ['🏡 Sell', '🏠 Rent'],
            ['🔄 Both']
        ]
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_owner_action_selection(chat_id, text, session):
    """Выбор действия владельца"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏡 Продать', '🏡 Sell']:
        session['data']['owner_action'] = 'sell'
    elif text in ['🏠 Сдать в аренду', '🏠 Rent']:
        session['data']['owner_action'] = 'rent'
    elif text in ['🔄 И то, и другое', '🔄 Both']:
        session['data']['owner_action'] = 'both'
    else:
        msg = "Выберите один из вариантов" if lang == 'ru' else "Choose one of the options"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_property_type'
    
    keyboard = {
        'keyboard': [
            ['🏘️ Вилла', '🏢 Апартаменты'],
            ['🏬 Коммерческая недвижимость']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏗️ Сцена объекта:"
    else:
        msg = "🏗️ Property type:"
        keyboard['keyboard'] = [
            ['🏘️ Villa', '🏢 Apartment'],
            ['🏬 Commercial']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_property_type(chat_id, text, session):
    """Тип недвижимости"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏘️ Вилла', '🏘️ Villa']:
        session['data']['property_type'] = 'villa'
    elif text in ['🏢 Апартаменты', '🏢 Apartment']:
        session['data']['property_type'] = 'apartment'
    elif text in ['🏬 Коммерческая недвижимость', '🏬 Commercial']:
        session['data']['property_type'] = 'commercial'
    else:
        msg = "Выберите тип недвижимости" if lang == 'ru' else "Choose property type"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_rooms'
    
    keyboard = {
        'keyboard': [
            ['1', '2', '3'],
            ['4', '5+', 'Студия']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🛏️ Количество тихих зон (спален)?"
    else:
        msg = "🛏️ Number of quiet zones (bedrooms)?"
        keyboard['keyboard'] = [
            ['1', '2', '3'],
            ['4', '5+', 'Studio']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_rooms(chat_id, text, session):
    """Количество комнат"""
    session['data']['rooms'] = text
    session['stage'] = 'owner_features'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🌅 Терраса', '🏙️ Панорама'],
            ['🚪 Приватный вход', '🏡 Площадь'],
            ['✅ Все важно']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "✨ Основной акцент объекта:"
    else:
        msg = "✨ Main property highlight:"
        keyboard['keyboard'] = [
            ['🌅 Terrace', '🏙️ Panorama'],
            ['🚪 Private entrance', '🏡 Area'],
            ['✅ All important']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_features(chat_id, text, session):
    """Особенности объекта"""
    session['data']['features'] = text
    session['stage'] = 'owner_occupancy'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏠 Пустой', '👥 Сдан в аренду'],
            ['🏡 Живу сам']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🔍 Объект сейчас:"
    else:
        msg = "🔍 Property status:"
        keyboard['keyboard'] = [
            ['🏠 Vacant', '👥 Rented'],
            ['🏡 Owner occupied']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_occupancy(chat_id, text, session):
    """Статус объекта"""
    session['data']['occupancy'] = text
    lang = session['data'].get('language', 'ru')
    
    # Если сдан в аренду - уточняем детали
    if text in ['👥 Сдан в аренду', '👥 Rented']:
        if lang == 'ru':
            msg = "📅 До какого срока аренда? (например: до марта 2025)"
        else:
            msg = "📅 Rental contract until? (example: until March 2025)"
        
        send_message(chat_id, msg)
        session['stage'] = 'owner_price_range'
        return
    
    session['stage'] = 'owner_price_range'
    
    if lang == 'ru':
        msg = "💰 Диапазон цены, который устроит?\n\n(например: 2.5-3M AED для продажи или 15-18K AED/месяц для аренды)"
    else:
        msg = "💰 Price range that works for you?\n\n(example: 2.5-3M AED for sale or 15-18K AED/month for rent)"
    
    send_message(chat_id, msg)

def handle_owner_price_range(chat_id, text, session):
    """Ценовой диапазон"""
    session['data']['price_range'] = text
    session['stage'] = 'owner_documents'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['✅ Все готово', '📋 Частично'],
            ['❌ Нужна помощь']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📑 Документы готовы? (Title Deed, Passport, etc.)"
    else:
        msg = "📑 Documents ready? (Title Deed, Passport, etc.)"
        keyboard['keyboard'] = [
            ['✅ All ready', '📋 Partially'],
            ['❌ Need help']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_documents(chat_id, text, session):
    """Готовность документов"""
    session['data']['documents'] = text
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    
    # Дополнительные параметры для аренды
    if owner_action in ['rent', 'both']:
        session['stage'] = 'owner_additional_params'
        
        keyboard = {
            'keyboard': [
                ['🛋️ С мебелью', '🏠 Без мебели'],
                ['🔄 На выбор арендатора']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "🪑 Мебель в объекте:"
        else:
            msg = "🪑 Furniture in property:"
            keyboard['keyboard'] = [
                ['🛋️ Furnished', '🏠 Unfurnished'],
                ['🔄 Tenant choice']
            ]
        
        send_message(chat_id, msg, keyboard)
        return
    
    # Переход к AI анализу и контактам
    session['stage'] = 'contact_method_select'
    provide_ai_signal(chat_id, session)

def handle_owner_additional_params(chat_id, text, session):
    """Дополнительные параметры для аренды"""
    session['data']['furniture'] = text
    session['stage'] = 'contact_method_select'
    
    # AI анализ готовности к рынку
    provide_ai_signal(chat_id, session)

def provide_ai_signal(chat_id, session):
    """AI сигнал о готовности к рынку"""
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    documents = session['data'].get('documents')
    
    if lang == 'ru':
        if documents in ['✅ Все готово', '✅ All ready']:
            signal = "🟢 <b>Честный сигнал:</b> можно идти в рынок сразу.\n\n"
            signal += "✅ Документы готовы\n"
            signal += "✅ Рынок активен для вашего сегмента\n"
            signal += "⚡ Рекомендация: качественные фото + правильная цена = быстрая сделка"
        else:
            signal = "🟡 <b>Честный сигнал:</b> лучше подготовиться.\n\n"
            signal += "📋 Завершить документооборот\n"
            signal += "📸 Профессиональные фото\n"
            signal += "🛠️ Возможен легкий refresh интерьера\n"
            signal += "📈 Это повысит цену на 3-7%"
        
        signal += f"\n\n🎯 Готов передать профиль брокеру для {owner_action}?"
    else:
        if documents in ['✅ All ready']:
            signal = "🟢 <b>Honest signal:</b> ready for market now.\n\n"
            signal += "✅ Documents ready\n"
            signal += "✅ Market is active for your segment\n"
            signal += "⚡ Recommendation: quality photos + right price = quick deal"
        else:
            signal = "🟡 <b>Honest signal:</b> better to prepare.\n\n"
            signal += "📋 Complete documentation\n"
            signal += "📸 Professional photos\n" 
            signal += "🛠️ Light interior refresh possible\n"
            signal += "📈 This increases price by 3-7%"
        
        signal += f"\n\n🎯 Ready to pass profile to broker for {owner_action}?"
    
    send_message(chat_id, signal, parse_mode='HTML')
    
    # Переход к сбору контактов
    start_contact_flow(chat_id, session)

# ==================== МОДУЛЬ КОНТАКТОВ ====================

def start_contact_flow(chat_id, session):
    """Начalo сбора контактной информации"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['📱 Телефон', '💬 WhatsApp'],
            ['📧 Email', '📲 Telegram']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📞 <b>Как связаться удобнее?</b>\n\nВыберите предпочтительный способ:"
    else:
        msg = "📞 <b>How to contact you?</b>\n\nChoose preferred method:"
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_contact_method_selection(chat_id, text, session):
    """Выбор способа связи"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📱 Телефон', '💬 WhatsApp', '📱 Phone', '💬 WhatsApp']:
        session['data']['contact_method'] = 'phone'
        session['stage'] = 'phone_input'
        
        keyboard = {
            'keyboard': [
                [{'text': '📱 Поделиться номером', 'request_contact': True}],
                ['✍️ Ввести вручную']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "📱 <b>Номер телефона</b>\n\nМожете поделиться номером или ввести вручную:"
        else:
            msg = "📱 <b>Phone Number</b>\n\nYou can share your number or enter manually:"
            keyboard['keyboard'] = [
                [{'text': '📱 Share number', 'request_contact': True}],
                ['✍️ Enter manually']
            ]
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
        
    elif text in ['📧 Email']:
        session['data']['contact_method'] = 'email'
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = "📧 <b>Email адрес</b>\n\nВведите email для документов и планов:"
        else:
            msg = "📧 <b>Email Address</b>\n\nEnter email for documents and plans:"
        
        send_message(chat_id, msg, parse_mode='HTML')
        
    elif text in ['📲 Telegram']:
        session['data']['contact_method'] = 'telegram'
        session['stage'] = 'telegram_input'
        
        if lang == 'ru':
            msg = "📲 <b>Telegram</b>\n\nВведите ваш @username в Telegram:"
        else:
            msg = "📲 <b>Telegram</b>\n\nEnter your @username in Telegram:"
        
        send_message(chat_i
    
    if not text.startswith('@'):
        text = '@' + text
    
    if re.match(tg_pattern, text):
        session['data']['telegram'] = text
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = f"✅ Telegram сохранен: {text}\n\n📧 <b>Email (опционально)</b>\n\nОставьте email для документов:"
        else:
            msg = f"✅ Telegram saved: {text}\n\n📧 <b>Email (optional)</b>\n\nLeave email for documents:"
        
        keyboard = {
            'keyboard': [['⏭️ Пропустить' if lang == 'ru' else '⏭️ Skip']],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
    else:
        if lang == 'ru':
            msg = "❌ Неверный формат.\n\nПример: @username (5-32 символа)"
        else:
            msg = "❌ Invalid format.\n\nExample: @username (5-32 characters)"
        send_message(chat_id, msg)

def show_contact_confirmation(chat_id, session):
    """Показ подтверждения контактных данных"""
    lang = session['data'].get('language', 'ru')
    data = session['data']
    
    if lang == 'ru':
        msg = "📋 <b>Проверьте данные:</b>\n\n"
    else:
        msg = "📋 <b>Verify information:</b>\n\n"
    
    if data.get('phone'):
        msg += f"📱 Телефон: {data['phone']}\n"
    if data.get('email'):
        msg += f"📧 Email: {data['email']}\n"
    if data.get('telegram'):
        msg += f"📲 Telegram: {data['telegram']}\n"
    
    if lang == 'ru':
        msg += "\n🎯 Передать профиль брокеру?"
    else:
        msg += "\n🎯 Send profile to broker?"
    
    keyboard = {
        'keyboard': [
            ['✅ Да, передать' if lang == 'ru' else '✅ Yes, send'],
            ['✏️ Исправить' if lang == 'ru' else '✏️ Correct']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_contact_confirmation(chat_id, text, session):
    """Подтверждение и отправка данных"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['✅ Да, передать', '✅ Yes, send']:
        # Отправляем детальную заявку вам
        send_detailed_lead_notification(session['data'], chat_id)
        
        # Подтверждение пользователю
        if lang == 'ru':
            msg = """✅ <b>Заявка отправлена!</b>

Свяжусь с вами в течение дня для уточнения деталей и подбора вариантов под ваш сценарий.

📱 <b>Контакты:</b>
• Telegram: @ivandubai_signal_bot
• WhatsApp: +971502778021
• Website: www.ivandubai.xyz

🏠 <i>Ivan Tyrtyshnyy | Dubai Real Estate</i>"""
        else:
            msg = """✅ <b>Request sent!</b>

I'll contact you within a day to clarify details and find options for your scenario.

📱 <b>Contacts:</b>
• Telegram: @ivandubai_signal_bot
• WhatsApp: +971502778021
• Website: www.ivandubai.xyz

🏠 <i>Ivan Tyrtyshnyy | Dubai Real Estate</i>"""
        
        keyboard = {
            'keyboard': [
                ['🔄 Начать заново' if lang == 'ru' else '🔄 Start over']
            ],
            'resize_keyboard': True
        }
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
        
    elif text in ['✏️ Исправить', '✏️ Correct']:
        session['stage'] = 'contact_method_select'
        start_contact_flow(chat_id, session)
    else:
        msg = "Выберите действие" if lang == 'ru' else "Choose action"
        send_message(chat_id, msg)

# ==================== УВЕДОМЛЕНИЯ БРОКЕРУ ====================

def send_detailed_lead_notification(user_data, client_chat_id):
    """Отправка детальной заявки в личный чат Ивана"""
    IVAN_CHAT_ID = "367380234"  # Ваш chat_id
    
    # Базовые данные
    lang = user_data.get('language', 'ru')
    name = user_data.get('name', 'Неизвестно')
    role = user_data.get('role', 'не указано')
    
    # Начало сообщения
    notification = f"""🔥 <b>НОВАЯ ДЕТАЛЬНАЯ ЗАЯВКА!</b>

👤 <b>Клиент:</b> {name}
🗣 <b>Язык:</b> {'Русский' if lang == 'ru' else 'English'}
📱 <b>Client ID:</b> <code>{client_chat_id}</code>
⏰ <b>Время:</b> {get_current_time()}

"""

    # Роль и специфичные данные
    if role == 'owner':
        notification += format_owner_notification(user_data)
    else:
        notification += format_buyer_notification(user_data)
    
    # Контактная информация
    notification += "\n📞 <b>КОНТАКТЫ:</b>\n"
    if user_data.get('phone'):
        notification += f"📱 Телефон: <code>{user_data['phone']}</code>\n"
    if user_data.get('email'):
        notification += f"📧 Email: <code>{user_data['email']}</code>\n"
    if user_data.get('telegram'):
        notification += f"📲 Telegram: {user_data['telegram']}\n"
    
    # Клавиатура для быстрых действий
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '✅ Взял в работу', 'callback_data': f'take_{client_chat_id}'},
                {'text': '📞 Связался', 'callback_data': f'contacted_{client_chat_id}'}
            ],
            [
                {'text': '📊 Статистика лидов', 'callback_data': 'stats'},
                {'text': '🏠 ivandubai.xyz', 'url': 'https://www.ivandubai.xyz'}
            ]
        ]
    }
    
    # Отправляем уведомление
    send_message(IVAN_CHAT_ID, notification, keyboard, parse_mode='HTML')
    print(f"Detailed lead notification sent: {user_data}")

def format_owner_notification(user_data):
    """Форматирование уведомления для владельцев"""
    notification = "🏠 <b>ТИП ЗАЯВКИ:</b> ВЛАДЕЛЕЦ\n\n"
    
    # Основные параметры
    owner_action = user_data.get('owner_action', 'не указано')
    if owner_action == 'sell':
        notification += "🎯 <b>Цель:</b> Продать\n"
    elif owner_action == 'rent':
        notification += "🎯 <b>Цель:</b> Сдать в аренду\n"
    elif owner_action == 'both':
        notification += "🎯 <b>Цель:</b> Продать И сдать\n"
    
    notification += f"🏗️ <b>Тип:</b> {user_data.get('property_type', 'не указано')}\n"
    notification += f"🛏️ <b>Комнат:</b> {user_data.get('rooms', 'не указано')}\n"
    notification += f"✨ <b>Акцент:</b> {user_data.get('features', 'не указано')}\n"
    notification += f"🔍 <b>Статус:</b> {user_data.get('occupancy', 'не указано')}\n"
    notification += f"💰 <b>Цена:</b> {user_data.get('price_range', 'не указано')}\n"
    notification += f"📑 <b>Документы:</b> {user_data.get('documents', 'не указано')}\n"
    
    if user_data.get('furniture'):
        notification += f"🪑 <b>Мебель:</b> {user_data['furniture']}\n"
    
    return notification

def format_buyer_notification(user_data):
    """Форматирование уведомления для покупателей"""
    notification = "🏠 <b>ТИП ЗАЯВКИ:</b> ПОКУПАТЕЛЬ/ИНВЕСТОР\n\n"
    
    # Роль
    role = user_data.get('role', 'не указано')
    role_names = {
        'live': 'Для жизни',
        'invest': 'Инвестиции',
        'mixed': 'Смешанный'
    }
    notification += f"🎯 <b>Цель:</b> {role_names.get(role, role)}\n"
    
    # Основные параметры
    notification += f"💰 <b>Бюджет:</b> {user_data.get('budget', 'не указан')}\n"
    
    priority = user_data.get('priority', 'не указан')
    priority_names = {
        'water': 'Утро у воды 🌊',
        'center': 'Доступ к центру 🏙️',
        'balance': 'Баланс ⚖️'
    }
    notification += f"🏠 <b>Приоритет:</b> {priority_names.get(priority, priority)}\n"
    
    # Рекомендации локаций
    notification += "\n🎯 <b>РЕКОМЕНДУЕМЫЕ ЛОКАЦИИ:</b>\n"
    if priority in ['water', 'balance']:
        notification += "• 🏝️ Palm Jumeirah\n• 🌊 Dubai Marina\n"
    if priority in ['center', 'balance']:
        notification += "• 🏙️ Downtown Dubai\n• 🏛️ Business Bay\n"
    
    return notification

def get_current_time():
    """Получить текущее время"""
    try:
        now = datetime.now()
        return now.strftime('%d.%m.%Y %H:%M')
    except:
        return "сейчас"

# ==================== CALLBACK ОБРАБОТКА ====================

def handle_callback(callback):
    """Обработка нажатий inline кнопок"""
    chat_id = callback['from']['id']
    data = callback['data']
    message_id = callback['message']['message_id']
    
    if data.startswith('take_'):
        client_id = data.replace('take_', '')
        answer_callback(callback['id'], f"✅ Лид {client_id} взят в работу!")
        edit_message_text(chat_id, message_id, f"✅ <b>Лид взят в работу</b>\n\nClient ID: {client_id}")
    
    elif data.startswith('contacted_'):
        client_id = data.replace('contacted_', '')
        answer_callback(callback['id'], f"📞 Отмечено: связь с {client_id}")
        edit_message_text(chat_id, message_id, f"📞 <b>Связь установлена</b>\n\nClient ID: {client_id}")
    
    elif data == 'stats':
        answer_callback(callback['id'], "📊 Статистика в разработке")

def answer_callback(callback_id, text):
    """Ответ на callback query"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {'callback_query_id': callback_id, 'text': text}
    requests.post(url, json=payload)

def edit_message_text(chat_id, message_id, text):
    """Редактирование сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(url, json=payload)

# ==================== ОТПРАВКА СООБЩЕНИЙ ====================

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
    app.run(host='0.0.0.0', port=port)d, "Используйте /start для начала работы с ботом")

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
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['📈 Инвестировать', '📈 Invest']:
        session['data']['role'] = 'invest'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    elif text in ['🔄 Продать/Сдать', '🔄 Sell/Rent']:
        session['data']['role'] = 'owner'
        session['stage'] = 'owner_action_select'
        start_owner_flow(chat_id, session)
    elif text in ['🎯 Смешанный', '🎯 Mixed']:
        session['data']['role'] = 'mixed'
        session['stage'] = 'budget_input'
        ask_budget(chat_id, session)
    else:
        msg = "Пожалуйста, выберите один из предложенных вариантов" if lang == 'ru' else "Please choose one of the suggested options"
        send_message(chat_id, msg)

def ask_budget(chat_id, session):
    """Запрос бюджета для покупателей/инвесторов"""
    lang = session['data'].get('language', 'ru')
    
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
    """Обработка финальных действий для покупателей"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📞 Связаться с брокером', '📞 Contact broker']:
        session['stage'] = 'contact_method_select'
        start_contact_flow(chat_id, session)
    elif text in ['🔄 Начать заново', '🔄 Start over']:
        handle_start(chat_id)
    else:
        msg = "Выберите действие из предложенных" if lang == 'ru' else "Choose an action from the suggested options"
        send_message(chat_id, msg)

# ==================== МОДУЛЬ ВЛАДЕЛЕЦ (ПРОДАТЬ/СДАТЬ) ====================

def start_owner_flow(chat_id, session):
    """Начало флоу для владельцев"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏡 Продать', '🏠 Сдать в аренду'],
            ['🔄 И то, и другое']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏠 <b>Модуль владельца</b>\n\nЧто планируете с объектом?"
    else:
        msg = "🏠 <b>Owner Module</b>\n\nWhat are your plans with the property?"
        keyboard['keyboard'] = [
            ['🏡 Sell', '🏠 Rent'],
            ['🔄 Both']
        ]
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_owner_action_selection(chat_id, text, session):
    """Выбор действия владельца"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏡 Продать', '🏡 Sell']:
        session['data']['owner_action'] = 'sell'
    elif text in ['🏠 Сдать в аренду', '🏠 Rent']:
        session['data']['owner_action'] = 'rent'
    elif text in ['🔄 И то, и другое', '🔄 Both']:
        session['data']['owner_action'] = 'both'
    else:
        msg = "Выберите один из вариантов" if lang == 'ru' else "Choose one of the options"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_property_type'
    
    keyboard = {
        'keyboard': [
            ['🏘️ Вилла', '🏢 Апартаменты'],
            ['🏬 Коммерческая недвижимость']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🏗️ Сцена объекта:"
    else:
        msg = "🏗️ Property type:"
        keyboard['keyboard'] = [
            ['🏘️ Villa', '🏢 Apartment'],
            ['🏬 Commercial']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_property_type(chat_id, text, session):
    """Тип недвижимости"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['🏘️ Вилла', '🏘️ Villa']:
        session['data']['property_type'] = 'villa'
    elif text in ['🏢 Апартаменты', '🏢 Apartment']:
        session['data']['property_type'] = 'apartment'
    elif text in ['🏬 Коммерческая недвижимость', '🏬 Commercial']:
        session['data']['property_type'] = 'commercial'
    else:
        msg = "Выберите тип недвижимости" if lang == 'ru' else "Choose property type"
        send_message(chat_id, msg)
        return
    
    session['stage'] = 'owner_rooms'
    
    keyboard = {
        'keyboard': [
            ['1', '2', '3'],
            ['4', '5+', 'Студия']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🛏️ Количество тихих зон (спален)?"
    else:
        msg = "🛏️ Number of quiet zones (bedrooms)?"
        keyboard['keyboard'] = [
            ['1', '2', '3'],
            ['4', '5+', 'Studio']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_rooms(chat_id, text, session):
    """Количество комнат"""
    session['data']['rooms'] = text
    session['stage'] = 'owner_features'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🌅 Терраса', '🏙️ Панорама'],
            ['🚪 Приватный вход', '🏡 Площадь'],
            ['✅ Все важно']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "✨ Основной акцент объекта:"
    else:
        msg = "✨ Main property highlight:"
        keyboard['keyboard'] = [
            ['🌅 Terrace', '🏙️ Panorama'],
            ['🚪 Private entrance', '🏡 Area'],
            ['✅ All important']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_features(chat_id, text, session):
    """Особенности объекта"""
    session['data']['features'] = text
    session['stage'] = 'owner_occupancy'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['🏠 Пустой', '👥 Сдан в аренду'],
            ['🏡 Живу сам']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "🔍 Объект сейчас:"
    else:
        msg = "🔍 Property status:"
        keyboard['keyboard'] = [
            ['🏠 Vacant', '👥 Rented'],
            ['🏡 Owner occupied']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_occupancy(chat_id, text, session):
    """Статус объекта"""
    session['data']['occupancy'] = text
    lang = session['data'].get('language', 'ru')
    
    # Если сдан в аренду - уточняем детали
    if text in ['👥 Сдан в аренду', '👥 Rented']:
        if lang == 'ru':
            msg = "📅 До какого срока аренда? (например: до марта 2025)"
        else:
            msg = "📅 Rental contract until? (example: until March 2025)"
        
        send_message(chat_id, msg)
        session['stage'] = 'owner_price_range'
        return
    
    session['stage'] = 'owner_price_range'
    
    if lang == 'ru':
        msg = "💰 Диапазон цены, который устроит?\n\n(например: 2.5-3M AED для продажи или 15-18K AED/месяц для аренды)"
    else:
        msg = "💰 Price range that works for you?\n\n(example: 2.5-3M AED for sale or 15-18K AED/month for rent)"
    
    send_message(chat_id, msg)

def handle_owner_price_range(chat_id, text, session):
    """Ценовой диапазон"""
    session['data']['price_range'] = text
    session['stage'] = 'owner_documents'
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['✅ Все готово', '📋 Частично'],
            ['❌ Нужна помощь']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📑 Документы готовы? (Title Deed, Passport, etc.)"
    else:
        msg = "📑 Documents ready? (Title Deed, Passport, etc.)"
        keyboard['keyboard'] = [
            ['✅ All ready', '📋 Partially'],
            ['❌ Need help']
        ]
    
    send_message(chat_id, msg, keyboard)

def handle_owner_documents(chat_id, text, session):
    """Готовность документов"""
    session['data']['documents'] = text
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    
    # Дополнительные параметры для аренды
    if owner_action in ['rent', 'both']:
        session['stage'] = 'owner_additional_params'
        
        keyboard = {
            'keyboard': [
                ['🛋️ С мебелью', '🏠 Без мебели'],
                ['🔄 На выбор арендатора']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "🪑 Мебель в объекте:"
        else:
            msg = "🪑 Furniture in property:"
            keyboard['keyboard'] = [
                ['🛋️ Furnished', '🏠 Unfurnished'],
                ['🔄 Tenant choice']
            ]
        
        send_message(chat_id, msg, keyboard)
        return
    
    # Переход к AI анализу и контактам
    session['stage'] = 'contact_method_select'
    provide_ai_signal(chat_id, session)

def handle_owner_additional_params(chat_id, text, session):
    """Дополнительные параметры для аренды"""
    session['data']['furniture'] = text
    session['stage'] = 'contact_method_select'
    
    # AI анализ готовности к рынку
    provide_ai_signal(chat_id, session)

def provide_ai_signal(chat_id, session):
    """AI сигнал о готовности к рынку"""
    lang = session['data'].get('language', 'ru')
    owner_action = session['data'].get('owner_action')
    documents = session['data'].get('documents')
    
    if lang == 'ru':
        if documents in ['✅ Все готово', '✅ All ready']:
            signal = "🟢 <b>Честный сигнал:</b> можно идти в рынок сразу.\n\n"
            signal += "✅ Документы готовы\n"
            signal += "✅ Рынок активен для вашего сегмента\n"
            signal += "⚡ Рекомендация: качественные фото + правильная цена = быстрая сделка"
        else:
            signal = "🟡 <b>Честный сигнал:</b> лучше подготовиться.\n\n"
            signal += "📋 Завершить документооборот\n"
            signal += "📸 Профессиональные фото\n"
            signal += "🛠️ Возможен легкий refresh интерьера\n"
            signal += "📈 Это повысит цену на 3-7%"
        
        signal += f"\n\n🎯 Готов передать профиль брокеру для {owner_action}?"
    else:
        if documents in ['✅ All ready']:
            signal = "🟢 <b>Honest signal:</b> ready for market now.\n\n"
            signal += "✅ Documents ready\n"
            signal += "✅ Market is active for your segment\n"
            signal += "⚡ Recommendation: quality photos + right price = quick deal"
        else:
            signal = "🟡 <b>Honest signal:</b> better to prepare.\n\n"
            signal += "📋 Complete documentation\n"
            signal += "📸 Professional photos\n" 
            signal += "🛠️ Light interior refresh possible\n"
            signal += "📈 This increases price by 3-7%"
        
        signal += f"\n\n🎯 Ready to pass profile to broker for {owner_action}?"
    
    send_message(chat_id, signal, parse_mode='HTML')
    
    # Переход к сбору контактов
    start_contact_flow(chat_id, session)

# ==================== МОДУЛЬ КОНТАКТОВ ====================

def start_contact_flow(chat_id, session):
    """Начalo сбора контактной информации"""
    lang = session['data'].get('language', 'ru')
    
    keyboard = {
        'keyboard': [
            ['📱 Телефон', '💬 WhatsApp'],
            ['📧 Email', '📲 Telegram']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    
    if lang == 'ru':
        msg = "📞 <b>Как связаться удобнее?</b>\n\nВыберите предпочтительный способ:"
    else:
        msg = "📞 <b>How to contact you?</b>\n\nChoose preferred method:"
    
    send_message(chat_id, msg, keyboard, parse_mode='HTML')

def handle_contact_method_selection(chat_id, text, session):
    """Выбор способа связи"""
    lang = session['data'].get('language', 'ru')
    
    if text in ['📱 Телефон', '💬 WhatsApp', '📱 Phone', '💬 WhatsApp']:
        session['data']['contact_method'] = 'phone'
        session['stage'] = 'phone_input'
        
        keyboard = {
            'keyboard': [
                [{'text': '📱 Поделиться номером', 'request_contact': True}],
                ['✍️ Ввести вручную']
            ],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
        
        if lang == 'ru':
            msg = "📱 <b>Номер телефона</b>\n\nМожете поделиться номером или ввести вручную:"
        else:
            msg = "📱 <b>Phone Number</b>\n\nYou can share your number or enter manually:"
            keyboard['keyboard'] = [
                [{'text': '📱 Share number', 'request_contact': True}],
                ['✍️ Enter manually']
            ]
        
        send_message(chat_id, msg, keyboard, parse_mode='HTML')
        
    elif text in ['📧 Email']:
        session['data']['contact_method'] = 'email'
        session['stage'] = 'email_input'
        
        if lang == 'ru':
            msg = "📧 <b>Email адрес</b>\n\nВведите email для документов и планов:"
        else:
            msg = "📧 <b>Email Address</b>\n\nEnter email for documents and plans:"
        
        send_message(chat_id, msg, parse_mode='HTML')
        
    elif text in ['📲 Telegram']:
        session['data']['contact_method'] = 'telegram'
        session['stage'] = 'telegram_input'
        
        if lang == 'ru':
            msg = "📲 <b>Telegram</b>\n\nВведите ваш @username в Telegram:"
        else:
            msg = "📲 <b>Telegram</b>\n\nEnter your @username in Telegram:"
        
        send_message(chat_i
