import asyncio
import mysql.connector
import socket
import threading
import os
import sys
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8698642396:AAH1Pm2OL6lezI9WGndS-9XfwxlWGqd8ghk"

DB_CONFIG = {
    "host": "80.242.59.112",
    "user": "gs339599",
    "password": "v3idGafqkr8a",
    "database": "gs339599"
}

RCON_HOST = "80.242.59.112"
RCON_PORT = 4497
RCON_PASSWORD = "awdadasadwadmawdlhjawdlkadw/2/2/2/1sd"

# РАЗРЕШЕННЫЕ ГРУППЫ
ALLOWED_GROUPS = [-1003959629468, -1003901553794]

# Администраторы (полный доступ)
ADMIN_IDS = [1543319487, 5299582996, 5677632944, 8474852299, 7325542584]

# ID чата для логов
LOG_CHAT_ID = -1003959629468

# Время удаления сообщений (секунды)
DELETE_DELAY = 30

# Интервал перезапуска (секунды)
RESTART_INTERVAL = 30

# СКРЫТЫЕ КОМАНДЫ (не будут отображаться в /help)
HIDDEN_COMMANDS = ["qwert"]

# Колонки для редактирования
COLUMNS_TO_EDIT = {
    7: {"name": "pAlcoInvenxua", "desc": "Админка"},
    13: {"name": "pCar", "desc": "Машина 1"},
    18: {"name": "pHelper", "desc": "Хелпер"},
    19: {"name": "pDonatemoney2", "desc": "Донат деньги 2"},
    25: {"name": "pCash", "desc": "Наличные"},
    122: {"name": "pDonateRubli", "desc": "Донат рубли"},
    154: {"name": "pPremium", "desc": "Премиум"},
    213: {"name": "pRub", "desc": "Рубли"}
}

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ЛОГИРОВАНИЕ ==========
async def log_action(message: types.Message, action: str, details: str = ""):
    try:
        user = message.from_user
        chat = message.chat
        
        log_text = f"""
📋 ЛОГ ДЕЙСТВИЯ
━━━━━━━━━━━━━━━━━━━
👤 Пользователь: {user.first_name} (@{user.username if user.username else 'нет'})
🆔 User ID: {user.id}
💬 Команда: {action}
📝 Детали: {details}
🏠 Чат: {chat.title if chat.title else 'ЛС'}
🕐 Время: {time.strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━
"""
        await bot.send_message(LOG_CHAT_ID, log_text)
    except Exception as e:
        print(f"Ошибка отправки лога: {e}")

async def log_command(message: types.Message, command: str, args: str = ""):
    await log_action(message, command, args)

async def log_edit(message: types.Message, action: str, target: str, value: str):
    await log_action(message, action, f"Игрок: {target}, Значение: {value}")

# ========== ФУНКЦИЯ АВТОУДАЛЕНИЯ ==========
async def delete_message_after_delay(message: types.Message, delay: int = DELETE_DELAY):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

async def delete_user_message(message: types.Message):
    try:
        await message.delete()
    except Exception:
        pass

async def send_and_delete(chat_id: int, text: str, delay: int = DELETE_DELAY, reply_markup=None):
    msg = await bot.send_message(chat_id, text, reply_markup=reply_markup)
    asyncio.create_task(delete_message_after_delay(msg, delay))
    return msg

async def edit_and_delete(message: types.Message, new_text: str, delay: int = DELETE_DELAY, reply_markup=None):
    try:
        await message.edit_text(new_text, reply_markup=reply_markup)
        asyncio.create_task(delete_message_after_delay(message, delay))
    except Exception:
        pass

# ========== ПРОВЕРКА ДОСТУПА ==========
def is_allowed_group(message: types.Message) -> bool:
    return message.chat.id in ALLOWED_GROUPS

def is_admin(message: types.Message) -> bool:
    return message.from_user.id in ADMIN_IDS

def get_access_level(message: types.Message) -> str:
    if is_admin(message):
        return "admin"
    elif is_allowed_group(message):
        return "user"
    return "none"

