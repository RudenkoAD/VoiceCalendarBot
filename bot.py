import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Application
from telegram import Bot
import dotenv
dotenv.load_dotenv()
from whisperapi import WhisperAPI
from calendarapi import CalendarAPI
from openaiapi import OpenAIAPI
import os.path
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Define command handlers
async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот, который поможет тебе сделать запись в календарь, используя голосовые сообщения.")
    context.user_data["whisper"] = WhisperAPI()
    path = os.path.join("data", "user_creds", f"{update.effective_chat.id}.json")
    if os.path.exists(path):
      calendar = CalendarAPI(user_id=update.effective_chat.id)
      context.user_data["openai"] = OpenAIAPI(calendar=calendar)
      context.user_data["logged_in"] = True
    else:
      await login(update, context)
      
      
async def login(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Похоже, вы пока что не авторизованы.\nАвторизуйте бота в Google Calendar по ссылке: <a href = 'https://voicecalendarbot.ddns.net/login?id={update.effective_chat.id}'>Авторизация</a>, затем пропишите /start снова", parse_mode="HTML")
      
async def texthandler(update, context):
    if not context.user_data.get("logged_in", False):
      await login(update, context)
      return
    text=update.message.text
    response = context.user_data["openai"].run_conversation(text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def voicehandler(update, context):
    if not context.user_data.get("logged_in", False):
      await login(update, context)
      return
    new_file = await update.message.effective_attachment.get_file()
    await new_file.download_to_drive('data/temp/output.wav')
    text=context.user_data["whisper"].recognize_voice("data/temp/output.wav")
    response = context.user_data["openai"].run_conversation(text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    

# Set up the bot
def main():
    # Create the Updater and pass in your bot's token
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texthandler))
    app.add_handler(MessageHandler(filters.VOICE, voicehandler))
    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
