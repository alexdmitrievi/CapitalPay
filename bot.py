import os
import datetime
import gspread
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MANAGER_ID = 7279978383
CHANNEL_USERNAME = "@capital_pay"
BOT_USERNAME = "CapitalPay_bot"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def init_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("CapitalPay Leads").sheet1
    return sheet

sheet = init_sheet()

class PartnerForm(StatesGroup):
    country = State()
    methods = State()
    geo = State()
    volume = State()
    contact = State()

def step_keyboard():
    return types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    args = message.get_args()
    username = message.from_user.username or "—"
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([str(message.from_user.id), f"@{username}", args, date])

    banner = types.InputFile("banner.jpg")
    caption = (
        "<b>CapitalPay</b> — платёжная платформа для HighRisk

"
        "💼 Сделки в HighRisk
"
        "📊 Учёт, выплаты, аналитика
"
        "📚 Личный куратор
"
        "💰 Условия для опытных команд

"
        "⚙️ Депозит — от $500
"
        "📉 Вход — 8%, выход — 2,5%
"
        "🔄 Ставка в круг — 10,5%

"
        "🚀 3 дня без депозита
"
        "📆 На рынке с 2020
"
        "📩 @lexcapitalpay"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}")
    )

    await bot.send_photo(chat_id=message.chat.id, photo=banner, caption=caption, parse_mode='HTML', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    text = (
        "🤝 <b>6 преимуществ CapitalPay для тимлидов</b>

"
        "1. Высокая агентская рефка
"
        "2. Моментальный вывод средств
"
        "3. Тест без страхового депа
"
        "4. Личный кабинет и аналитика
"
        "5. Подключаем к закрытым площадкам
"
        "6. Заливаем до 100кк в течение часа

"
        "Хочешь условия и список площадок? Жми кнопку 👇🏼"
    )
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    await bot.send_message(callback_query.from_user.id, text, parse_mode="HTML", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_start(callback_query: types.CallbackQuery):
    await PartnerForm.country.set()
    await bot.send_message(callback_query.from_user.id, "1. Из какой вы страны?", reply_markup=step_keyboard())

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await PartnerForm.methods.set()
    await message.answer("2. Какие методы приёма платежей доступны? (C2C, СБП, крипта и т.д.)", reply_markup=step_keyboard())

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await PartnerForm.geo.set()
    await message.answer("3. На какие гео работаете?", reply_markup=step_keyboard())

@dp.message_handler(state=PartnerForm.geo)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await PartnerForm.volume.set()
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?", reply_markup=step_keyboard())

@dp.message_handler(state=PartnerForm.volume)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await PartnerForm.contact.set()
    await message.answer("5. Контакт для связи (Telegram или Email):", reply_markup=step_keyboard())

@dp.message_handler(state=PartnerForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    summary = (
        f"📩 Новая партнёрская заявка:
"
        f"🌍 Страна: {data['country']}
"
        f"💳 Методы: {data['methods']}
"
        f"📍 Гео: {data['geo']}
"
        f"📈 Объём: {data['volume']}
"
        f"📞 Контакт: {data['contact']}"
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=summary)
    await message.answer("🎉 Заявка отправлена! Мы свяжемся с вами в ближайшее время.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "back")
async def back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == PartnerForm.methods.state:
        await PartnerForm.country.set()
        await bot.send_message(callback_query.from_user.id, "1. Из какой вы страны?", reply_markup=step_keyboard())
    elif current_state == PartnerForm.geo.state:
        await PartnerForm.methods.set()
        await bot.send_message(callback_query.from_user.id, "2. Какие методы приёма платежей доступны?", reply_markup=step_keyboard())
    elif current_state == PartnerForm.volume.state:
        await PartnerForm.geo.set()
        await bot.send_message(callback_query.from_user.id, "3. На какие гео работаете?", reply_markup=step_keyboard())
    elif current_state == PartnerForm.contact.state:
        await PartnerForm.volume.set()
        await bot.send_message(callback_query.from_user.id, "4. Какой объём в день готовы обрабатывать?", reply_markup=step_keyboard())
    else:
        await state.finish()
        await start(callback_query.message, state)

@dp.message_handler(commands=["post_button"])
async def post_button(message: types.Message):
    if message.from_user.id != MANAGER_ID:
        await message.answer("⛔ Доступ запрещён.")
        return

    text = (
        "🚀 Хочешь подключиться к CapitalPay?
"
        "Платёжная платформа для HighRisk: гемблинг, беттинг, дейтинг.

"
        "🛠 Старт без депозита
"
        "📊 Учёт и кабинет под команду
"
        "⚡️ Выплаты 24/7"
    )

    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Подключиться", url=f"https://t.me/{BOT_USERNAME}?start=from_channel")
    )

    await bot.send_message(chat_id=CHANNEL_USERNAME, text=text, reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)