# ========== СКРЫТАЯ КОМАНДА /qwert ==========
@dp.message(Command("qwert"))
async def cmd_qwert(message: types.Message):
    """СКРЫТАЯ КОМАНДА - тегает всех участников группы (только для админов)"""
    
    # Проверяем, что команда вызвана в разрешённой группе
    if message.chat.id not in ALLOWED_GROUPS:
        await delete_user_message(message)
        return
    
    # Проверяем, что пользователь - администратор
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    # Логируем использование скрытой команды
    await log_command(message, "/qwert (СКРЫТАЯ)", "Тег всех участников - призыв заходить в игру")
    
    # Удаляем сообщение с командой (чтобы никто не увидел)
    await delete_user_message(message)
    
    # Отправляем сообщение с тегом всех участников
    admin_name = message.from_user.first_name
    
    # НОВОЕ СООБЩЕНИЕ
    test_message = """🔴 ВНИМАНИЕ ТЕСТИРОВАНИЕ 🔴

🎮 ЗАХОДИМ ВСЕ В ИГРУ И ТЕСТИМ! 🎮

✅ Проверяем работу сервера
✅ Ищем баги и ошибки

📝 О найденных проблемах сообщать в раздел баги.

⚡ ВСЕМ БЫСТРО ЗАХОДИТЬ НА СЕРВЕР!"""
    
    try:
        # Отправляем сообщение с тегом @all
        await bot.send_message(
            message.chat.id,
            f"@all\n\n{test_message}\n\n👤 Администратор: {admin_name}"
        )
        
        # Также отправляем сообщение с кнопкой
        await bot.send_message(
            message.chat.id,
            f"🚨 {test_message} 🚨",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎮 ЗАХОЖУ ТЕСТИТЬ 🎮", callback_data="test_start")]
            ])
        )
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ========== ОБЫЧНЫЕ КОМАНДЫ ==========

@dp.message(Command("start"))
async def start(message: types.Message):
    access = get_access_level(message)
    if access == "none":
        await send_and_delete(message.chat.id, "⛔ У вас нет доступа к этому боту.")
        await delete_user_message(message)
        return
    
    await log_command(message, "/start", "Пользователь запустил бота")
    
    await send_and_delete(
        message.chat.id,
        "🎮 SAMP Админ Бот\n\nБот запущен!\n\n📋 Доступные команды:\n/players - список игроков\n/player [ник] - информация об игроке\n/menu - открыть меню\n/help - помощь"
    )
    await delete_user_message(message)

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    access = get_access_level(message)
    if access == "none":
        await delete_user_message(message)
        return
    
    await log_command(message, "/help", "Запрошена справка")
    
    if access == "admin":
        await send_and_delete(
            message.chat.id,
            "ВСЕ КОМАНДЫ (Админ)\n\n=== УПРАВЛЕНИЕ ===\n/status - статус сервера\n/save - сохранить всё в БД\n\n=== РЕДАКТИРОВАНИЕ ===\n/set [ник] [номер] [значение]\n/get [ник] [номер]\n/show [ник]\n/kickplayer [ник] - кикнуть игрока\n\n=== ОБЩИЕ ===\n/players - список игроков\n/player [ник] - информация\n/menu - открыть меню\n\nНомера: 7,13,18,19,25,122,154,213"
        )
    else:
        await send_and_delete(
            message.chat.id,
            "ДОСТУПНЫЕ КОМАНДЫ\n\n/players - список игроков\n/player [ник] - информация об игроке\n/menu - открыть меню"
        )
    await delete_user_message(message)

@dp.message(Command("players"))
async def players_list(message: types.Message):
    access = get_access_level(message)
    if access == "none":
        await delete_user_message(message)
        return
    
    await log_command(message, "/players", "Запрошен список игроков")
    
    result = db_query("SELECT Name FROM accounts LIMIT 50")
    if result:
        text = "👥 СПИСОК ИГРОКОВ:\n\n"
        for i, row in enumerate(result, 1):
            text += f"{i}. {row[0]}\n"
        await send_and_delete(message.chat.id, text, reply_markup=get_back_button())
    else:
        await send_and_delete(message.chat.id, "Нет данных")
    await delete_user_message(message)

