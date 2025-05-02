import os
import logging
import gspread
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials

PORT = int(os.environ.get('PORT', 8080))

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = -1002316458792
MANAGER_ID = 7279978383
ADMIN_IDS = [7279978383]  # список админов
BOT_USERNAME = "Capitalpay_newbot"

if not API_TOKEN:
    raise Exception("API_TOKEN not found in environment variables")

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if not creds_json:
        raise Exception("GOOGLE_CREDS_JSON not found in environment variables")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("CapitalPay Leads").sheet1

sheet = init_sheet()

class PartnerForm(StatesGroup):
    country = State()
    methods = State()
    geo = State()
    volume = State()
    contact = State()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    source = message.get_args() or "direct"
    await dp.storage.set_data(user=message.from_user.id, data={"source": source})

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    # Кнопки для всех
    keyboard.add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}")
    )

    # Дополнительно кнопки только для админов
    if str(message.from_user.id) in [str(admin) for admin in ADMIN_IDS]:
        keyboard.add(
            types.InlineKeyboardButton("📢 Опубликовать пост", callback_data="publish_post"),
            types.InlineKeyboardButton("ℹ️ Опубликовать инфо", callback_data="info_post")
        )

    caption = (
        "<b>CapitalPay</b>\n\n"
        "💼 Сделки в HighRisk\n"
        "📊 Учёт, выплаты, аналитика\n"
        "📚 Личный куратор\n"
        "💰 Условия для опытных команд\n\n"
        "⚙️ Депозит — от $500\n"
        "📉 Вход — 8%, выход — 2,5%\n"
        "🔄 Ставка в круг — 10,5%\n\n"
        "🚀 3 дня без депозита\n"
        "📆 На рынке с 2020\n\n"
        "📩 @lexcapitalpay"
    )

    if os.path.exists("banner.jpg"):
        await bot.send_photo(message.chat.id, types.InputFile("banner.jpg"), caption=caption, reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    text = (
        "🤝 <b>6 преимуществ CapitalPay для тимлидов</b>\n\n"
        "1. Высокая агентская рефка\n"
        "2. Моментальный вывод средств\n"
        "3. Тест без страхового депа\n"
        "4. Личный кабинет и аналитика\n"
        "5. Подключаем к закрытым площадкам\n"
        "6. Заливаем до 100кк в течение часа\n\n"
        "👇🏼 Жми кнопку ниже"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )

    await bot.send_message(callback_query.from_user.id, text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "back_to_menu", state="*")
async def back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await start(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_start(callback_query: types.CallbackQuery):
    await PartnerForm.country.set()
    await bot.send_message(callback_query.from_user.id, "1. Из какой вы страны?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
        ))

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await PartnerForm.methods.set()
    await message.answer("2. Какие методы приёма платежей доступны?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
        ))

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await PartnerForm.geo.set()
    await message.answer("3. На каком гео работаете?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
        ))

@dp.message_handler(state=PartnerForm.geo)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await PartnerForm.volume.set()
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
        ))

@dp.message_handler(state=PartnerForm.volume)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await PartnerForm.contact.set()
    await message.answer("5. Контакт для связи (Telegram или Email):",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
            types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
        ))

@dp.message_handler(state=PartnerForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    user = message.from_user
    source_data = await dp.storage.get_data(user=user.id)
    source = source_data.get("source", "direct")

    sheet.append_row([
        user.id,
        f"@{user.username}" if user.username else "-",
        source,
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    ])

    await bot.send_message(MANAGER_ID, f"<b>Новая партнёрская заявка:</b>\n"
                                       f"Страна: {data['country']}\n"
                                       f"Методы: {data['methods']}\n"
                                       f"Гео: {data['geo']}\n"
                                       f"Объём: {data['volume']}\n"
                                       f"Контакт: {data['contact']}")

    await message.answer("Спасибо! Мы получили вашу заявку. 🎉")
    await state.finish()

# Обработка кнопки "ℹ️ Опубликовать инфо"
@dp.callback_query_handler(lambda c: c.data == "info_post")
async def info_post_button(callback_query: types.CallbackQuery):
    if str(callback_query.from_user.id) not in [str(admin) for admin in ADMIN_IDS]:
        await callback_query.answer("🚫 Нет доступа.", show_alert=True)
        return

    await send_info_post()
    await callback_query.answer("✅ Информация опубликована.", show_alert=True)

# Команда /publish (только для админов)
@dp.message_handler(commands=["publish"])
async def publish_post_command(message: types.Message):
    if str(message.from_user.id) not in [str(admin) for admin in ADMIN_IDS]:
        await message.reply("🚫 У вас нет прав для публикации поста.")
        return

    await send_publish_post()
    await message.reply("✅ Пост опубликован.")

# Обработка кнопки "📢 Опубликовать пост"
@dp.callback_query_handler(lambda c: c.data == "publish_post")
async def publish_post_button(callback_query: types.CallbackQuery):
    if str(callback_query.from_user.id) not in [str(admin) for admin in ADMIN_IDS]:
        await callback_query.answer("🚫 Нет доступа.", show_alert=True)
        return

    await send_publish_post()
    await callback_query.answer("✅ Пост опубликован.", show_alert=True)

# Общая функция отправки инфо-поста
async def send_info_post():
    text = (
        "ℹ️ Важная информация над закреплённым постом:\n\n"
        "• Условия для команд\n"
        "• Почему выбирают нас\n"
        "• Обзор нашей платформы\n\n"
        "👀 Нажмите на кнопку ниже, чтобы ознакомиться с важной информацией. "
        "После перехода, пролистайте вниз, чтобы узнать больше о нашем софте и условиях для трейдеров."
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("👀 Посмотреть", url="https://t.me/capital_pay/17")
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=keyboard)

# Общая функция отправки промо-поста
async def send_publish_post():
    text = (
        "🚀 <b>CapitalPay</b> — ваш надёжный партнёр в мире гемблинг-платежей!\n\n"
        "🎯 <b>Почему выбирают нас?</b>\n"
        "💰 Выгодные условия для тимлидов\n"
        "💻 Софт с аналитикой и API\n"
        "🛡 Поддержка с опытом в гемблинге\n\n"
        "👥 Присоединяйтесь к чату: @CapitalPay_Chat\n"
        "⬇️ Нажмите кнопку ниже, чтобы подключиться!"
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🔗 Подключиться", url=f"https://t.me/{BOT_USERNAME}?start=from_channel")
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=keyboard)

async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    logging.info("🤖 Бот запускается...")

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        types.BotCommand("start", "🔁 Перезапустить"),
    ])

    logging.info("✅ Команды установлены и бот успешно запущен.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

