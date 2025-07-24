import os
import json
import re
from datetime import datetime
import pytz
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Конфигурация
TELEGRAM_TOKEN = "8074002738:AAGNAAHE9sdUDRl7EVwLGYYPrnZK48cxBf4"
ADMIN_ID = 367380234
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Хранение данных в памяти
user_sessions = {}
user_profiles = {}

# Константы для состояний
STATES = {
    'LANGUAGE_SELECT': 'language_select',
    'ROLE_SELECT': 'role_select',
    'BUDGET_INPUT': 'budget_input',
    'PRIORITY_SELECT': 'priority_select',
    'HORIZON_SELECT': 'horizon_select',
    'PROFILE_CONFIRM': 'profile_confirm',
    'CONTACT_CHANNEL': 'contact_channel',
    'PHONE_INPUT': 'phone_input',
    'EMAIL_INPUT': 'email_input',
    'TG_INPUT': 'tg_input',
    'CONTACT_CONFIRM': 'contact_confirm',
    'READY': 'ready'
}

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения с reply клавиатурой"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    print(f"Sending to {chat_id}: {text[:50]}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Response: {response.status_code}")
        return response
    except Exception as e:
        print(f"Send message error: {e}")
        return None

def create_reply_keyboard(buttons, one_time=True):
    """Создание reply клавиатуры"""
    return {
        'keyboard': buttons,
        'resize_keyboard': True,
        'one_time_keyboard': one_time
    }

def remove_keyboard():
    """Убрать клавиатуру"""
    return {'remove_keyboard': True}

def validate_budget(text):
    """Валидация бюджета - принимаем любой текст"""
    return text.strip() if text.strip() else None

def validate_phone(text):
    """Валидация телефона"""
    pattern = r'^\+?\d{9,15}$'
    return re.match(pattern, text.replace(' ', '').replace('-', ''))

def validate_email(text):
    """Валидация email"""
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, text)

def validate_telegram(text):
    """Валидация Telegram username"""
    if not text.startswith('@'):
        text = '@' + text
    pattern = r'^@[A-Za-z0-9_]{5,32}$'
    return re.match(pattern, text)

def get_ai_recommendations(profile):
    """AI рекомендации на основе профиля"""
    try:
        budget = profile.get('budget', '').lower()
        priority = profile.get('priority_mood', '')
        
        recommendations = []
        
        # Анализ по бюджету
        if any(x in budget for x in ['1m', '2m', '1-2', '2-3']):
            recommendations.append("📍 <b>JVC, Dubai Sports City</b> - отличная стартовая позиция")
            recommendations.append("📍 <b>Dubai Marina (студии)</b> - городская энергия")
        elif any(x in budget for x in ['3m', '4m', '5m', '3-4', '4-5']):
            recommendations.append("📍 <b>Palm Jumeirah (восточная дуга)</b> - утренний свет + вода")
            recommendations.append("📍 <b>Dubai Marina (1-2BR)</b> - центральная локация")
            recommendations.append("📍 <b>Business Bay</b> - динамика + инвестпотенциал")
        else:
            recommendations.append("📍 <b>Palm Jumeirah (премиум)</b> - прямой выход к воде")
            recommendations.append("📍 <b>DIFC, Downtown</b> - центр финансов + культуры")
            recommendations.append("📍 <b>Bluewaters</b> - новый уровень комфорта")
        
        # Анализ по приоритетам
        if priority == 'water_mornings':
            recommendations.append("🌊 <b>Фокус на восточные виды</b> - Palm, Marina east")
        elif priority == 'city_access':
            recommendations.append("🏙️ <b>Транспортные узлы</b> - Metro line, Sheikh Zayed Road")
        else:  # balance
            recommendations.append("⚖️ <b>Золотая середина</b> - Business Bay, JLT")
        
        return recommendations[:3]
    except Exception as e:
        print(f"Error in AI recommendations: {e}")
        return ["📍 <b>Подберем варианты</b> под ваши критерии"]

# === ОБРАБОТЧИКИ СОСТОЯНИЙ ===

def handle_start(chat_id, user_id):
    """Начало работы - выбор языка"""
    user_sessions[user_id] = {'state': STATES['LANGUAGE_SELECT']}
    
    keyboard = create_reply_keyboard([
        ['🇷🇺 Русский', '🇬🇧 English']
    ])
    
    send_message(chat_id, "Выберите язык / Choose language:", reply_markup=keyboard)

