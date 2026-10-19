import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Sujon TikTok Bot Ready!\nTikTok link pathao, ami HD video debo.")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ Valid TikTok link dao.")
        return

    await update.message.reply_text("⏳ Downloading...")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(api_url, headers=headers, timeout=15).json()
        
        if r.get("code") == 0:
            video_url = r["data"]["play"]
            await update.message.reply_video(video=video_url, caption="✅ Done by Sujon Bot")
        else:
            await update.message.reply_text("❌ Download failed, onno link try koro.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    print("Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
