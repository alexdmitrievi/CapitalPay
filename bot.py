import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

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

def manager_buttons(include_back=True):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"))
    if include_back:
        kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("🤝 Стать партнёром", callback_data="connect"),
        types.InlineKeyboardButton("👨‍💼 Я тимлид 🤗", callback_data="teamlead"),
        types.InlineKeyboardButton("🔁 Перезапустить", callback_data="restart"),
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
    await bot.send_photo(chat_id=message.chat.id, photo=banner, caption=caption, parse_mode='HTML', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_start(callback_query: types.CallbackQuery):
    await PartnerForm.country.set()
    await callback_query.message.answer("1. Из какой вы страны?", reply_markup=manager_buttons())

@dp.message_handler(state=PartnerForm.country)
async def form_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await PartnerForm.methods.set()
    await message.answer("2. Какие методы приёма платежей доступны?", reply_markup=manager_buttons())

@dp.message_handler(state=PartnerForm.methods)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await PartnerForm.geo.set()
    await message.answer("3. На какое гео работаете?", reply_markup=manager_buttons())

@dp.message_handler(state=PartnerForm.geo)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await PartnerForm.volume.set()
    await message.answer("4. Какой объём в день готовы обрабатывать?", reply_markup=manager_buttons())

@dp.message_handler(state=PartnerForm.volume)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await PartnerForm.contact.set()
    await message.answer("5. Контакт для связи (Telegram или Email):", reply_markup=manager_buttons())

@dp.message_handler(state=PartnerForm.contact)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    summary = f"""
<b>Новая партнёрская заявка:</b>

Страна: {data['country']}
Методы: {data['methods']}
Гео: {data['geo']}
Объём: {data['volume']}
Контакт: {data['contact']}
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=summary, parse_mode="HTML")
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Вы успешно зарегистрировались как партнёр CapitalPay. Мы свяжемся с вами в ближайшее время.")
    await state.finish()

@dp.callback_query_handler(Text(equals="back"), state=PartnerForm.methods)
async def back_to_country(callback: types.CallbackQuery):
    await PartnerForm.country.set()
    await callback.message.answer("1. Из какой вы страны?", reply_markup=manager_buttons())

@dp.callback_query_handler(Text(equals="back"), state=PartnerForm.geo)
async def back_to_methods(callback: types.CallbackQuery):
    await PartnerForm.methods.set()
    await callback.message.answer("2. Какие методы приёма платежей доступны?", reply_markup=manager_buttons())

@dp.callback_query_handler(Text(equals="back"), state=PartnerForm.volume)
async def back_to_geo(callback: types.CallbackQuery):
    await PartnerForm.geo.set()
    await callback.message.answer("3. На какое гео работаете?", reply_markup=manager_buttons())

@dp.callback_query_handler(Text(equals="back"), state=PartnerForm.contact)
async def back_to_volume(callback: types.CallbackQuery):
    await PartnerForm.volume.set()
    await callback.message.answer("4. Какой объём в день готовы обрабатывать?", reply_markup=manager_buttons())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