def handle_language_select(chat_id, user_id, text):
    """Обработка выбора языка"""
    print(f"Language select: user={user_id}, text={text}")
    
    # ВАЖНО: работаем напрямую с user_sessions
    if user_id not in user_sessions:
        user_sessions[user_id] = {'state': STATES['LANGUAGE_SELECT']}
    
    if text == '🇷🇺 Русский':
        user_sessions[user_id]['language'] = 'ru'
        user_sessions[user_id]['state'] = STATES['ROLE_SELECT']
        
        print(f"Updated session: {user_sessions[user_id]}")
        
        keyboard = create_reply_keyboard([
            ['🏠 Жить'],
            ['📈 Инвестировать'],
            ['🔄 Продать/Сдать'],
            ['🎯 Смешанный']
        ])
        
        send_message(chat_id,
            "<b>Иван, цифровой напарник в эфире</b>.\n\n"
            "Хочу услышать твой текущий фокус:",
            reply_markup=keyboard)
        return True
    
    elif text == '🇬🇧 English':
        send_message(chat_id, "English version coming soon. Use 🇷🇺 Русский for now.")
        return True
    
    return False

def handle_role_select(chat_id, user_id, text):
    """Обработка выбора роли"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {'state': STATES['ROLE_SELECT']}
    
    role_map = {
        '🏠 Жить': 'live',
        '📈 Инвестировать': 'invest',
        '🔄 Продать/Сдать': 'owner',
        '🎯 Смешанный': 'mixed'
    }
    
    if text not in role_map:
        return False
    
    user_sessions[user_id]['role'] = role_map[text]
    
    if user_sessions[user_id]['role'] == 'owner':
        send_message(chat_id, "🏠 Ветка владельца в разработке. Выберите другую роль.", 
                    reply_markup=create_reply_keyboard([
                        ['🏠 Жить'], ['📈 Инвестировать'], ['🎯 Смешанный']
                    ]))
        return True
    
    # Переходим к сбору бюджета
    user_sessions[user_id]['state'] = STATES['BUDGET_INPUT']
    
    send_message(chat_id,
        "Каков ориентир по бюджету?\n\n"
        "<i>Любой формат: 3-4M AED, 5М, 2.5 миллиона и т.д.</i>",
        reply_markup=remove_keyboard())
    
    return True

def handle_budget_input(chat_id, user_id, text):
    """Обработка ввода бюджета"""
    budget = validate_budget(text)
    
    if not budget:
        send_message(chat_id, "Пожалуйста, укажите ваш бюджет")
        return
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    user_sessions[user_id]['budget'] = budget
    user_sessions[user_id]['state'] = STATES['PRIORITY_SELECT']
    
    keyboard = create_reply_keyboard([
        ['🌊 Утро у воды'],
        ['🏙️ Доступ к центру'],
        ['⚖️ Баланс']
    ])
    
    send_message(chat_id,
        "Важнее утро у воды или скорость доступа к центру?",
        reply_markup=keyboard)

def handle_priority_select(chat_id, user_id, text):
    """Обработка выбора приоритета"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    priority_map = {
        '🌊 Утро у воды': 'water_mornings',
        '🏙️ Доступ к центру': 'city_access',
        '⚖️ Баланс': 'balance'
    }
    
    if text not in priority_map:
        return False
    
    user_sessions[user_id]['priority_mood'] = priority_map[text]
    user_sessions[user_id]['state'] = STATES['HORIZON_SELECT']
    
    keyboard = create_reply_keyboard([
        ['1 месяц', '3 месяца'],
        ['6 месяцев', 'больше 6']
    ])
    
    send_message(chat_id,
        "Какой горизонт планирования — месяцев до решения?",
        reply_markup=keyboard)
    
    return True

