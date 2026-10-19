import os, tempfile, asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import imageio_ffmpeg

# --- 1. PORT FIX - Ei part ta add korechi jate Render e No open ports error na ase ---
web_app = Flask(__name__)
@web_app.route('/')
def home():
    return "Sujon Bot is Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
# --- END FIX ---

BOT_TOKEN = os.getenv("BOT_TOKEN")
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Sujon TikTok Bot Ready! Video pathao, ami HD kore debo.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Downloading...")
    try:
        file = await update.message.video.get_file()
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.mp4")
            output_path = os.path.join(tmp, "output.mp4")
            await file.download_to_drive(input_path)

            await msg.edit_text("⚙️ Transcoding 1080p 60fps 10Mbps H.264...")

            # 1080p + 60fps + 10Mbps + H.264
            proc = await asyncio.create_subprocess_exec(
                ffmpeg_path, "-y", "-i", input_path,
                "-vf", "scale=-2:1080,fps=60",
                "-r", "60",
                "-c:v", "libx264", "-profile:v", "high", "-preset", "ultrafast",
                "-b:v", "10M", "-maxrate", "10M", "-bufsize", "20M",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                output_path
            )
            await proc.communicate()

            await msg.edit_text("⬆️ Uploading...")
            await update.message.reply_video(video=open(output_path, 'rb'), caption="✅ 1080p 60fps 10Mbps H.264 Done")
            await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.run_polling()