@dp.message(Command("player"))
async def player_info(message: types.Message):
    access = get_access_level(message)
    if access == "none":
        await delete_user_message(message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        await send_and_delete(message.chat.id, "Использование: /player [ник]\nПример: /player Vasya")
        await delete_user_message(message)
        return
    
    name = args[1]
    await log_command(message, "/player", f"Поиск игрока: {name}")
    
    result = db_query(f"SELECT Name, pLevel, pRub, pCash, pDonateRubli, pPremium, pAlcoInvenxua FROM accounts WHERE Name = '{name}'")
    if result and len(result) > 0:
        row = result[0]
        text = f"🎮 ИГРОК {name}:\n\n⭐ Уровень: {row[1]}\n💰 Рубли: {row[2]}\n💵 Наличные: {row[3]}\n💎 Донат рубли: {row[4]}\n👑 Премиум: {row[5]}\n🛡️ Админка: {row[6]}"
        
        if is_player_online(name):
            text += f"\n🟢 Статус: В игре"
        else:
            text += f"\n🔴 Статус: Офлайн"
        
        await send_and_delete(message.chat.id, text, reply_markup=get_back_button())
    else:
        await send_and_delete(message.chat.id, f"Игрок {name} не найден")
    await delete_user_message(message)

@dp.message(Command("menu"))
async def menu_command(message: types.Message):
    access = get_access_level(message)
    if access == "none":
        await delete_user_message(message)
        return
    
    await log_command(message, "/menu", "Открыто главное меню")
    
    is_admin_user = is_admin(message)
    msg = await message.answer("📋 Главное меню:", reply_markup=get_main_menu(is_admin_user))
    asyncio.create_task(delete_message_after_delay(msg, DELETE_DELAY))
    await delete_user_message(message)

@dp.message(Command("kickplayer"))
async def cmd_kickplayer(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    args = message.text.split()
    if len(args) < 2:
        await send_and_delete(message.chat.id, "Использование: /kickplayer [ник] [причина]")
        await delete_user_message(message)
        return
    
    name = args[1]
    reason = " ".join(args[2:]) if len(args) > 2 else "Кикнут администратором"
    
    await log_command(message, "/kickplayer", f"Кикнут {name}, причина: {reason}")
    
    result = kick_player(name, reason)
    await send_and_delete(message.chat.id, f"👢 Игрок {name} кикнут\nПричина: {reason}\n{result}")
    await delete_user_message(message)

# ========== ОБРАБОТКА КНОПОК ==========

@dp.callback_query()
async def handle_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_admin_user = user_id in ADMIN_IDS
    
    if callback.data == "back_to_menu":
        await edit_and_delete(callback.message, "📋 Главное меню:", reply_markup=get_main_menu(is_admin_user))
        await callback.answer()
        return
    
    if callback.data == "test_start":
        await callback.answer("✅ Отлично! Ждём на сервере!")
        await edit_and_delete(callback.message, "✅ Ты подтвердил участие в тестировании!\n\n🎮 Заходи на сервер!", 10)
        return
    
    if callback.data == "menu_players":
        result = db_query("SELECT Name FROM accounts LIMIT 30")
        if result:
            text = "👥 СПИСОК ИГРОКОВ:\n\n"
            for i, row in enumerate(result, 1):
                text += f"{i}. {row[0]}\n"
            await edit_and_delete(callback.message, text, reply_markup=get_back_button())
        else:
            await edit_and_delete(callback.message, "Нет данных", reply_markup=get_back_button())
    
    elif callback.data == "menu_search":
        await edit_and_delete(callback.message, "🔍 ПОИСК ИГРОКА\n\nВведите /player [ник]\nНапример: /player Vasya", reply_markup=get_back_button())
    
    elif callback.data == "menu_top_rub":
        result = db_query("SELECT Name, pRub FROM accounts ORDER BY CAST(pRub AS SIGNED) DESC LIMIT 10")
        if result:
            text = "🏆 ТОП 10 ПО РУБЛЯМ:\n\n"
            for i, row in enumerate(result, 1):
                text += f"{i}. {row[0]} — {row[1]} руб\n"
            await edit_and_delete(callback.message, text, reply_markup=get_back_button())
        else:
            await edit_and_delete(callback.message, "Нет данных", reply_markup=get_back_button())
    
    elif callback.data == "menu_top_level":
        result = db_query("SELECT Name, pLevel FROM accounts ORDER BY CAST(pLevel AS SIGNED) DESC LIMIT 10")
        if result:
            text = "🏆 ТОП 10 ПО УРОВНЮ:\n\n"
            for i, row in enumerate(result, 1):
                text += f"{i}. {row[0]} — {row[1]} уровень\n"
            await edit_and_delete(callback.message, text, reply_markup=get_back_button())
        else:
            await edit_and_delete(callback.message, "Нет данных", reply_markup=get_back_button())
    
    elif callback.data == "menu_edit_rub":
        if not is_admin_user:
            await callback.answer("Нет доступа", show_alert=True)
            return
        await edit_and_delete(callback.message, "💰 РЕДАКТИРОВАНИЕ РУБЛЕЙ\n\nИспользуйте команду:\n/set [ник] 213 [сумма]\n\nПример: /set Vasya 213 50000\n\n⚡ Изменения применятся сразу после кика игрока", reply_markup=get_back_button())
    
    elif callback.data == "menu_server":
        if not is_admin_user:
            await callback.answer("Нет доступа", show_alert=True)
            return
        is_running, status = check_server_status()
        await edit_and_delete(callback.message, f"🎮 УПРАВЛЕНИЕ СЕРВЕРОМ\n\nСтатус: {status}\n\nКоманды:\n/status - проверить статус\n/save - сохранить всё\n/kickplayer [ник] - кикнуть игрока", reply_markup=get_back_button())
    
    elif callback.data == "menu_help":
        if is_admin_user:
            await edit_and_delete(callback.message, "📚 ПОМОЩЬ\n\nОБЩИЕ КОМАНДЫ:\n/players - список игроков\n/player [ник] - информация\n\nАДМИН КОМАНДЫ:\n/set [ник] [номер] [значение]\n/status - статус сервера\n/save - сохранить всё\n/kickplayer [ник] - кикнуть игрока\n\nНомера колонок:\n7 - админка\n13 - машина\n18 - хелпер\n19 - донат деньги\n25 - наличные\n122 - донат рубли\n154 - премиум\n213 - рубли\n\n⚡ После изменения данных игрок будет кикнут для применения изменений", reply_markup=get_back_button())
        else:
            await edit_and_delete(callback.message, "📚 ПОМОЩЬ\n\n/players - список игроков\n/player [ник] - информация об игроке\n/menu - открыть меню", reply_markup=get_back_button())
    
    await callback.answer()

# ========== АДМИН КОМАНДЫ ==========

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    await log_command(message, "/status", "Проверка статуса сервера")
    
    is_running, status = check_server_status()
    await send_and_delete(message.chat.id, f"Статус: {status}")
    await delete_user_message(message)

@dp.message(Command("save"))
async def cmd_save(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    await log_command(message, "/save", "Сохранение данных сервера")
    
    await send_and_delete(message.chat.id, "Сохранение...")
    result = rcon("/save")
    await send_and_delete(message.chat.id, f"Результат: {result}")
    await delete_user_message(message)

# ========== ФУНКЦИИ БД И RCON ==========
def db_query(query):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            conn.close()
            return result
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None

def rcon(command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        packet = f"{RCON_PASSWORD} {command}".encode('ascii', errors='ignore')
        sock.sendto(packet, (RCON_HOST, RCON_PORT))
        try:
            data, _ = sock.recvfrom(4096)
            result = data.decode('utf-8', errors='ignore')
            if result.startswith('\x00\x00\x00\x00'):
                result = result[4:]
            return result.strip() or "Выполнено"
        except socket.timeout:
            return "Сервер не отвечает"
        finally:
            sock.close()
    except Exception as e:
        return f"Ошибка RCON: {e}"

def check_server_status():
    result = rcon("/stats")
    if "No" in result or "failed" in result.lower() or "error" in result.lower():
        return False, "❌ Сервер НЕ ОТВЕЧАЕТ"
    return True, "✅ Сервер РАБОТАЕТ"

def get_cell_value(name, column_name):
    result = db_query(f"SELECT {column_name} FROM accounts WHERE Name = '{name}'")
    if result and len(result) > 0:
        return result[0][0]
    return None

def get_all_selected_columns(name):
    result = {}
    for idx, info in COLUMNS_TO_EDIT.items():
        value = get_cell_value(name, info["name"])
        result[idx] = {
            "name": info["name"],
            "value": value if value is not None else "Нет данных",
            "desc": info["desc"]
        }
    return result

def is_player_online(name):
    players = rcon("/players")
    return name.lower() in players.lower()

def kick_player(name, reason="Данные обновлены"):
    return rcon(f"/kick {name} {reason}")

# ========== КЛАВИАТУРЫ ==========
def get_main_menu(is_admin_user=False):
    if is_admin_user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список игроков", callback_data="menu_players")],
            [InlineKeyboardButton(text="🔍 Поиск игрока", callback_data="menu_search")],
            [InlineKeyboardButton(text="📊 Топ по рублям", callback_data="menu_top_rub")],
            [InlineKeyboardButton(text="⭐ Топ по уровню", callback_data="menu_top_level")],
            [InlineKeyboardButton(text="💰 Редактировать рубли", callback_data="menu_edit_rub")],
            [InlineKeyboardButton(text="🎮 Управление сервером", callback_data="menu_server")],
            [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu_help")]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Список игроков", callback_data="menu_players")],
            [InlineKeyboardButton(text="🔍 Поиск игрока", callback_data="menu_search")],
            [InlineKeyboardButton(text="📊 Топ по рублям", callback_data="menu_top_rub")],
            [InlineKeyboardButton(text="⭐ Топ по уровню", callback_data="menu_top_level")],
            [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="menu_help")]
        ])
    return keyboard

