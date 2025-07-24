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
    """Отправка сообщения - упрощенная версия"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if reply_markup:
        payload['reply_markup'] = reply_markup
    
    print(f"Sending message to {chat_id}: {text[:50]}...")  # Отладка
    if reply_markup:
        print(f"With keyboard: {reply_markup}")
    
    response = requests.post(url, json=payload)  # Используем json=payload
    print(f"Response status: {response.status_code}")
    return response

def create_keyboard(buttons, resize=True):
    """Создание inline клавиатуры - упрощенная версия"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            keyboard_row.append({'text': btn[0], 'callback_data': btn[1]})
        keyboard.append(keyboard_row)
    
    return {'inline_keyboard': keyboard}

def validate_budget(text):
    """Свободный формат бюджета - принимаем любой текст"""
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
        elif any(x in budget for x in ['3m', '4m', '5m', '3-4', '4-5', '5m']):
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
        
        return recommendations[:3]  # Максимум 3 рекомендации
    except Exception as e:
        print(f"Error in AI recommendations: {str(e)}")
        return ["📍 <b>Подберем варианты</b> под ваши критерии"]

def handle_start(chat_id, user_id):
    """Обработка команды /start"""
    # Очищаем предыдущую сессию при /start
    user_sessions[user_id] = {'state': STATES['LANGUAGE_SELECT']}
    
    keyboard = create_keyboard([
        [('🇷🇺 Русский', 'lang_ru'), ('🇬🇧 English', 'lang_en')]
    ])
    
    send_message(chat_id, 
        "Выберите язык / Choose language:", 
        reply_markup=keyboard)

def handle_language_select(chat_id, user_id, data):
    """Выбор языка"""
    if data == 'lang_ru':
        user_sessions[user_id]['language'] = 'ru'
        user_sessions[user_id]['state'] = STATES['ROLE_SELECT']
        
        keyboard = create_keyboard([
            [('🏠 Жить', 'role_live')],
            [('📈 Инвестировать', 'role_invest')],
            [('🔄 Продать/Сдать', 'role_owner')],
            [('🎯 Смешанный', 'role_mixed')]
        ])
        
        send_message(chat_id,
            "<b>Иван, цифровой напарник в эфире</b>.\n\n"
            "Хочу услышать твой текущий фокус:",
            reply_markup=keyboard)

def handle_role_select(chat_id, user_id, data):
    """Выбор роли"""
    try:
        # Проверяем наличие сессии
        if user_id not in user_sessions:
            send_message(chat_id, "Сессия потеряна. Используйте /start")
            return
            
        session = user_sessions[user_id]
        
        role_map = {
            'role_live': 'live',
            'role_invest': 'invest', 
            'role_owner': 'owner',
            'role_mixed': 'mixed'
        }
        
        session['role'] = role_map.get(data, 'live')
        
        print(f"Role saved: {session['role']}")  # Отладка
        print(f"Session after role: {session}")  # Отладка
        
        # Владельцы идут по отдельной ветке (уже реализовано в Этапе 2)
        if session['role'] == 'owner':
            handle_owner_flow(chat_id, user_id)
            return
        
        # Покупатели/инвесторы идут на сбор бюджета
        session['state'] = STATES['BUDGET_INPUT']
        
        send_message(chat_id,
            "Каков ориентир по бюджету?\n\n"
            "<i>Диапазон (например: 3-4M AED)</i>")
            
    except Exception as e:
        print(f"Error in handle_role_select: {str(e)}")
        print(f"Data received: {data}")
        send_message(chat_id, "Ошибка выбора роли. Используйте /start")

def handle_budget_input(chat_id, user_id, text):
    """Обработка ввода бюджета - свободный формат"""
    try:
        # Проверяем наличие сессии
        if user_id not in user_sessions:
            send_message(chat_id, "Сессия потеряна. Используйте /start")
            return
            
        budget = validate_budget(text)
        
        if not budget:
            send_message(chat_id, "Пожалуйста, укажите ваш бюджет")
            return
        
        session = user_sessions[user_id]
        session['budget'] = budget
        session['state'] = STATES['PRIORITY_SELECT']
        
        print(f"Budget saved: {session['budget']}")  # Отладка
        print(f"Session after budget: {session}")  # Отладка
        
        keyboard = create_keyboard([
            [('🌊 Утро у воды', 'priority_water')],
            [('🏙️ Доступ к центру', 'priority_city')],
            [('⚖️ Баланс', 'priority_balance')]
        ])
        
        send_message(chat_id,
            "Важнее утро у воды или скорость доступа к центру?",
            reply_markup=keyboard)
            
    except Exception as e:
        print(f"Error in handle_budget_input: {str(e)}")
        print(f"Text received: {text}")
        send_message(chat_id, "Ошибка обработки бюджета. Используйте /start")

