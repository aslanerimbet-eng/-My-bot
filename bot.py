import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

PROJECT_NAME = "CRMP Project"
CHANNEL_LINK = "https://t.me/your_channel"
PARTNER_CONTACT = "https://t.me/your_manager"

PROJECTS = [
    ("🔥 Проект 1", "https://t.me/project1"),
    ("🚀 Проект 2", "https://t.me/project2"),
    ("⭐ Проект 3", "https://t.me/project3"),
]

MODS = [
    ("🚗 Моды на машины", "https://t.me/mods_cars"),
    ("🎨 Моды на скины", "https://t.me/mods_skins"),
    ("📦 Сборки", "https://t.me/mods_packs"),
]

PARTNER_TEXT = (
    "🤝 <b>Партнёрская программа</b>\n\n"
    "Хочешь сотрудничать? Мы открыты к партнёрству.\n\n"
    "Нажми кнопку ниже и напиши менеджеру."
)

WAIT_SUPPORT = 0


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Проекты", callback_data="projects"),
         InlineKeyboardButton("🛠 Моды", callback_data="mods")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support"),
         InlineKeyboardButton("🤝 Партнёрка", callback_data="partner")],
        [InlineKeyboardButton("📢 Наш канал", url=CHANNEL_LINK)],
    ])


def back_button():
    return [InlineKeyboardButton("⬅️ Назад", callback_data="menu")]


async def show(update, text, kb):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


WELCOME = f"👋 Добро пожаловать в <b>{PROJECT_NAME}</b>!\n\nВыбери раздел:"


async def start(update, ctx):
    await show(update, WELCOME, main_menu())
    return ConversationHandler.ENDasync def menu(update, ctx):
    await show(update, WELCOME, main_menu())
    return ConversationHandler.END


async def projects(update, ctx):
    rows = [[InlineKeyboardButton(n, url=u)] for n, u in PROJECTS]
    rows.append(back_button())
    await show(update, "🎮 <b>Наши проекты:</b>", InlineKeyboardMarkup(rows))


async def mods(update, ctx):
    rows = [[InlineKeyboardButton(n, url=u)] for n, u in MODS]
    rows.append(back_button())
    await show(update, "🛠 <b>Моды и сборки:</b>", InlineKeyboardMarkup(rows))


async def partner(update, ctx):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Написать менеджеру", url=PARTNER_CONTACT)],
        back_button(),
    ])
    await show(update, PARTNER_TEXT, kb)


async def support_start(update, ctx):
    kb = InlineKeyboardMarkup([back_button()])
    await show(update, "💬 <b>Поддержка</b>\n\nНапиши свой вопрос:", kb)
    return WAIT_SUPPORT


async def support_message(update, ctx):
    user = update.effective_user
    text = (
        f"📩 <b>Обращение</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🔗 @{user.username or '—'}\n"
        f"🆔 <code>{user.id}</code>\n\n"
        f"💬 {update.message.text}"
    )
    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    await update.message.reply_text("✅ Отправлено!", reply_markup=InlineKeyboardMarkup([back_button()]))
    return ConversationHandler.END


if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    support_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(support_start, pattern="^support$")],
        states={WAIT_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message)]},
        fallbacks=[CommandHandler("start", start), CallbackQueryHandler(menu, pattern="^menu$")],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(support_conv)
    app.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(projects, pattern="^projects$"))
    app.add_handler(CallbackQueryHandler(mods, pattern="^mods$"))
    app.add_handler(CallbackQueryHandler(partner, pattern="^partner$"))

    logger.info("Бот запущен...")
    app.run_polling()