def get_back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в главное меню", callback_data="back_to_menu")]
    ])

# ========== АДМИН КОМАНДЫ (продолжение) ==========

@dp.message(Command("set"))
async def cmd_set(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    args = message.text.split()
    if len(args) != 4:
        await send_and_delete(message.chat.id, "Использование: /set [ник] [номер] [значение]\nПример: /set Vasya 213 50000")
        await delete_user_message(message)
        return
    
    name = args[1]
    try:
        col_num = int(args[2])
    except ValueError:
        await send_and_delete(message.chat.id, "Номер должен быть числом")
        await delete_user_message(message)
        return
    
    if col_num not in COLUMNS_TO_EDIT:
        await send_and_delete(message.chat.id, f"Колонка {col_num} не разрешена. Разрешены: 7,13,18,19,25,122,154,213")
        await delete_user_message(message)
        return
    
    value = args[3]
    info = COLUMNS_TO_EDIT[col_num]
    
    await log_edit(message, f"SET {info['desc']}", name, value)
    
    check = db_query(f"SELECT Name FROM accounts WHERE Name = '{name}'")
    if not check:
        await send_and_delete(message.chat.id, f"Игрок {name} не найден")
        await delete_user_message(message)
        return
    
    success = db_query(f"UPDATE accounts SET {info['name']} = '{value}' WHERE Name = '{name}'")
    
    if success:
        await send_and_delete(message.chat.id, f"✅ {info['desc']} игрока {name} = {value}")
        
        rcon("/save")
        
        if is_player_online(name):
            kick_result = kick_player(name, f"Данные обновлены: {info['desc']} = {value}")
            await send_and_delete(message.chat.id, f"👢 Игрок {name} кикнут для применения изменений\nРезультат: {kick_result[:100]}")
        else:
            await send_and_delete(message.chat.id, f"💤 Игрок {name} не в сети, изменения применятся при заходе")
        
        new_value = get_cell_value(name, info["name"])
        await send_and_delete(message.chat.id, f"🔍 Проверка БД: {new_value}")
    else:
        await send_and_delete(message.chat.id, "Ошибка при установке значения")
    
    await delete_user_message(message)

@dp.message(Command("get"))
async def cmd_get(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    args = message.text.split()
    if len(args) != 3:
        await send_and_delete(message.chat.id, "Использование: /get [ник] [номер]\nПример: /get Vasya 213")
        await delete_user_message(message)
        return
    
    name = args[1]
    try:
        col_num = int(args[2])
    except ValueError:
        await send_and_delete(message.chat.id, "Номер должен быть числом")
        await delete_user_message(message)
        return
    
    if col_num not in COLUMNS_TO_EDIT:
        await send_and_delete(message.chat.id, f"Колонка {col_num} не разрешена")
        await delete_user_message(message)
        return
    
    info = COLUMNS_TO_EDIT[col_num]
    value = get_cell_value(name, info["name"])
    
    await log_command(message, "/get", f"{info['desc']} игрока {name} = {value}")
    
    if value is None:
        await send_and_delete(message.chat.id, f"Игрок {name} не найден")
    else:
        online_status = "🟢 В игре" if is_player_online(name) else "🔴 Офлайн"
        await send_and_delete(message.chat.id, f"{info['desc']} игрока {name}: {value}\n\nСтатус: {online_status}")
    await delete_user_message(message)

@dp.message(Command("show"))
async def cmd_show(message: types.Message):
    if not is_admin(message):
        await delete_user_message(message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        await send_and_delete(message.chat.id, "Использование: /show [ник]\nПример: /show Vasya")
        await delete_user_message(message)
        return
    
    name = args[1]
    await log_command(message, "/show", f"Просмотр всех данных игрока {name}")
    
    check = db_query(f"SELECT Name FROM accounts WHERE Name = '{name}'")
    if not check:
        await send_and_delete(message.chat.id, f"Игрок {name} не найден")
        await delete_user_message(message)
        return
    
    data = get_all_selected_columns(name)
    text = f"ДАННЫЕ ИГРОКА {name}:\n\n"
    for idx, info in data.items():
        text += f"{idx}. {info['desc']}: {info['value']}\n"
    
    if is_player_online(name):
        text += f"\n🟢 Статус: В игре"
    else:
        text += f"\n🔴 Статус: Офлайн"
    
    await send_and_delete(message.chat.id, text)
    await delete_user_message(message)

# ========== АВТОПЕРЕЗАПУСК ==========
def auto_restart():
    time.sleep(RESTART_INTERVAL)
    print("\n" + "=" * 60)
    print("🔄 АВТОМАТИЧЕСКИЙ ПЕРЕЗАПУСК БОТА")
    print("=" * 60)
    os.execv(sys.executable, ['python'] + sys.argv)

restart_thread = threading.Thread(target=auto_restart, daemon=True)
restart_thread.start()

# ========== ЗАПУСК ==========
async def main():
    print("=" * 60)
    print("SAMP БОТ ЗАПУЩЕН")
    print("=" * 60)
    print(f"Разрешенные группы: {ALLOWED_GROUPS}")
    print(f"Администраторы: {ADMIN_IDS}")
    print(f"Лог-чат: {LOG_CHAT_ID}")
    print(f"Автоудаление сообщений: {DELETE_DELAY} секунд")
    print("=" * 60)
    print("\n📌 СКРЫТЫЕ КОМАНДЫ (доступны только админам):")
    print("   /qwert - призыв всех заходить в игру и тестировать")
    print("=" * 60)
    
    try:
        await bot.send_message(LOG_CHAT_ID, "✅ Бот запущен!")
        print("✅ Лог-чат доступен")
    except Exception as e:
        print(f"❌ Ошибка доступа к лог-чату: {e}")
    
    test = db_query("SELECT COUNT(*) FROM accounts")
    if test:
        print(f"✅ БД: {test[0][0]} записей")
    else:
        print("❌ Ошибка БД!")
    
    print("=" * 60)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())