def handle_priority_select(chat_id, user_id, data):
    """Выбор приоритета"""
    try:
        # Проверяем наличие сессии
        if user_id not in user_sessions:
            send_message(chat_id, "Сессия потеряна. Используйте /start")
            return
            
        session = user_sessions[user_id]
        
        priority_map = {
            'priority_water': 'water_mornings',
            'priority_city': 'city_access',
            'priority_balance': 'balance'
        }
        
        # Сохраняем приоритет в сессии
        session['priority_mood'] = priority_map.get(data, 'balance')
        session['state'] = STATES['HORIZON_SELECT']
        
        print(f"Priority saved: {session['priority_mood']}")  # Отладка
        print(f"Session after priority: {session}")  # Отладка
        
        keyboard = create_keyboard([
            [('1 месяц', 'horizon_1'), ('3 месяца', 'horizon_3')],
            [('6 месяцев', 'horizon_6'), ('больше 6', 'horizon_6plus')]
        ])
        
        send_message(chat_id,
            "Какой горизонт планирования — месяцев до решения?",
            reply_markup=keyboard)
            
    except Exception as e:
        print(f"Error in handle_priority_select: {str(e)}")
        print(f"Data received: {data}")
        send_message(chat_id, "Ошибка выбора приоритета. Используйте /start")

def handle_horizon_select(chat_id, user_id, data):
    """Выбор горизонта планирования"""
    try:
        session = user_sessions.get(user_id, {})
        
        horizon_map = {
            'horizon_1': 1,
            'horizon_3': 3,
            'horizon_6': 6,
            'horizon_6plus': 12
        }
        
        session['horizon_months'] = horizon_map.get(data, 3)
        session['state'] = STATES['PROFILE_CONFIRM']
        
        # Генерируем AI рекомендации
        profile = {
            'budget': session.get('budget', ''),
            'priority_mood': session.get('priority_mood', ''),
            'role': session.get('role', 'live')  # дефолт значение
        }
        
        print(f"Profile for AI: {profile}")  # Отладка
        
        recommendations = get_ai_recommendations(profile)
        
        # Формируем сводку профиля
        role_names = {
            'live': 'Жить',
            'invest': 'Инвестировать', 
            'mixed': 'Смешанный',
            'owner': 'Продать/Сдать'
        }
        
        priority_names = {
            'water_mornings': 'Утро у воды',
            'city_access': 'Доступ к центру',
            'balance': 'Баланс'
        }
        
        # Безопасное получение данных с дефолтами
        user_role = session.get('role', 'неизвестно')
        user_budget = session.get('budget', 'не указан')
        user_priority = session.get('priority_mood', 'не выбран')
        user_horizon = session.get('horizon_months', 3)
        
        summary = (
            f"<b>📋 Твой профиль:</b>\n"
            f"• Цель: {role_names.get(user_role, user_role)}\n"
            f"• Бюджет: {user_budget}\n"
            f"• Приоритет: {priority_names.get(user_priority, user_priority)}\n"
            f"• Горизонт: {user_horizon} мес\n\n"
            f"<b>🎯 AI рекомендации:</b>\n"
        )
        
        for rec in recommendations:
            summary += f"{rec}\n"
        
        summary += "\nГотов фиксировать профиль?"
        
        keyboard = create_keyboard([
            [('✅ Фиксировать', 'profile_confirm')],
            [('🔄 Ещё вопрос', 'profile_edit')]
        ])
        
        send_message(chat_id, summary, reply_markup=keyboard)
        
    except Exception as e:
        print(f"Error in handle_horizon_select: {str(e)}")
        print(f"Session data: {user_sessions.get(user_id, {})}")
        print(f"Data received: {data}")
        # Попробуем восстановить сессию
        if user_id in user_sessions:
            send_message(chat_id, "Что-то пошло не так. Попробуйте еще раз или /start")
        else:
            send_message(chat_id, "Сессия потеряна. Используйте /start")

