import os
import logging
import gspread
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHANNEL_USERNAME = "@capital_pay"
MANAGER_ID = 7279978383
BOT_USERNAME = "Capitalpay_newbot"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# Google Sheets
def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_path = "/etc/secrets/capitalpay-3d03a47fdd18.json"
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open("CapitalPay Leads").sheet1
    return sheet

sheet = init_sheet()

# Состояния формы
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

# Старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}")
    )
    banner = types.InputFile("banner.jpg")
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
        "📆 На рынке с 2020\n"
        "📩 @lexcapitalpay"
    )
    await bot.send_photo(message.chat.id, banner, caption=caption, reply_markup=keyboard)

# Тимлид
@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    text = (
        "🤝 <b>6 преимуществ CapitalPay для тимлидов</b>\n\n"
        "1. Высокая агентская рефка\n"
        "2. Моментальный вывод средств\n"
        "3. Тест без страхового депа\n"
        "4. Личный кабинет и аналитика\n"
        "5. Подключаем к закрытым площадкам\n"
        "6. Заливаем до 100кк в течение часа\n\n"
        "Хочешь условия и список площадок? Жми кнопку 👇🏼"
    )
    await bot.send_message(callback_query.from_user.id, text, reply_markup=back_or_manager())

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)

# Анкета
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
    sheet.append_row([
        message.from_user.id,
        data['country'],
        data['methods'],
        data['geo'],
        data['volume'],
        data['contact']
    ])
    await bot.send_message(CHANNEL_ID, f"""
<b>Новая партнёрская заявка:</b>
Страна: {data['country']}
Методы: {data['methods']}
Гео: {data['geo']}
Объём: {data['volume']}
Контакт: {data['contact']}
""")
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Поздравляем! Вы успешно зарегистрировались как партнёр CapitalPay.")
    await state.finish()

# Публикация в канал
@dp.message_handler(commands=["publish"])
async def publish_welcome_post(message: types.Message):
    text = (
        "🚀 <b>CapitalPay</b> — ваш надёжный партнёр в мире гемблинг-платежей!\n\n"
        "Если вы работаете с финансовыми потоками в iGaming, вы знаете: надёжный процессинг — это как туз в рукаве. CapitalPay готов стать вашим козырем 💼\n\n"
        "🎯 <b>Почему топовые команды выбирают нас?</b>\n\n"
        "💰 <b>Выгодные условия для тимлидов:</b>\n"
        "• Спецтарифы для крупных проектов\n"
        "• Бонусы за объём и лояльность\n"
        "• Индивидуальные решения под ваш трафик\n\n"
        "💻 <b>Софт, который экономит нервы:</b>\n"
        "• Удобный личный кабинет с аналитикой\n"
        "• Интеграция API за 1 день\n"
        "• Автоотчёты 24/7\n\n"
        "🛡 <b>Поддержка с опытом:</b>\n"
        "• Персональный менеджер в теме гемблинга\n"
        "• Быстрые ответы и помощь 24/7\n"
        "• Работаем с KYC, чарджбэками и рисками\n\n"
        "👥 Присоединяйтесь к чату: @CapitalPay_Chat\n"
        "⬇️ Нажмите кнопку ниже, чтобы подключиться!"
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🔗 Подключиться", url="https://t.me/Capitalpay_newbot?start=from_channel")
    )
    await bot.send_message(chat_id=CHANNEL_USERNAME, text=text, reply_markup=keyboard)

# 📌 Мини-пост с кнопкой «Посмотреть»
@dp.message_handler(commands=["info"])
async def view_channel_message(message: types.Message):
    text = (
        "ℹ️ <b>Не пропустите важное!</b>\n\n"
        "Прямо над закреплённым сообщением — ценная информация для команд и тимлидов:\n"
        "• ответы на частые вопросы\n"
        "• условия подключения\n"
        "• быстрые гайды и ссылки\n\n"
        "🔼 Пролистайте немного вверх или нажмите кнопку ниже 👇"
    )
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("👀 Посмотреть", url="https://t.me/capital_pay/17")
    )
    await message.answer(text, reply_markup=keyboard)

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
