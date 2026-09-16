import os, threading, random
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ZOL_HOST = "172.64.145.202"
ECONET_HOST = "vpsbible.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def cat_time():
    return (datetime.now(timezone.utc)+timedelta(hours=2)).strftime("%d/%m/%Y %H:%M CAT")

@app.route('/')
def home(): return f"LIVE ZOL:{ZOL_HOST} ECONET:{ECONET_HOST} {cat_time()}"

@bot.message_handler(commands=['start'])
def h_start(m):
    mk=InlineKeyboardMarkup(row_width=2)
    mk.add(InlineKeyboardButton(f"ZOL {ZOL_HOST}", callback_data="gen_ZOL"), InlineKeyboardButton(f"ECONET {ECONET_HOST}", callback_data="gen_ECONET"))
    bot.send_message(m.chat.id, f"REO GEN {cat_time()}\nZOL: {ZOL_HOST}\nECONET: {ECONET_HOST}\n/gen /create /status", reply_markup=mk)

@bot.message_handler(commands=['gen','server','create','status','host'])
def h_all(m):
    host = ZOL_HOST
    if "ECONET" in m.text.upper(): host = ECONET_HOST
    bot.send_message(m.chat.id, f"✅ Host: {host}\n{cat_time()}")
    with open("server.txt","w") as f: f.write(f"Host: {host}\n{cat_time()}")
    with open("server.txt","rb") as f: bot.send_document(m.chat.id, f)

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    host = ZOL_HOST if "ZOL" in c.data else ECONET_HOST
    if "FAMILY" in c.data: host = f"{ZOL_HOST} + {ECONET_HOST}"
    bot.send_message(c.message.chat.id, f"✅ SERVER {host}\n{cat_time()}")
    with open("server.txt","w") as f: f.write(f"Host: {host}")
    with open("server.txt","rb") as f: bot.send_document(c.message.chat.id, f)

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
if __name__=="__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
