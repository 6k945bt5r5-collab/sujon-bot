import os, tempfile, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import imageio_ffmpeg

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
