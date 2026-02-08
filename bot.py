import os

import re

import time

import subprocess

from telegram import Update

from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


# --------------------------

# MASUKKAN TOKEN BOT DI SINI

# --------------------------

BOT_TOKEN = "8259462768:AAEoz4v87wTOGO68R1crGJWn4rdeNR6qwr8"


# regex untuk menangkap link trycloudflare

URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


tunnel_process = None


# --------------------------

# Command /expose

# --------------------------

async def expose(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global tunnel_process


    if tunnel_process and tunnel_process.poll() is None:

        await update.message.reply_text("Tunnel sudah aktif ⚠️")

        return


    await update.message.reply_text("Menyalakan tunnel Cloudflare... ⏳")


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

    timeout = 20  # detik


    for line in tunnel_process.stdout:

        match = URL_REGEX.search(line)

        if match:

            tunnel_url = match.group(0)

            await update.message.reply_text(

                f"Expose aktif 🚀\n{tunnel_url}"

            )

            return


        if time.time() - start_time > timeout:

            await update.message.reply_text(

                "Gagal mendapatkan link Cloudflare ⏱️"

            )

            tunnel_process.terminate()

            tunnel_process = None

            return


# --------------------------

# Command /down

# --------------------------

async def down(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global tunnel_process


    if not tunnel_process or tunnel_process.poll() is not None:

        await update.message.reply_text("Tidak ada tunnel yang aktif.")

        tunnel_process = None

        return


    tunnel_process.terminate()

    tunnel_process = None

    await update.message.reply_text("Tunnel dimatikan ❌")


# --------------------------

# Command /start

# --------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(

        "Bot Exposer siap 🤖\n\n"

        "/expose  → buka akses cockpit\n"

        "/down    → tutup akses"

    )


# --------------------------

# MAIN

# --------------------------

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()


    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("expose", expose))

    app.add_handler(CommandHandler("down", down))


    print("Bot berjalan...", flush=True)

    app.run_polling()



if __name__ == "__main__":

    main()

