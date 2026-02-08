import os
import re
import time
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# bot token
BOT_TOKEN = "!!!"

# regex for cloudflare URL
URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

tunnel_process = None

# --------------------------
# /expose command
# --------------------------
async def expose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tunnel_process

    if tunnel_process and tunnel_process.poll() is None:
        await update.message.reply_text("Tunnel already running ⚠️")
        return

    await update.message.reply_text("Starting Cloudflare tunnel... ⏳")

    cmd = [
        "cloudflared", "tunnel",
        "--url", "https://host.containers.internal:9090",
        "--no-tls-verify"
    ]

    tunnel_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    start_time = time.time()
    timeout = 20  # seconds

    for line in tunnel_process.stdout:
        match = URL_REGEX.search(line)
        if match:
            tunnel_url = match.group(0)
            await update.message.reply_text(f"Tunnel active 🚀\n{tunnel_url}")
            return

        if time.time() - start_time > timeout:
            await update.message.reply_text("Failed to get Cloudflare URL ⏱️")
            tunnel_process.terminate()
            tunnel_process = None
            return

# --------------------------
# /down command
# --------------------------
async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tunnel_process

    if not tunnel_process or tunnel_process.poll() is not None:
        await update.message.reply_text("No active tunnel.")
        tunnel_process = None
        return

    tunnel_process.terminate()
    tunnel_process = None
    await update.message.reply_text("Tunnel stopped ❌")

# --------------------------
# /start command
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot ready 🤖\n\n"
        "/expose → open cockpit\n"
        "/down → close tunnel"
    )

# --------------------------
# main
# --------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("expose", expose))
    app.add_handler(CommandHandler("down", down))

    print("Bot running...", flush=True)
    app.run_polling()

if __name__ == "__main__":
    main()
