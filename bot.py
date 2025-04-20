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

    banner = types.InputFile("banner.jpg")
    caption = (
        "💼 CapitalPay — платёжная платформа для HighRisk\n"
        "👥 Партнёры, тимлиды, арбитражники\n"
        "📊 Учёт, аналитика, выплаты\n"
        "🚀 Без депозита — 3 дня на тест"
    )

    await bot.set_chat_menu_button(
        menu_button=types.MenuButtonCommands()
    )

    await bot.send_photo(chat_id=message.chat.id, photo=banner, caption=caption, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == "back")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == "connect")
async def form_country(message: types.Message):
    await PartnerForm.country.set()
    await bot.send_message(message.from_user.id, "1. Из какой вы страны?", reply_markup=back_button)


@dp.message_handler(state=PartnerForm.country)
async def form_methods(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Какие методы приёма платежей доступны? (C2C, СБП, crypto и т.д.)", reply_markup=back_button)
    await PartnerForm.methods.set()


@dp.message_handler(state=PartnerForm.methods)
async def form_geo(message: types.Message, state: FSMContext):
    await state.update_data(methods=message.text)
    await message.answer("3. На какое гео работаете?", reply_markup=back_button)
    await PartnerForm.geo.set()


@dp.message_handler(state=PartnerForm.geo)
async def form_volume(message: types.Message, state: FSMContext):
    await state.update_data(geo=message.text)
    await message.answer("4. Какой объём в день готовы обрабатывать (USD)?", reply_markup=back_button)
    await PartnerForm.volume.set()


@dp.message_handler(state=PartnerForm.volume)
async def form_contact(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("5. Контакт для связи (Telegram или Email):", reply_markup=back_button)
    await PartnerForm.contact.set()


@dp.message_handler(state=PartnerForm.contact)
async def form_summary(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    summary = (
        f"📩 Новая партнёрская заявка:\n"
        f"Страна: {data['country']}\n"
        f"Методы: {data['methods']}\n"
        f"Гео: {data['geo']}\n"
        f"Объём: {data['volume']}\n"
        f"Контакт: {data['contact']}"
    )
    await bot.send_message(chat_id=CHANNEL_ID, text=summary)
    await message.answer("Спасибо! Мы получили вашу заявку.")
    await message.answer("🎉 Поздравляем! Вы успешно зарегистрировались как партнёр CapitalPay. Мы свяжемся с вами в ближайшее время.")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "teamlead")
async def teamlead_info(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(
        types.InlineKeyboardButton("📩 Связаться с менеджером", url=f"tg://user?id={MANAGER_ID}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    await bot.send_message(
        callback_query.from_user.id,
        text=(
            "🤝 Наши плюсы для тимлидов:\n\n"
            "1. Высокая агентская рефка\n"
            "2. Вывод в любое время\n"
            "3. Тест трейдера без депа\n"
            "4. ЛК со статистикой\n"
            "5. Подключим к закрытым ПП\n"
            "6. Есть лимиты > 100кк — зальём за час\n\n"
            "👇🏼 Нажми кнопку ниже, чтобы получить список площадок"
        ),
        reply_markup=keyboard
    )


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
