import logging
import os
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменной окружения
BOT_TOKEN = os.environ["BOT_TOKEN"]

# 🔐 Список разрешённых Telegram ID (замените на свои)
ALLOWED_USERS = set(map(int, os.environ.get("ALLOWED_USER_IDS", "").split(","))) if os.environ.get("ALLOWED_USER_IDS") else None

# 🔗 Ссылки на прайсы (временно заглушки — заменим позже)
PRICE_OPT_URL = os.environ.get("PRICE_OPT_URL", "https://example.com/opt.xlsx")
PRICE_RETAIL_URL = os.environ.get("PRICE_RETAIL_URL", "https://example.com/retail.xlsx")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}!\n"
        "Используйте:\n"
        "/opt — прайс опт\n"
        "/retail — прайс розница"
    )

async def check_access(update: Update):
    if ALLOWED_USERS and update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return False
    return True

async def send_price(update: Update, url: str, name: str):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        await update.message.reply_document(
            document=resp.content,
            filename=f"{name}.xlsx"
        )
    except Exception as e:
        logging.error(f"Ошибка загрузки {name}: {e}")
        await update.message.reply_text(f"❌ Не удалось получить прайс '{name}'. Попробуйте позже.")

async def opt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await send_price(update, PRICE_OPT_URL, "Прайс_опт")

async def retail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_access(update):
        return
    await send_price(update, PRICE_RETAIL_URL, "Прайс_розница")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("opt", opt))
    app.add_handler(CommandHandler("retail", retail))
    app.run_polling()

if __name__ == "__main__":
    main()
