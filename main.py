import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Sujon HD Transcoder Ready!\nVideo pathao, ami 1080p 60fps 10Mbps H.264 file baniye debo.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Downloading...")
    try:
        file = await update.message.effective_attachment.get_file()
        input_path = "/tmp/input"
        output_path = "/tmp/output.mp4"
        await file.download_to_drive(input_path)
        await msg.edit_text("⚙️ Transcoding 1080p 60fps 10Mbps H.264...")

        cmd = ["ffmpeg","-y","-i",input_path,"-vf","scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fps=60","-r","60","-c:v","libx264","-preset","fast","-b:v","10M","-maxrate","10M","-bufsize","20M","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",output_path]
        subprocess.run(cmd, check=True)
        await msg.edit_text("📤 Uploading as file...")
        
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename="1080p_60fps_10Mbps_H264.mp4",
                caption="✅ Done: 1080p | 60fps | 10Mbps | H.264\nFile hisabe save koren"
            )
        await msg.delete()
        os.remove(input_path)
        os.remove(output_path)
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.run_polling()

if __name__ == "__main__":
    main()
