import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    logger.error("No token found!")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me any text and I'll generate an image!")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text(f"Generating: {prompt}...")
    
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            await update.message.reply_photo(response.content)
        else:
            await update.message.reply_text("Failed to generate image.")
    except Exception as e:
        await update.message.reply_text("Error generating image.")
        logger.error(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    logger.info("Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
