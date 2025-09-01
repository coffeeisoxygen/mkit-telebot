from loguru import logger
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Replace with your actual bot token
TOKEN = "yourtokenhere"

logger.add("bot.log", rotation="1 week", retention="1 month")


async def start(update, context):
    """Handles the /start command."""
    logger.info(f"/start command received from user_id={update.effective_user.id}")
    await update.message.reply_text("Hello! I am your Telegram bot.")


async def echo(update, context):
    """Echos back any text message."""
    logger.info(
        f"Echoing message from user_id={update.effective_user.id}: {update.message.text}"
    )
    await update.message.reply_text(update.message.text)


def main():
    """Starts the bot."""
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start polling for updates
    application.run_polling()


if __name__ == "__main__":
    main()
