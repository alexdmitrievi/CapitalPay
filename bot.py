
import os
import logging
import gspread
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = -1002316458792
MANAGER_ID = 7279978383
BOT_USERNAME = "Capitalpay_newbot"

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = "/etc/secrets/capitalpay-3d03a47fdd18.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    return client.open("CapitalPay Leads").sheet1

sheet = init_sheet()

class PartnerForm(StatesGroup):
    country = State()
    methods = State()
    geo = State()
    volume = State()
    contact = State()

def back_or_manager():
    return types.InlineKeyboardMarkup(row_width=2).add(
        types.InlineKeyboardButton("🔙 Назад", callback_data="back"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}")
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    source = message.get_args() or "-"
    await dp.storage.set_data(user=message.from_user.id, data={"source": source})

    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}")
    )

    caption = (
        "<b>CapitalPay</b>\n"
        "💼 Сделки в HighRisk\n"
        "📊 Учёт, выплаты, аналитика\n"
        "📚 Личный куратор\n"
        "💰 Условия для опытных команд\n"
        "⚙️ Депозит — от $500\n"
        "📉 Вход — 8%, выход — 2,5%\n"
        "🔄 Ставка в круг — 10,5%\n"
        "🚀 3 дня без депозита\n"
        "📆 На рынке с 2020\n"
        "📩 @lexcapitalpay"
    )

    if os.path.exists("banner.jpg"):
        await bot.send_photo(message.chat.id, types.InputFile("banner.jpg"), caption=caption, reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    text = (
        "🤝 <b>6 преимуществ CapitalPay для тимлидов</b>\n"
        "1. Высокая агентская рефка\n"
        "2. Моментальный вывод средств\n"
        "3. Тест без страхового депа\n"
        "4. Личный кабинет и аналитика\n"
        "5. Подключаем к закрытым площадкам\n"
        "6. Заливаем до 100кк в течение часа\n"
        "Хочешь условия и список площадок? Жми кнопку 👇🏼"
    )
    await bot.send_message(callback_query.from_user.id, text, reply_markup=back_or_manager())

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_start(callback_query: types.CallbackQuery):
    await callback_query.message.answer("1. Из какой вы страны?", reply_markup=back_or_manager())
    await PartnerForm.country.set()

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Какие методы приёма платежей доступны?", reply_markup=back_or_manager())
    await PartnerForm.methods.set()

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await message.answer("3. На каком гео работаете?", reply_markup=back_or_manager())
    await PartnerForm.geo.set()

@dp.message_handler(state=PartnerForm.geo)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?", reply_markup=back_or_manager())
    await PartnerForm.volume.set()

@dp.message_handler(state=PartnerForm.volume)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("5. Контакт для связи (Telegram или Email):", reply_markup=back_or_manager())
    await PartnerForm.contact.set()

@dp.message_handler(state=PartnerForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    user = message.from_user
    source_data = await dp.storage.get_data(user=user.id)
    source = source_data.get("source", "-")
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
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Поздравляем! Вы успешно зарегистрировались как партнёр CapitalPay.")
    await state.finish()

@dp.message_handler(commands=["publish"])
async def publish_post(message: types.Message):
    text = (
        "🚀 <b>CapitalPay</b> — ваш надёжный партнёр в мире гемблинг-платежей!\n"
        "🎯 <b>Почему выбирают нас?</b>\n"
        "💰 Выгодные условия для тимлидов\n"
        "💻 Софт с аналитикой и API\n"
        "🛡 Поддержка с опытом в гемблинге\n"
        "👥 Присоединяйтесь к чату: @CapitalPay_Chat\n"
        "⬇️ Нажмите кнопку ниже, чтобы подключиться!"
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🔗 Подключиться", url="https://t.me/Capitalpay_newbot?start=from_channel")
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=keyboard)

@dp.message_handler(commands=["info"])
async def info_post(message: types.Message):
    text = (
        "ℹ️ Важная информация прямо над закреплённым постом:\n"
        "• Частые вопросы\n"
        "• Условия\n"
        "• Гайды\n"
        "👀 Нажми кнопку или пролистай вверх"
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("👀 Посмотреть", url="https://t.me/capital_pay/17")
    )
    await message.answer(text, reply_markup=keyboard)

async def on_startup(dp):
    await bot.set_my_commands([
        types.BotCommand("start", "🔁 Перезапустить"),
        types.BotCommand("publish", "📣 Опубликовать пост"),
        types.BotCommand("info", "ℹ️ Инфо над закрепом")
    ])

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
