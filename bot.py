import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

# Constants
POLLINATIONS_API = "https://image.pollinations.ai/prompt"
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512

# Supported commands
COMMANDS = {
    "start": "Start the bot and see help",
    "help": "Get help and usage instructions",
    "about": "Learn about this bot",
    "info": "Get bot information"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Welcome message."""
    welcome_text = (
        "🎨 *Welcome to TextToImageBot!*\n\n"
        "I can generate images from your text descriptions using AI.\n\n"
        "*How to use:*\n"
        "• Simply send me any text description\n"
        "• Example: 'a beautiful sunset over mountains'\n"
        "• Example: 'a cat wearing a hat drinking coffee'\n\n"
        "Use /help for more commands."
    )
    keyboard = [
        [InlineKeyboardButton("📸 Example Prompts", callback_data="examples")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - Show help information."""
    help_text = (
        "🤖 *TextToImageBot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - Learn about this bot\n"
        "/info - Get bot information\n\n"
        "*How to generate images:*\n"
        "Just type any text description and I'll generate an image!\n\n"
        "*Tips:*\n"
        "• Be descriptive for better results\n"
        "• Use styles like 'watercolor', 'oil painting', '3d render'\n"
        "• Include lighting details for realistic images"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command - Show about information."""
    about_text = (
        "ℹ️ *About TextToImageBot*\n\n"
        "This bot uses Pollinations.ai API to generate images from text descriptions.\n\n"
        "*Features:*\n"
        "• Free text-to-image generation\n"
        "• No API keys required\n"
        "• Fast image generation\n"
        "• Various image styles available\n\n"
        "*Source Code:*\n"
        "GitHub: https://github.com/yourusername/text-to-image-bot"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /info command - Show bot information."""
    info_text = (
        "📊 *Bot Information*\n\n"
        f"• Bot Name: TextToImageBot\n"
        f"• User ID: {update.effective_user.id}\n"
        f"• Chat ID: {update.effective_chat.id}\n"
        "• Status: Active\n"
        "• Version: 1.0.0\n\n"
        "Powered by Pollinations.ai"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate an image from user's text prompt."""
    prompt = update.message.text.strip()
    
    # Validate prompt
    if len(prompt) < 3:
        await update.message.reply_text("⚠️ Please provide a longer description (at least 3 characters).")
        return
    
    if len(prompt) > 1000:
        await update.message.reply_text("⚠️ Please keep your description under 1000 characters.")
        return

    # Send processing message
    processing_msg = await update.message.reply_text(
        f"🎨 Generating image for:\n*{prompt[:50]}...*" if len(prompt) > 50 else f"🎨 Generating image for:\n*{prompt}*",
        parse_mode='Markdown'
    )
    
    logger.info(f"User {update.effective_user.id} generating image: '{prompt}'")

    try:
        # Construct API URL with parameters
        url = f"{POLLINATIONS_API}/{prompt}"
        params = {
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "nologo": "true",
            "enhance": "true"  # Enable enhancement for better quality
        }
        
        # Generate image
        response = requests.get(url, params=params, stream=True, timeout=60)
        
        if response.status_code == 200:
            # Delete processing message
            await processing_msg.delete()
            
            # Send the generated image
            await update.message.reply_photo(
                photo=response.content,
                caption=f"✅ Generated from: *{prompt[:100]}*" + ("..." if len(prompt) > 100 else ""),
                parse_mode='Markdown'
            )
            logger.info(f"Image sent to user {update.effective_user.id}")
        else:
            await processing_msg.edit_text(
                f"❌ Image generation failed. Please try again later.\nError: {response.status_code}"
            )
            logger.error(f"API error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        await processing_msg.edit_text("⏱️ The request timed out. Please try again.")
        logger.error(f"Timeout for user {update.effective_user.id}")
    except requests.exceptions.ConnectionError:
        await processing_msg.edit_text("🌐 Network error. Please check your connection and try again.")
        logger.error(f"Connection error for user {update.effective_user.id}")
    except Exception as e:
        await processing_msg.edit_text("❌ An unexpected error occurred. Please try again later.")
        logger.error(f"Error generating image: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks for inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "examples":
        examples_text = (
            "📸 *Example Prompts*\n\n"
            "*Art & Style:*\n"
            "• 'watercolor painting of a forest'\n"
            "• 'oil painting of a starry night'\n"
            "• '3D render of a modern house'\n"
            "• 'anime character in a cyberpunk city'\n\n"
            "*Nature:*\n"
            "• 'beautiful sunset over ocean waves'\n"
            "• 'cherry blossom tree in spring'\n"
            "• 'northern lights over mountains'\n\n"
            "*Animals:*\n"
            "• 'cute cat wearing a top hat'\n"
            "• 'lion in the savannah'\n"
            "• 'panda eating bamboo'\n\n"
            "*Feel free to get creative!* 🎨"
        )
        await query.edit_message_text(examples_text, parse_mode='Markdown')
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="back")]
        ]))
    
    elif query.data == "about":
        about_text = (
            "ℹ️ *About TextToImageBot*\n\n"
            "This bot generates images from text descriptions using Pollinations.ai API.\n\n"
            "*Technical Details:*\n"
            "• Built with Python and python-telegram-bot\n"
            "• Hosted on Railway\n"
            "• Uses Pollinations.ai for free image generation\n\n"
            "*Support:*\n"
            "For issues or suggestions, contact @your_support_username"
        )
        await query.edit_message_text(about_text, parse_mode='Markdown')
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="back")]
        ]))
    
    elif query.data == "back":
        start_text = (
            "🎨 *Welcome to TextToImageBot!*\n\n"
            "I can generate images from your text descriptions using AI.\n\n"
            "*How to use:*\n"
            "• Simply send me any text description\n"
            "• Example: 'a beautiful sunset over mountains'\n"
            "• Example: 'a cat wearing a hat drinking coffee'\n\n"
            "Use /help for more commands."
        )
        keyboard = [
            [InlineKeyboardButton("📸 Example Prompts", callback_data="examples")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
        await query.edit_message_text(start_text, parse_mode='Markdown')
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors globally."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        await update.message.reply_text("⚠️ An error occurred. Please try again later.")
    except:
        pass

def main():
    """Start the bot."""
    logger.info("🚀 Starting TextToImageBot...")
    
    # Build application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("info", info_command))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_image))
    
    # Add callback handler for inline keyboards
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Bot is ready!")
    application.run_polling(
        poll_interval=1.0,
        timeout=30,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
