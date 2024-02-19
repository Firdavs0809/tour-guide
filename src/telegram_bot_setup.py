# import os
# from dotenv import load_dotenv
#
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
#
# load_dotenv()
# TOKEN = os.getenv('TG_TOKEN')
#
#
# async def start_(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         tg_username = update.effective_user.username
#         print(tg_username)
#         from tour.agency.models import Company
#         chat_id = update.message.chat_id
#         company = Company.objects.filter(tg_username=tg_username).first()
#         company.chat_id = chat_id
#         company.save()
#     except Exception as e:
#         print(e.args)
#     await update.message.reply_text(f"Welcome "
#                                     f"{update.effective_user.first_name}! It's a Tour Guide bot. Your clients get in "
#                                     f"touch with "
#                                     f"you through this bot. Stay Tuned!")
#
#
# async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(f"Write your question in here. We will get to you soon!")
#
#
# async def custom_(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(f"Welcome "
#                                     f"{update.effective_user.first_name}! It's a Tour Guide bot. Your clients get in touch with "
#                                     f"you through this bot. Stay Tuned!")
#
#
# def handle_response(text: str):
#     if 'hello' in text.lower():
#         return 'Hey there, How can I help you!'
#
#     if 'how are you' in text.lower():
#         return 'Hey there,I am ok. How can I help you!'
#
#     return 'I don\'t understand you'
#
#
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     message_type = update.message.chat.type
#     text: str = context.message.text
#
#     if message_type == 'group':
#         response = ''
#     else:
#         response = handle_response(text)
#
#     await update.message.reply_text(response)
#
#
# def setup():
#     app = Application.builder().token(TOKEN).build()
#     app.add_handler(CommandHandler('start', start_))
#     app.add_handler(CommandHandler('help', help_))
#     app.add_handler(CommandHandler('custom', custom_))
#
#     # app.add_handler(MessageHandler(filters.TEXT, handle_message))
#
#     app.run_polling(poll_interval=1)
