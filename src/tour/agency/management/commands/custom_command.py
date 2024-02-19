from django.core.management.base import BaseCommand
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from tour.agency.models import Company

load_dotenv()
TOKEN = os.getenv('TG_TOKEN')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        setup()


async def start_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tg_username = update.effective_user.username
        print(tg_username)
        chat_id = update.message.chat_id
        company = Company.objects.filter(tg_username=tg_username).first()
        company.chat_id = chat_id
        company.save()
    except Exception as e:
        print(e.args)
    await update.message.reply_text(f"Welcome "
                                    f"{update.effective_user.first_name}! It's a Tour Guide bot. Your clients get in "
                                    f"touch with "
                                    f"you through this bot. Stay Tuned!")


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Write your question in here. We will get to you soon!")


async def custom_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Welcome "
                                    f"{update.effective_user.first_name}! It's a Tour Guide bot. Your clients get in touch with "
                                    f"you through this bot. Stay Tuned!")


def setup():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_))
    app.add_handler(CommandHandler('help', help_))
    app.add_handler(CommandHandler('custom', custom_))

    app.run_polling(poll_interval=1)