def handle_profile_confirm(chat_id, user_id, data):
    """Подтверждение профиля"""
    session = user_sessions[user_id]
    
    if data == 'profile_confirm':
        # Переходим к сбору контактов
        session['state'] = STATES['CONTACT_CHANNEL']
        
        keyboard = create_keyboard([
            [('📱 Телефон', 'contact_phone')],
            [('📧 Email', 'contact_email')],
            [('✈️ Telegram @ник', 'contact_tg')]
        ])
        
        send_message(chat_id,
            "Как связаться удобнее?",
            reply_markup=keyboard)
    
    elif data == 'profile_edit':
        # Возвращаемся к выбору роли
        session['state'] = STATES['ROLE_SELECT']
        handle_role_select(chat_id, user_id, f"role_{session['role']}")

def handle_contact_channel(chat_id, user_id, data):
    """Выбор канала связи"""
    session = user_sessions[user_id]
    session['contact_method'] = data.replace('contact_', '')
    
    if data == 'contact_phone':
        session['state'] = STATES['PHONE_INPUT']
        send_message(chat_id,
            "Введи номер в международном формате:\n"
            "<i>+9715xxxxxxx (9-15 цифр)</i>")
    
    elif data == 'contact_email':
        session['state'] = STATES['EMAIL_INPUT']
        send_message(chat_id,
            "Оставь email для документов:\n"
            "<i>name@mail.com</i>")
    
    elif data == 'contact_tg':
        session['state'] = STATES['TG_INPUT']
        send_message(chat_id,
            "Напиши @username для связи в ТГ:\n"
            "<i>@username (5-32 символов)</i>")

def handle_contact_input(chat_id, user_id, text):
    """Обработка ввода контактных данных"""
    session = user_sessions[user_id]
    state = session['state']
    
    if state == STATES['PHONE_INPUT']:
        if validate_phone(text):
            session['phone'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id,
                "Похоже, цифр мало/много. Повторим?\n"
                "<i>Формат: +9715xxxxxxx</i>")
    
    elif state == STATES['EMAIL_INPUT']:
        if validate_email(text):
            session['email'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id,
                "Формат письма другой. Пример:\n"
                "<i>name@mail.com</i>")
    
    elif state == STATES['TG_INPUT']:
        if validate_telegram(text):
            session['telegram'] = text
            finalize_contact(chat_id, user_id)
        else:
            send_message(chat_id,
                "Нужен формат @username (5-32 символов)")

def finalize_contact(chat_id, user_id):
    """Финализация контактных данных"""
    session = user_sessions[user_id]
    session['state'] = STATES['CONTACT_CONFIRM']
    
    contact_info = "Фиксирую:\n"
    if 'phone' in session:
        contact_info += f"📱 Телефон: {session['phone']}\n"
    if 'email' in session:
        contact_info += f"📧 Email: {session['email']}\n"
    if 'telegram' in session:
        contact_info += f"✈️ TG: {session['telegram']}\n"
    
    contact_info += "\nПередать профиль брокеру?"
    
    keyboard = create_keyboard([
        [('✅ Да', 'contact_send')],
        [('📝 Исправить', 'contact_edit')]
    ])
    
    send_message(chat_id, contact_info, reply_markup=keyboard)

def handle_contact_confirm(chat_id, user_id, data):
    """Подтверждение отправки контактов"""
    session = user_sessions[user_id]
    
    if data == 'contact_send':
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
        session['state'] = STATES['READY']
        
        # Отправляем уведомление админу
        admin_message = (
            f"🔥 <b>Новая заявка!</b>\n\n"
            f"👤 User ID: {user_id}\n"
            f"🎯 Цель: {profile['role']}\n"
            f"💰 Бюджет: {profile['budget']}\n"
            f"⭐ Приоритет: {profile['priority_mood']}\n"
            f"📅 Горизонт: {profile['horizon_months']} мес\n\n"
            f"📞 Контакт:\n"
        )
        
        if profile['phone']:
            admin_message += f"📱 {profile['phone']}\n"
        if profile['email']:
            admin_message += f"📧 {profile['email']}\n"
        if profile['telegram']:
            admin_message += f"✈️ {profile['telegram']}\n"
        
        send_message(ADMIN_ID, admin_message)
        
        # Подтверждение пользователю
        send_message(chat_id,
            "✅ <b>Готово!</b>\n\n"
            "Профиль передан брокеру. Человек свяжется в указанное окно.\n\n"
            "Я рядом, если появится новый сигнал. /start для нового запроса.")
    
    elif data == 'contact_edit':
        # Возвращаемся к выбору канала связи
        session['state'] = STATES['CONTACT_CHANNEL']
        handle_contact_channel(chat_id, user_id, f"contact_{session['contact_method']}")

