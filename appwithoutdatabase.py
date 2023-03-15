#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telebot import TeleBot
from datetime import date

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

# import mysql.connector
# from datetime import datetime
# import getpass

# db = mysql.connector.connect(host = "localhost",user = "root",passwd = "root",database = "HOTEL_MANAGEMENT")

# cur = db.cursor()

import json
import datetime
from json import JSONEncoder

class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

TOKEN = "6208047469:AAFmQNhFJMsPI-soY5HBWTPaO7kPGPDkaTQ"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSE, BOOK, PHONE, ROOMTYPE, CHECKIN, SELECTDATE, CHOOSEBOOKINGSOURCE, STATUS, PAYMENT, PARTIAL, DEPOSIT, DISPLAY, CONFIRM = range(
    13)
ONE, TWO, THREE, FOUR, FIVE, SIX = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Start the bot and ask what to do when the command /start is issued.
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("Book a new room", callback_data=str(ONE)),
            InlineKeyboardButton(
                "Check if there are any bookings on a specific date", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Adjust booking status",
                                 callback_data=str(THREE)),
            InlineKeyboardButton("Delete booking", callback_data=str(FOUR)),
        ],
        [
            InlineKeyboardButton("Reminder", callback_data=str(FIVE)),
            InlineKeyboardButton(
                "Check-in and payment marking", callback_data=str(SIX)),
        ],
    ]
    await update.message.reply_text(
        "Choose what to do",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHOOSE

guestinformation = {}


async def book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # You choosed booking a new room. Ask the guest's name
    query = update.callback_query
    user = query.from_user
    await query.answer()
    await query.message.edit_text("You are booking a new guest.\nEnter the guest's name")
    ForceReply(selective=True)

    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the entered name and ask the phone number
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    guestinformation["Name"] = update.message.text
    await update.message.reply_text(
        "Guest's name:"+guestinformation["Name"]+"\nEnter the phone number",
        reply_markup=ForceReply(selective=True),
    )

    return ROOMTYPE


async def roomtype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the entered phone number and ask type of room
    user = update.message.from_user
    logger.info("Phone number of %s: %s", user.first_name, update.message.text)
    guestinformation["Phone number"] = update.message.text
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="A"),
            InlineKeyboardButton("B1", callback_data="B1"),
            InlineKeyboardButton("B2", callback_data="B2"),
        ],
        [
            InlineKeyboardButton("C", callback_data="C"),
            InlineKeyboardButton("101", callback_data="101"),
            InlineKeyboardButton("102", callback_data="102"),
        ],
        [
            InlineKeyboardButton("201", callback_data=201),
            InlineKeyboardButton("202", callback_data=202),
            InlineKeyboardButton("full house", callback_data="fullhouse"),
        ],
    ]
    await update.message.reply_text(
        "Guest's phone number:"+guestinformation["Phone number"]+"\nChoose the type of room desired",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHECKIN


async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the type of room and ask check-in date
    query = update.callback_query
    user = query.from_user
    await query.answer()
    logger.info("Type of room for %s: %s",
                user.first_name, query.data)
    guestinformation["Type of room"] = query.data
    calendar, step = DetailedTelegramCalendar().build()
    await query.message.edit_text(
        "Type of room: " + guestinformation["Type of room"] + f"\nSelect {LSTEP[step]}",
        reply_markup=calendar
    )
    context.user_data["selectdate"] = "checkin"
    return SELECTDATE

async def selectdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the check-in date and ask check-out date
    query = update.callback_query
    user = query.from_user
    datetype = context.user_data["selectdate"]
    await query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        await query.message.edit_text(f"Select {LSTEP[step]}",
                            reply_markup=key)
    elif result:
        if datetype == "checkin":
            logger.info("Check-in date of %s: %s",
                    user.first_name, result)
            guestinformation["Check-in date"] = result
            context.user_data["selectdate"] = "checkout"
            calendar, step = DetailedTelegramCalendar().build()
            await query.message.edit_text(
                "Check-out date: "+json.dumps(guestinformation["Check-in date"], indent=4, cls=DateTimeEncoder)+f"\nSelect {LSTEP[step]}",
                reply_markup=calendar
            )
            return SELECTDATE
        elif datetype == "checkout":
            logger.info("Check-out date of %s: %s",
                    user.first_name, result)
            guestinformation["Check-out date"] = result
            keyboard = [
                [
                    InlineKeyboardButton("agoda", callback_data="agoda"),
                    InlineKeyboardButton("booking", callback_data="booking"),
                    InlineKeyboardButton(
                        "direct booking", callback_data="directbooking"),
                ]
            ]
            await query.message.edit_text(
                "Check-out date: "+json.dumps(guestinformation["Check-out date"], indent=4, cls=DateTimeEncoder)+"\nChoose the booking source",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return CHOOSEBOOKINGSOURCE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the booking source and ask the price for this booking
    query = update.callback_query
    user = query.from_user
    logger.info("Booking source of %s: %s",
                user.first_name, query.data)
    guestinformation["The booking source"] = query.data
    await query.answer()
    await query.message.edit_text("The booking source: " + guestinformation["The booking source"] + "\nEnter the price for this booking")
    ForceReply(selective=True)

    return STATUS


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the price of booking and choose between pay in full and partial deposit
    user = update.message.from_user
    logger.info("Price of booking for %s: %s",
                user.first_name, update.message.text)
    guestinformation["Price of booking"] = update.message.text
    keyboard = [
        [
            InlineKeyboardButton("Pay in full", callback_data="fullpay"),
            InlineKeyboardButton(
                "Partial deposit", callback_data="partial"),
        ]]
    await update.message.reply_text(
        "The booking price: " + guestinformation["Price of booking"] + "\nPay in full or partial deposit?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return PAYMENT


async def partial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose partial deposit. Ask the amount of deposit
    query = update.callback_query
    user = query.from_user
    logger.info("The user %s will pay partial deposit",
                user.first_name)
    guestinformation["Payment"] = query.data
    await query.answer()
    await query.message.edit_text("Enter the amount of deposit")
    ForceReply(selective=True)

    return DEPOSIT


async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the amount of deposit and go on to displaying all information
    user = update.message.from_user
    logger.info("The amount of deposit for %s: %s",
                user.first_name, update.message.text)
    guestinformation["Deposit"] = update.message.text
    await update.message.reply_text(
        "You have chosen partial deposit. Deposit: " + guestinformation["Deposit"] + "\nType anything to see the guest information",
        reply_markup=ForceReply(selective=True)
    )

    return DISPLAY


async def fullpay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose fullpay and go on to dispaying all information
    query = update.callback_query
    user = query.from_user
    await query.answer()
    logger.info("The user %s will pay full",
                user.first_name)
    guestinformation["Payment"] = "Full payment"
    guestinformation["Deposit"] = 0
    await query.message.edit_text("You have chosen full payment\nType anything to see the guest information")
    ForceReply(selective=True)

    return DISPLAY

async def display(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the price of booking and choose between pay in full and partial deposit
    user = update.message.from_user
    logger.info("View information of %s",
            user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data="confirm"),
            InlineKeyboardButton("Cancel", callback_data="cancel"),
        ]]
    viewinfo = json.dumps(guestinformation, indent=4, cls=DateTimeEncoder)
    await update.message.reply_text(
        viewinfo,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Confirm booking
    query = update.callback_query
    user = query.from_user
    await query.answer()
    await query.message.edit_text("Confirmed")
    # query = "insert into customer_data values ('{}','{}','{}','{}','{}')".format(cid, name, age, add, email)
    # cur.execute(query)
    # db.commit()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Cancel booking
    query = update.callback_query
    user = query.from_user
    await query.answer()
    await query.message.edit_text("Canceled")

    return ConversationHandler.END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE: [CallbackQueryHandler(book, pattern="^" + str(ONE) + "$"),
                     CallbackQueryHandler(book, pattern="^" + str(TWO) + "$"),
                     CallbackQueryHandler(
                         book, pattern="^" + str(THREE) + "$"),
                     CallbackQueryHandler(book, pattern="^" + str(FOUR) + "$"),
                     CallbackQueryHandler(book, pattern="^" + str(FIVE) + "$"),
                     CallbackQueryHandler(book, pattern="^" + str(SIX) + "$")],
            BOOK: [MessageHandler(filters.TEXT, book)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            ROOMTYPE: [MessageHandler(filters.TEXT, roomtype)],
            CHECKIN: [CallbackQueryHandler(checkin)],
            SELECTDATE: [CallbackQueryHandler(selectdate)],
            CHOOSEBOOKINGSOURCE: [CallbackQueryHandler(price)],
            STATUS: [MessageHandler(filters.TEXT, status)],
            PAYMENT: [CallbackQueryHandler(partial, pattern="partial"),
                      CallbackQueryHandler(fullpay, pattern="fullpay"),],
            DEPOSIT: [CallbackQueryHandler(deposit)],
            DISPLAY: [MessageHandler(filters.TEXT, display)],
            CONFIRM: [CallbackQueryHandler(confirm, pattern="confirm"),
                      CallbackQueryHandler(cancel, pattern="cancel"),],
        },
        fallbacks=[CommandHandler("end", end)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