def handle_horizon_select(chat_id, user_id, text):
    """Обработка выбора горизонта"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    horizon_map = {
        '1 месяц': 1,
        '3 месяца': 3,
        '6 месяцев': 6,
        'больше 6': 12
    }
    
    if text not in horizon_map:
        return False
    
    user_sessions[user_id]['horizon_months'] = horizon_map[text]
    user_sessions[user_id]['state'] = STATES['PROFILE_CONFIRM']
    
    # Показываем профиль с рекомендациями
    show_profile_summary(chat_id, user_id)
    return True

def show_profile_summary(chat_id, user_id):
    """Показать сводку профиля с AI рекомендациями"""
    session = user_sessions.get(user_id, {})
    
    # Генерируем AI рекомендации
    profile = {
        'budget': session.get('budget', ''),
        'priority_mood': session.get('priority_mood', ''),
        'role': session.get('role', 'live')
    }
    
    recommendations = get_ai_recommendations(profile)
    
    # Формируем сводку
    role_names = {
        'live': 'Жить',
        'invest': 'Инвестировать',
        'mixed': 'Смешанный'
    }
    
    priority_names = {
        'water_mornings': 'Утро у воды',
        'city_access': 'Доступ к центру',
        'balance': 'Баланс'
    }
    
    summary = (
        f"<b>📋 Твой профиль:</b>\n"
        f"• Цель: {role_names.get(session.get('role'), session.get('role', 'неизвестно'))}\n"
        f"• Бюджет: {session.get('budget', 'не указан')}\n"
        f"• Приоритет: {priority_names.get(session.get('priority_mood'), session.get('priority_mood', 'не выбран'))}\n"
        f"• Горизонт: {session.get('horizon_months', 3)} мес\n\n"
        f"<b>🎯 AI рекомендации:</b>\n"
    )
    
    for rec in recommendations:
        summary += f"{rec}\n"
    
    summary += "\nГотов фиксировать профиль?"
    
    keyboard = create_reply_keyboard([
        ['✅ Фиксировать'],
        ['🔄 Изменить данные']
    ])
    
    send_message(chat_id, summary, reply_markup=keyboard)

def handle_profile_confirm(chat_id, user_id, text):
    """Обработка подтверждения профиля"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    if text == '✅ Фиксировать':
        user_sessions[user_id]['state'] = STATES['CONTACT_CHANNEL']
        
        keyboard = create_reply_keyboard([
            ['📱 Телефон'],
            ['📧 Email'],
            ['✈️ Telegram']
        ])
        
        send_message(chat_id, "Как удобнее связаться?", reply_markup=keyboard)
        return True
    
    elif text == '🔄 Изменить данные':
        # Возвращаемся к выбору роли
        user_sessions[user_id]['state'] = STATES['ROLE_SELECT']
        
        keyboard = create_reply_keyboard([
            ['🏠 Жить'],
            ['📈 Инвестировать'],
            ['🎯 Смешанный']
        ])
        
        send_message(chat_id, "Выберите роль заново:", reply_markup=keyboard)
        return True
    
    return False

def handle_contact_channel(chat_id, user_id, text):
    """Обработка выбора канала связи"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    if text == '📱 Телефон':
        user_sessions[user_id]['contact_method'] = 'phone'
        user_sessions[user_id]['state'] = STATES['PHONE_INPUT']
        send_message(chat_id, 
            "Введите номер в международном формате:\n"
            "<i>+9715xxxxxxx (9-15 цифр)</i>",
            reply_markup=remove_keyboard())
    
    elif text == '📧 Email':
        user_sessions[user_id]['contact_method'] = 'email'
        user_sessions[user_id]['state'] = STATES['EMAIL_INPUT']
        send_message(chat_id,
            "Введите email для документов:\n"
            "<i>name@mail.com</i>",
            reply_markup=remove_keyboard())
    
    elif text == '✈️ Telegram':
        user_sessions[user_id]['contact_method'] = 'telegram'
        user_sessions[user_id]['state'] = STATES['TG_INPUT']
        send_message(chat_id,
            "Введите @username для связи:\n"
            "<i>@username (5-32 символов)</i>",
            reply_markup=remove_keyboard())
    else:
        return False
    
    return True

def handle_contact_input(chat_id, user_id, text):
    """Обработка ввода контактных данных"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    state = session.get('state')
    
    if state == STATES['PHONE_INPUT']:
        if validate_phone(text):
            user_sessions[user_id]['phone'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id, "Неверный формат. Попробуйте: +9715xxxxxxx")
    
    elif state == STATES['EMAIL_INPUT']:
        if validate_email(text):
            user_sessions[user_id]['email'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id, "Неверный формат. Пример: name@mail.com")
    
    elif state == STATES['TG_INPUT']:
        if validate_telegram(text):
            user_sessions[user_id]['telegram'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id, "Неверный формат. Нужно: @username")

