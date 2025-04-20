import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

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
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
    )

    banner = types.InputFile("Поиск команды.jpg")

    await bot.send_photo(chat_id=message.chat.id, photo=banner)

    intro_text = """
CapitalPay
💼 Платформа для проведения сделок в HighRisk
📊 Собственный софт для учёта, выплат и аналитики
📚 Учебный центр с личным куратором
💰 Выгодные условия для опытных команд

⚙️ Минимальный депозит — 500$
📉 Вход — 8%, выход — 2,5%
🔄 Ставка в круг — 10,5%

🚀 3 дня работы без страхового депозита
📆 На рынке с 2020 года

📩 Связь: @lexcapitalpay
"""
    await message.answer(intro_text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def start_form(callback_query: types.CallbackQuery):
    await callback_query.message.answer("1. Из какой вы страны?", reply_markup=back_button)
    await PartnerForm.country.set()
    await callback_query.answer()

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Какие методы приёма платежей доступны? (С2С, СБП, crypto и т.д.)", reply_markup=back_button)
    await PartnerForm.methods.set()

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await message.answer("3. По каким гео работаете?", reply_markup=back_button)
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
    summary = f"""
Новая партнёрская заявка:
Страна: {data['country']}
Методы: {data['methods']}
Гео: {data['geo']}
Объём: {data['volume']}
Контакт: {data['contact']}
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=summary)
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Поздравляем! Вы успешно зарегистрировались как партнёр CapitalPay. Мы свяжемся с вами в ближайшее время.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")
    )
    text = """
🤝 6 наших преимуществ при работе с тимлидами:

1. Высокая агентская рефка;
2. Выводите баланс в любое время;
3. Тестовый период для трейдера без страхового депа;
4. Личный кабинет с детальной статистикой по всем вашим трейдерам;
5. Подключайте к закрытым площадкам через нас;
6. В данный момент свободный объем более 100кк, так что зальем в лимиты менее чем за 1 час.

Если хочешь узнать условия и получить список площадок, нажми кнопку ниже👇🏼
"""
    await callback_query.message.answer(text, reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)
    await callback_query.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
