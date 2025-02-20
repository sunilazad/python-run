import logging
import tracemalloc
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes)

# Enable nested event loops
nest_asyncio.apply()
tracemalloc.start()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    YOUR_BOT_TOKEN = os.environ["YOUR_BOT_TOKEN"]
except KeyError as e:
    YOUR_BOT_TOKEN = 'no bot-token found'
    logger.info(f'no bot-token found and error is {e}')

# Store recent messages
chat_history = []  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("You're talking to S Azad', How are you")

async def Help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("wait.. what type of help you want.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_history
    message = update.message.text
    chat_history.append(message)
    if len(chat_history) > 5:
        chat_history.pop(0)  # Keep only the last 5 messages
    await update.message.reply_text(message)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await update.message.reply_text(text_caps)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Terminating Bot...')
    application = context.application
    await application.stop()
    await application.shutdown()
    loop = asyncio.get_event_loop()
    loop.stop()  # Stop the event loop

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    err_msg = f"Update: {update}\nError: {context.error}"
    logging.error(err_msg, exc_info=context.error)
    if update and update.effective_chat:
        await update.message.reply_text(err_msg)

async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if chat_history:
        history_text = '\n'.join(chat_history)
        await update.message.reply_text(f"Recent messages:\n{history_text}")
    else:
        await update.message.reply_text("No recent messages.")

async def main():
    application = ApplicationBuilder().token(YOUR_BOT_TOKEN).build()
    
    # Add Handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', Help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler('caps', caps))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('recent', recent))
    application.add_error_handler(error)
    
    # Start bot
    await application.run_polling()

'''
try:
    loop = asyncio.get_running_loop()
    loop.stop()  # Stop any running loop
    loop.close()  # Close the loop
except RuntimeError as e:
    print(e) 
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
'''    
if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main())  # Schedule the bot in the existing event loop
        loop    #.run_forever()  # Keep the event loop running
        logger.info('Telegram Bot started')
    except error as e:
        logger.info(e)
