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

# ====== НАСТРОЙКИ (замени на данные клиента) ======
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
    "• Реклама и обмен аудиторией\n"
    "• Совместные проекты\n"
    "• Бонусы для партнёров\n\n"
    "Нажми кнопку ниже и напиши менеджеру."
)
# ==================================================

WAIT_SUPPORT = 0


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Проекты", callback_data="projects"),
         InlineKeyboardButton("🛠 Моды", callback_data="mods")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support"),
         InlineKeyboardButton("🤝 Партнёрка", callback_data="partner")],
        [InlineKeyboardButton("📢 Наш канал", url=CHANNEL_LINK)],
    ])


def back_button() -> list:
    return [InlineKeyboardButton("⬅️ Назад", callback_data="menu")]


async def show(update: Update, text: str, kb: InlineKeyboardMarkup) -> None:
    """Редактирует сообщение (если нажата кнопка) или отправляет новое."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, parse_mode="HTML", reply_markup=kb
        )
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


WELCOME = (
    f"👋 Добро пожаловать в <b>{PROJECT_NAME}</b>!\n\n"
    "Здесь ты найдёшь проекты, моды, поддержку и партнёрку по CRMP.\n\n"
    "Выбери раздел:"
)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await show(update, WELCOME, main_menu())
    return ConversationHandler.END


async def menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    await show(update, WELCOME, main_menu())
    return ConversationHandler.END


async def projects(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    rows = [[InlineKeyboardButton(name, url=url)] for name, url in PROJECTS]
    rows.append(back_button())
    await show(update, "🎮 <b>Наши проекты CRMP:</b>", InlineKeyboardMarkup(rows))


async def mods(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    rows = [[InlineKeyboardButton(name, url=url)] for name, url in MODS]
    rows.append(back_button())
    await show(update, "🛠 <b>Моды и сборки:</b>", InlineKeyboardMarkup(rows))


async def partner(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Написать менеджеру", url=PARTNER_CONTACT)],
        back_button(),
    ])
    await show(update, PARTNER_TEXT, kb)


async def support_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    kb = InlineKeyboardMarkup([back_button()])
    await show(
        update,
        "💬 <b>Поддержка</b>\n\nНапиши свой вопрос одним сообщением, "
        "и мы ответим как можно скорее.",
        kb,
    )
    return WAIT_SUPPORT


async def support_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = (
        "📩 <b>Обращение в поддержку</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🔗 @{user.username or '—'}\n"
        f"🆔 <code>{user.id}</code>\n\n"
        f"💬 {update.message.text}"
    )
    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

    await update.message.reply_text(
        "✅ Сообщение отправлено! Мы скоро ответим.",
        reply_markup=InlineKeyboardMarkup([back_button()]),
    )
    return ConversationHandler.END


async def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    support_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(support_start, pattern="^support$")],
        states={
            WAIT_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(menu, pattern="^menu$"),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(support_conv)
    app.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(projects, pattern="^projects$"))
    app.add_handler(CallbackQueryHandler(mods, pattern="^mods$"))
    app.add_handler(CallbackQueryHandler(partner, pattern="^partner$"))

    logger.info("Бот запущен...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
