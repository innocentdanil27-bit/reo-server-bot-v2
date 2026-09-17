import os
import logging
import uuid
from datetime import datetime

from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8443"))

ALLOWED_USERS_RAW = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USERS = [int(uid) for uid in ALLOWED_USERS_RAW.split(",") if uid.strip()]

# VLESS Hosts
ECONET_HOST = "vpsbible.com"
ZOL_HOST = "172.64.145.202"

def make_vless(host, port=443):
    uid = str(uuid.uuid4())
    return f"vless://{uid}@{host}:{port}?encryption=none&security=tls&sni={host}&type=ws&path=%2F#REO-{host}"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def restricted(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            await update.message.reply_text("🚫 Access denied.")
            return
        return await func(update, context)
    return wrapped

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, {user.first_name}! 👋\n\n"
        f"/help - commands\n"
        f"/econet - Econet VLESS\n"
        f"/zol - Zol VLESS\n"
        f"/time - time\n"
        f"/ping - pong"
    )

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - start\n/help - help\n/econet - Econet VLESS\n/zol - Zol VLESS\n/time - time\n/echo [text] - echo\n/status - status\n/ping - ping",
    )

@restricted
async def econet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(make_vless(ECONET_HOST))

@restricted
async def zol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(make_vless(ZOL_HOST))

@restricted
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}")

@restricted
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else "Usage: /echo [text]"
    await update.message.reply_text(f"📢 {text}")

@restricted
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running")

@restricted
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!")

@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

async def post_init(application: Application):
    commands = [
        BotCommand("start", "Start"),
        BotCommand("help", "Help"),
        BotCommand("econet", "Econet VLESS"),
        BotCommand("zol", "Zol VLESS"),
        BotCommand("time", "Time"),
        BotCommand("echo", "Echo"),
        BotCommand("status", "Status"),
        BotCommand("ping", "Ping"),
    ]
    await application.bot.set_my_commands(commands)

def main():
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("econet", econet))
    application.add_handler(CommandHandler("zol", zol))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"Starting webhook on port {PORT}")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