def finalize_contact(chat_id, user_id):
    """Финализация контактных данных"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    user_sessions[user_id]['state'] = STATES['CONTACT_CONFIRM']
    session = user_sessions[user_id]
    
    contact_info = "Проверьте контакт:\n"
    if 'phone' in session:
        contact_info += f"📱 {session['phone']}\n"
    if 'email' in session:
        contact_info += f"📧 {session['email']}\n"
    if 'telegram' in session:
        contact_info += f"✈️ {session['telegram']}\n"
    
    contact_info += "\nОтправить профиль брокеру?"
    
    keyboard = create_reply_keyboard([
        ['✅ Отправить'],
        ['🔄 Исправить']
    ])
    
    send_message(chat_id, contact_info, reply_markup=keyboard)

def handle_contact_confirm(chat_id, user_id, text):
    """Подтверждение отправки"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    session = user_sessions[user_id]
    
    if text == '✅ Отправить':
        # Сохраняем профиль
        profile = {
            'user_id': user_id,
            'timestamp': datetime.now(pytz.UTC).isoformat(),
            'language': session.get('language', 'ru'),
            'role': session.get('role', ''),
            'budget': session.get('budget', ''),
            'priority_mood': session.get('priority_mood', ''),
            'horizon_months': session.get('horizon_months', 3),
            'phone': session.get('phone', ''),
            'email': session.get('email', ''),
            'telegram': session.get('telegram', ''),
            'contact_method': session.get('contact_method', '')
        }
        
        user_profiles[user_id] = profile
        user_sessions[user_id]['state'] = STATES['READY']
        
        # Отправляем админу
        admin_message = (
            f"🔥 <b>Новая заявка!</b>\n\n"
            f"👤 User: {user_id}\n"
            f"🎯 Цель: {profile['role']}\n"
            f"💰 Бюджет: {profile['budget']}\n"
            f"⭐ Приоритет: {profile['priority_mood']}\n"
            f"📅 Горизонт: {profile['horizon_months']} мес\n\n"
            f"📞 Контакт:\n"
        )
        
        if profile.get('phone'):
            admin_message += f"📱 {profile['phone']}\n"
        if profile.get('email'):
            admin_message += f"📧 {profile['email']}\n"
        if profile.get('telegram'):
            admin_message += f"✈️ {profile['telegram']}\n"
        
        send_message(ADMIN_ID, admin_message)
        
        # Подтверждение пользователю
        send_message(chat_id,
            "✅ <b>Готово!</b>\n\n"
            "Профиль передан брокеру. Свяжемся в указанное время.\n\n"
            "Для нового запроса: /start",
            reply_markup=remove_keyboard())
        
        return True
    
    elif text == '🔄 Исправить':
        # Возвращаемся к выбору канала
        user_sessions[user_id]['state'] = STATES['CONTACT_CHANNEL']
        
        keyboard = create_reply_keyboard([
            ['📱 Телефон'],
            ['📧 Email'],
            ['✈️ Telegram']
        ])
        
        send_message(chat_id, "Как удобнее связаться?", reply_markup=keyboard)
        return True
    
    return False

# === ОСНОВНОЙ WEBHOOK ===

@app.route('/webhook', methods=['POST'])
def webhook():
    """Главный обработчик сообщений"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '')
            
            print(f"Message from {user_id}: {text}")
            
            # Команда /start всегда работает
            if text == '/start':
                handle_start(chat_id, user_id)
                return jsonify({'ok': True})
            
            # Получаем текущее состояние
            session = user_sessions.get(user_id, {})
            state = session.get('state', STATES['LANGUAGE_SELECT'])
            
            print(f"Current state for {user_id}: {state}")
            
            # Роутинг по состояниям
            handled = False
            
            if state == STATES['LANGUAGE_SELECT']:
                handled = handle_language_select(chat_id, user_id, text)
            
            elif state == STATES['ROLE_SELECT']:
                handled = handle_role_select(chat_id, user_id, text)
            
            elif state == STATES['BUDGET_INPUT']:
                handle_budget_input(chat_id, user_id, text)
                handled = True
            
            elif state == STATES['PRIORITY_SELECT']:
                handled = handle_priority_select(chat_id, user_id, text)
            
            elif state == STATES['HORIZON_SELECT']:
                handled = handle_horizon_select(chat_id, user_id, text)
            
            elif state == STATES['PROFILE_CONFIRM']:
                handled = handle_profile_confirm(chat_id, user_id, text)
            
            elif state == STATES['CONTACT_CHANNEL']:
                handled = handle_contact_channel(chat_id, user_id, text)
            
            elif state in [STATES['PHONE_INPUT'], STATES['EMAIL_INPUT'], STATES['TG_INPUT']]:
                handle_contact_input(chat_id, user_id, text)
                handled = True
            
            elif state == STATES['CONTACT_CONFIRM']:
                handled = handle_contact_confirm(chat_id, user_id, text)
            
            if not handled:
                # Показываем текущее состояние для отладки
                session_debug = user_sessions.get(user_id, "NO SESSION")
                send_message(chat_id, 
                    f"Не понял '{text}'. Используйте кнопки выше или /start\n\n"
                    f"<i>Debug: state={state}, session={session_debug}</i>")
        
        return jsonify({'ok': True})
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 200

@app.route('/')
def home():
    return "🤖 UAE Property Bot - Full Working Version!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
