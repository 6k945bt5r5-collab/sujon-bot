import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8470709607:AAGqjE5VBaRvdNinN0XXN5G2oiN5GUPP7OE"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! TikTok link pathao!")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        await update.message.reply_text("Valid link deo!")
        return
    msg = await update.message.reply_text("Download kortesi...")
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}).json()
        if res["code"] == 0:
            video_url = res["data"]["play"]
            await msg.delete()
            await update.message.reply_video(video=video_url)
        else:
            await msg.edit_text("Video paoa jay nai!")
    except Exception as e:
        await msg.edit_text(f"Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    app.run_polling()

if __name__ == "__main__":
    main()