def handle_owner_flow(chat_id, user_id):
    """Обработка ветки владельца (заглушка - уже реализовано в Этапе 2)"""
    send_message(chat_id,
        "🏠 <b>Владелец недвижимости</b>\n\n"
        "Эта ветка уже реализована в Этапе 2.\n"
        "Для тестирования выберите другую роль.")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Основной webhook для обработки сообщений"""
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Отладка
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '')
            
            # Команда /start
            if text == '/start':
                handle_start(chat_id, user_id)
                return jsonify({'ok': True})
            
            # Игнорируем команды без состояния
            if text.startswith('/') and user_id not in user_sessions:
                handle_start(chat_id, user_id)
                return jsonify({'ok': True})
            
            # Получаем состояние пользователя
            session = user_sessions.get(user_id, {})
            state = session.get('state', STATES['LANGUAGE_SELECT'])
            
            # Обработка текстового ввода по состояниям
            if state == STATES['BUDGET_INPUT']:
                handle_budget_input(chat_id, user_id, text)
            elif state in [STATES['PHONE_INPUT'], STATES['EMAIL_INPUT'], STATES['TG_INPUT']]:
                handle_contact_input(chat_id, user_id, text)
            else:
                # Если нет сессии - предлагаем старт
                if user_id not in user_sessions:
                    send_message(chat_id, "Используйте /start для начала")
                else:
                    # Неизвестное состояние - показываем текущий статус
                    send_message(chat_id, f"Используйте кнопки выше или /start для перезапуска")
        
        elif 'callback_query' in data:
            query = data['callback_query']
            chat_id = query['message']['chat']['id']
            user_id = query['from']['id']
            callback_data = query['data']
            message_id = query['message']['message_id']
            
            # ДОБАВИТЬ ЭТИ СТРОКИ:
            print(f"=== CALLBACK DEBUG ===")
            print(f"User: {user_id}")
            print(f"Data: {callback_data}")
            print(f"Session: {user_sessions.get(user_id, 'NO SESSION')}")
            print(f"=== END DEBUG ===")
            
            # Отвечаем на callback_query чтобы убрать "часики"
            requests.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", 
                         data={'callback_query_id': query['id']})
            
            # Если нет сессии - создаем новую для callback'ов выбора языка
            if user_id not in user_sessions and callback_data.startswith('lang_'):
                user_sessions[user_id] = {'state': STATES['LANGUAGE_SELECT']}
            elif user_id not in user_sessions:
                send_message(chat_id, "Сессия истекла. Используйте /start")
                return jsonify({'ok': True})
            
            # Получаем состояние пользователя
            session = user_sessions[user_id]
            state = session.get('state', STATES['LANGUAGE_SELECT'])
            
            print(f"Current state: {state}")  # Отладка
            
            # Роутинг по callback_data (не зависит от состояния)
            try:
                if callback_data.startswith('lang_'):
                    handle_language_select(chat_id, user_id, callback_data)
                elif callback_data.startswith('role_'):
                    handle_role_select(chat_id, user_id, callback_data)
                elif callback_data.startswith('priority_'):
                    handle_priority_select(chat_id, user_id, callback_data)
                elif callback_data.startswith('horizon_'):
                    handle_horizon_select(chat_id, user_id, callback_data)
                elif callback_data.startswith('profile_'):
                    handle_profile_confirm(chat_id, user_id, callback_data)
                elif callback_data.startswith('contact_'):
                    if state == STATES['CONTACT_CHANNEL']:
                        handle_contact_channel(chat_id, user_id, callback_data)
                    elif state == STATES['CONTACT_CONFIRM']:
                        handle_contact_confirm(chat_id, user_id, callback_data)
                    else:
                        print(f"Contact callback in wrong state: {state}")
                else:
                    print(f"Unknown callback: {callback_data}")
                    # НЕ отправляем сообщение пользователю для неизвестных callback'ов
            except Exception as e:
                print(f"Error in callback handling: {str(e)}")
                print(f"Callback data: {callback_data}")
                print(f"User session: {session}")
                # НЕ отправляем сообщение об ошибке пользователю
        
        return jsonify({'ok': True})
    
    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        print(f"Request data: {request.get_json()}")  # Отладка ошибок
        return jsonify({'error': str(e)}), 200  # Возвращаем 200 чтобы Telegram не повторял

@app.route('/')
def home():
    return "Telegram Bot UAE - Stage 3 Ready!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
