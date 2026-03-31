import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- BAGIAN WEB SERVER (ANTI-SLEEP) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    # Render menggunakan port 10000 secara default
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# --- BAGIAN DOWNLOADER ---
def download_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Pastikan format mp4 agar bisa diputar langsung
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirimkan link video untuk didownload!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    status_msg = await update.message.reply_text("Memproses... ⏳")
    
    try:
        file_path = await asyncio.to_thread(download_video, url)
        await update.message.reply_video(video=open(file_path, 'rb'))
        os.remove(file_path)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"Terjadi kesalahan: {str(e)}")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Jalankan Flask di thread terpisah
    threading.Thread(target=run_flask, daemon=True).start()

    # Jalankan Bot Telegram
    token = os.getenv("8572769927:AAGQFgo-VfC7krJ30qbyM8N63jF0TdiB-s0")
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot & Web Server started...")
    app.run_polling()
