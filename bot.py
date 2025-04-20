import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MANAGER_ID = 7279978383

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class PartnerForm(StatesGroup):
    country = State()
    methods = State()
    geo = State()
    volume = State()
    contact = State()

back_button = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton("🔙 Назад", callback_data="back")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead")
    )

    banner = types.InputFile("banner.jpg")
    caption = (
        "<b>CapitalPay</b> — платёжная платформа для HighRisk\n\n"
        "📊 Учёт, аналитика, выплаты\n"
        "🚀 Без депозита — 3 дня теста\n\n"
        "Нажмите кнопку ниже 👇🏼"
    )

    await bot.send_photo(chat_id=message.chat.id, photo=banner, caption=caption, parse_mode='HTML', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "🔁 Перезапустить")
async def restart_from_menu(message: types.Message):
    await start(message)

@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    msg = (
        "🤝 <b>6 преимуществ CapitalPay для тимлидов</b>\n\n"
        "1. Высокая агентская рефка\n"
        "2. Моментальный вывод средств\n"
        "3. Тест без страхового депа\n"
        "4. Личный кабинет и аналитика\n"
        "5. Подключаем к закрытым площадкам\n"
        "6. Заливаем до 100кк в течение часа\n\n"
        "Хочешь условия и список площадок? Жми кнопку👇🏼"
    )
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    await bot.edit_message_text(
        msg, callback_query.from_user.id, callback_query.message.message_id,
        parse_mode='HTML', reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_start(callback_query: types.CallbackQuery):
    await PartnerForm.country.set()
    await callback_query.message.answer("1. Из какой вы страны?", reply_markup=back_button)
    await callback_query.answer()

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Какие методы приёма платежей доступны? (C2C, СБП, crypto и т.д.)", reply_markup=back_button)
    await PartnerForm.methods.set()

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await message.answer("3. На какие гео работаете?", reply_markup=back_button)
    await PartnerForm.geo.set()

@dp.message_handler(state=PartnerForm.geo)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?", reply_markup=back_button)
    await PartnerForm.volume.set()

@dp.message_handler(state=PartnerForm.volume)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("5. Контакт для связи (Telegram или Email):", reply_markup=back_button)
    await PartnerForm.contact.set()

@dp.message_handler(state=PartnerForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    summary = (
        "📥 <b>Новая партнёрская заявка</b>\n\n"
        f"🌍 Страна: <b>{data['country']}</b>\n"
        f"💳 Методы: <b>{data['methods']}</b>\n"
        f"📍 Гео: <b>{data['geo']}</b>\n"
        f"📈 Объём: <b>{data['volume']}</b>\n"
        f"📞 Контакт: <b>{data['contact']}</b>"
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=summary, parse_mode='HTML')
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Поздравляем! Вы успешно зарегистрировались как партнёр CapitalPay. Мы свяжемся с вами в ближайшее время.")
    await state.finish()

# Установка команд для меню Telegram
async def set_commands(_: Dispatcher):
    await bot.set_my_commands([
        types.BotCommand("start", "🔁 Перезапустить")
    ])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)