import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class PartnerForm(StatesGroup):
    country = State()
    methods = State()
    geo = State()
    volume = State()
    contact = State()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("👤 Менеджер", url="https://t.me/lexcapitalpay")
    )
    await message.answer("Привет! Мы ищем команды для обработки платежей в гемблинг/беттинг. Выбери действие:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'connect')
async def connect(callback_query: types.CallbackQuery):
    await callback_query.message.answer("1. Из какой вы страны?")
    await PartnerForm.country.set()
    await callback_query.answer()

@dp.message_handler(state=PartnerForm.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Какие методы приёма платежей доступны? (например: C2C, crypto, APM)")
    await PartnerForm.next()

@dp.message_handler(state=PartnerForm.methods)
async def process_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await message.answer("3. На какие гео работаете?")
    await PartnerForm.next()

@dp.message_handler(state=PartnerForm.geo)
async def process_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?")
    await PartnerForm.next()

@dp.message_handler(state=PartnerForm.volume)
async def process_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("5. Контакт для связи (Telegram или Email):")
    await PartnerForm.next()

@dp.message_handler(state=PartnerForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    summary = (
        f"**Новая партнёрская заявка**\n"
        f"Страна: {data['country']}\n"
        f"Методы: {data['methods']}\n"
        f"Гео: {data['geo']}\n"
        f"Объем/день: {data['volume']}\n"
        f"Контакт: {data['contact']}"
    )

    await bot.send_message(chat_id=CHANNEL_ID, text=summary, parse_mode="Markdown")
    await message.answer("Спасибо! Мы скоро свяжемся с вами.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)