import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# === НАСТРОЙКИ ===
TOKEN = "8994612080:AAGJIFMGbPp8uqtiFPLFMGhQMyKYuOnBaEQ"
WEB_APP_URL = "https://bichdrift-hash.github.io/vape-dealer/"

OPERATOR_MAIN = "@vape_dealermd"  # Твой контакт
OPERATOR_ALT = "@ebywz"          # Второй контакт

# СЮДА ВСТАВЬ СВОЙ ID ИЗ БОТА @myidbot (число без кавычек)
ADMIN_CHAT_ID = 8275231458

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Кнопки проверки возраста (18+)
age_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🟢 Мне есть 18 лет", callback_data="age_yes"),
        InlineKeyboardButton(text="🔴 Мне нет 18", callback_data="age_no")
    ]
])

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Добро пожаловать в Vape Dealer!**\n\n"
        "Здесь ты можешь быстро оформить заказ на любимые жидкости, "
        "проверить актуальное наличие в **Бельцах и Кишинёве**, а также связаться с нами.\n\n"
        "⚠️ **ВАЖНО:** Наш бот и канал предназначены строго для лиц, достигших **18 лет**.\n\n"
        "**Тебе уже исполнилось 18 лет?**",
        reply_markup=age_keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data in ["age_yes", "age_no"])
async def process_age(callback: types.CallbackQuery):
    if callback.data == "age_yes":
        menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Открыть магазин", web_app=WebAppInfo(url=WEB_APP_URL))],
            [
                InlineKeyboardButton(text="✍️ Написать оператору", url=f"https://t.me/{OPERATOR_MAIN[1:]}"),
                InlineKeyboardButton(text="ℹ️ Наличие/Связь", callback_data="info_contacts")
            ]
        ])
        await callback.message.edit_text(
            "🎉 **Доступ разрешен!**\n\n"
            "Нажми кнопку **\"Открыть магазин\"** ниже, чтобы открыть каталог и выбрать нужные вкусы 👇",
            reply_markup=menu_keyboard,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ К сожалению, мы не продаем продукцию несовершеннолетним. "
            "Ждем тебя, когда исполнится 18!"
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "info_contacts")
async def process_info(callback: types.CallbackQuery):
    info_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ В магазин", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="age_yes")]
    ])
    await callback.message.edit_text(
        "📍 **Информация Vape Dealer:**\n\n"
        f"• **Доставка/Самовывоз:** Бельцы и Кишинёв\n"
        f"• **Основной контакт:** {OPERATOR_MAIN}\n"
        f"• **Дополнительный контакт:** {OPERATOR_ALT}\n\n"
        "Выбирай товары в Mini App или пиши напрямую операторам!",
        reply_markup=info_keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# ОБНОВЛЕННЫЙ ПРИЕМ ЗАКАЗА: отправляет его тебе и подтверждает клиенту
@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app_data(message: types.Message):
    order_data = message.web_app_data.data
    
    # Получаем данные о покупателе
    user = message.from_user
    username = f"@{user.username}" if user.username else "Нет юзернейма"
    full_name = user.full_name
    user_id = user.id
    user_link = f"tg://user?id={user_id}"

    # Сообщение, которое прилетит лично тебе в чат
    admin_notification = (
        f"🔔 **ПОЛУЧЕН НОВЫЙ ЗАКАЗ!**\n\n"
        f"👤 **Покупатель:** {full_name} ({username})\n"
        f"🆔 **ID пользователя:** `{user_id}`\n"
        f"💬 **Написать клиенту:** [Перейти в чат]({user_link})\n\n"
        f"{order_data}"
    )

    # 1. Отправляем уведомление тебе (админу) в личку
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_notification,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение админу: {e}")

    # 2. Пишем клиенту в чат, что всё принято
    await message.answer(
        f"✅ **Заказ успешно отправлен оператору!**\n\n"
        f"📋 **Твой заказ:**\n{order_data}\n\n"
        f"Оператор {OPERATOR_MAIN} или {OPERATOR_ALT} свяжется с тобой в ближайшее время для подтверждения выдачи. Спасибо! 🙌",
        parse_mode="Markdown"
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
