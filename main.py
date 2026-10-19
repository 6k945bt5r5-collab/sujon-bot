import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import subprocess
import tempfile
import imageio_ffmpeg

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Render ke khushi korar jonno fake web server ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sujon HD Bot is Running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()
# --- Fake server sesh ---

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Downloading...")
    file = await context.bot.get_file(update.message.video or update.message.document)
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "input.mp4")
        out_path = os.path.join(tmp, "output.mp4")
        await file.download_to_drive(in_path)

        await update.message.reply_text("⚙️ Transcoding 1080p 60fps 10Mbps H.264...")

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe, "-i", in_path,
            "-vf", "scale=1920:1080:flags=lanczos",
            "-r", "60",
            "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-b:v", "10M", "-maxrate", "10M", "-bufsize", "20M",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            out_path
        ]
        subprocess.run(cmd, check=True)
        await update.message.reply_text("📤 Uploading as file...")
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(out_path, 'rb'))

if __name__ == "__main__":
    print("Sujon HD Bot Started - 1080p 60fps 10Mbps")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.run_polling()
