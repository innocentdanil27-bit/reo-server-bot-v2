"""
A feature-rich Telegram bot with webhook support.
"""
import os
import logging
import asyncio
import uuid
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

# Allowed users (empty list = allow everyone)
ALLOWED_USERS_RAW = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USERS = [int(uid) for uid in ALLOWED_USERS_RAW.split(",") if uid.strip()]

# VLESS Hosts
ECONET_HOST = "vpsbible.com"
ZOL_HOST = "172.64.145.202"

def make_vless(host, port=443):
    uid = str(uuid.uuid4())
    return f"vless://{uid}@{host}:{port}?encryption=none&security=tls&sni={host}&type=ws&path=%2F#REO-{host}"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def restricted(func):
    """Decorator to restrict commands to allowed users."""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            await update.message.reply_text("🚫 Access denied.")
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            return
        return await func(update, context)
    return wrapped

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, {user.first_name}! 👋\n\n"
        f"I'm your personal bot. Here's what I can do:\n"
        f"/help - Show all commands\n"
        f"/time - Current server time\n"
        f"/echo [text] - Echo your message\n"
        f"/status - Server status\n"
        f"/econet - Get Econet VLESS\n"
        f"/zol - Get Zol VLESS"
    )

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
*Available Commands:*

/start - Welcome message
/help - This help message
/time - Current server time
/echo [text] - Echo text back
/status - Check server status
/ping - Test bot response
/econet - Get Econet VLESS
/zol - Get Zol VLESS
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

@restricted
async def econet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(make_vless(ECONET_HOST))

@restricted
async def zol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(make_vless(ZOL_HOST))

@restricted
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now()
    await update.message.reply_text(
        f"🕐 Server time: `{now.strftime('%Y-%m-%d %H:%M:%S')}`",
        parse_mode="Markdown"
    )

@restricted
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"📢 {text}")
    else:
        await update.message.reply_text("Usage: /echo [your message]")

@restricted
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import subprocess
    try:
        uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
        disk = subprocess.check_output("df -h / | tail -1 | awk '{print $3\"/\"$2\" (\"$5\" used)\"}'",
                                        shell=True).decode().strip()
        mem = subprocess.check_output("free -h | grep Mem | awk '{print $3\"/\"$2}'",
                                       shell=True).decode().strip()
        status_text = (
            f"*Server Status* ✅\n\n"
            f"⏱ Uptime: `{uptime}`\n"
            f"💾 Disk: `{disk}`\n"
            f"🧠 Memory: `{mem}`"
        )
        await update.message.reply_text(status_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error getting status: {e}")

@restricted
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🏓 Pong!")

@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

async def post_init(application: Application) -> None:
    commands = [
        BotCommand("start", "Welcome message"),
        BotCommand("help", "Show all commands"),
        BotCommand("time", "Current server time"),
        BotCommand("status", "Server status"),
        BotCommand("ping", "Test response"),
        BotCommand("echo", "Echo a message"),
        BotCommand("econet", "Get Econet VLESS"),
        BotCommand("zol", "Get Zol VLESS"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands registered")

def main() -> None:
    application = (
        Application.builder()
       .token(BOT_TOKEN)
       .post_init(post_init)
       .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("econet", econet))
    application.add_handler(CommandHandler("zol", zol))
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
