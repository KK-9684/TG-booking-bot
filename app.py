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

from json import JSONEncoder
import datetime
import json
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
from telegram import ForceReply, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telebot import TeleBot


from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

import mysql.connector

db = mysql.connector.connect(
    host="localhost", user="root", passwd="", database="test1")

cur = db.cursor()


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

CHOOSE, BOOK, PHONE, ROOMTYPE, CHECKIN, SELECTDATE, CHOOSEBOOKINGSOURCE, STATUS, PAYMENT, PARTIAL, DEPOSIT, DISPLAY, CONFIRM, CHECKOUTDATETOCHECK, DATECHECKED, CHECKROOMTYPE, CONFIRMSELECTION, SELECTADJUST, CONFIRMDELETE, VIEWDELETE, REMINDER, SELECTMARK, MARKANDPAY = range(
    23)
# DATECHECKED, CHECKROOMTYPE, DISPLAYCHECKED, CONFIRMSELECTION = range(4)
# DATECHECKED, CHECKROOMTYPE = range(2)
guestinformation = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Start the bot and ask what to do when the command /start is issued.
    user = update.effective_user
    guestinformation = {}
    if context.user_data.get("adjustID"):
        context.user_data["adjustID"]=""
    keyboard = [
        [
            InlineKeyboardButton(
                "Book a new room", callback_data="Book a new room"),
            InlineKeyboardButton(
                "Check if there are any bookings on a specific date", callback_data="Check if there are any bookings on a specific date"),
        ],
        [
            InlineKeyboardButton("Adjust booking status",
                                 callback_data="Adjust booking status"),
            InlineKeyboardButton(
                "Delete booking", callback_data="Delete booking"),
        ],
        [
            InlineKeyboardButton("Reminder", callback_data="Reminder"),
            InlineKeyboardButton(
                "Check-in and payment marking", callback_data="Check-in and payment marking"),
        ]
    ]
    await update.message.reply_text(
        "Choose what to do",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHOOSE


##########################################################################################
# 1. Booking A New Room
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose booking a new room. Ask the guest's name
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
            InlineKeyboardButton("201", callback_data="201"),
            InlineKeyboardButton("202", callback_data="202"),
            InlineKeyboardButton("full house", callback_data="fullhouse"),
        ],
    ]
    await update.message.reply_text(
        "Guest's phone number:" +
        guestinformation["Phone number"]+"\nChoose the type of room desired",
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
        "Type of room: " +
        guestinformation["Type of room"] + f"\nChoose check-in date\nSelect {LSTEP[step]}",
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
        return SELECTDATE
    elif result:
        if datetype == "checkin":
            logger.info("Check-in date of %s: %s",
                        user.first_name, result)
            guestinformation["Check-in date"] = result
            context.user_data["selectdate"] = "checkout"
            calendar, step = DetailedTelegramCalendar().build()
            await query.message.edit_text(
                "Check-in date: " +
                json.dumps(guestinformation["Check-in date"], indent=4,
                           cls=DateTimeEncoder)+f"\nChoose check-out date\nSelect {LSTEP[step]}",
                reply_markup=calendar
            )
            return SELECTDATE
        elif datetype == "checkout":
            logger.info("Check-out date of %s: %s",
                        user.first_name, result)
            guestinformation["Check-out date"] = result
            keyboard = [
                [
                    InlineKeyboardButton("Agoda", callback_data="Agoda"),
                    InlineKeyboardButton("booking", callback_data="booking"),
                    InlineKeyboardButton(
                        "direct booking", callback_data="directbooking"),
                ]
            ]
            await query.message.edit_text(
                "Check-out date: " +
                json.dumps(guestinformation["Check-out date"], indent=4,
                           cls=DateTimeEncoder)+"\nChoose the booking source",
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
        "The booking price: " +
        guestinformation["Price of booking"] +
        "\nPay in full or partial deposit?",
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
        "You have chosen partial deposit. Deposit: " +
        guestinformation["Deposit"] +
        "\nType anything to see the guest information",
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
    Name = guestinformation["Name"]
    PhoneNumber = guestinformation["Phone number"]
    match guestinformation["Type of room"]:
        case "A":
            RoomNumber= 1
        case "B1":
            RoomNumber = 2
        case "B2":
            RoomNumber = 3
        case "C":
            RoomNumber = 4
        case "101":
            RoomNumber = 5
        case "102":
            RoomNumber = 6
        case "201":
            RoomNumber = 7
        case "202":
            RoomNumber = 8
        case _:
            RoomNumber = 9
    CheckInDate = guestinformation["Check-in date"]
    CheckOutDate = guestinformation["Check-out date"]
    match guestinformation["The booking source"]:
        case "Agoda":
            BookingSource = 1
        case "booking":
            BookingSource = 2
        case _:
            BookingSource = 3
    Price = guestinformation["Price of booking"]
    match guestinformation["Payment"]:
        case "Full payment":
            Payment = 1
        case _:
            Payment = 0
    Deposit = guestinformation["Deposit"]
    if context.user_data.get("adjustID"):
        sqlquery = "UPDATE book SET Name = '{}', PhoneNumber = '{}', TypeOfRoom = '{}', CheckInDate = '{}', CheckOutDate = '{}', BookingSource = '{}', Price = '{}', Payment = '{}', Deposit = '{}' WHERE BookID = '{}'".format(
        Name, PhoneNumber, RoomNumber, CheckInDate, CheckOutDate, BookingSource, Price, Payment, Deposit, context.user_data["adjustID"])
        cur.execute(sqlquery)
        db.commit()
        await query.message.edit_text("Adjusted\nIf you want to do something else, enter /start")
    else:
        sqlquery = "insert into book (Name, PhoneNumber, TypeOfRoom, CheckInDate, CheckOutDate, BookingSource, Price, Payment, Deposit) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
        Name, PhoneNumber, RoomNumber, CheckInDate, CheckOutDate, BookingSource, Price, Payment, Deposit)
        cur.execute(sqlquery)
        db.commit()
        await query.message.edit_text("Confirmed\nIf you want to do something else, enter /start")
##########################################################################################
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Cancel booking
    query = update.callback_query
    user = query.from_user
    await query.answer()
    await query.message.edit_text("Canceled\nIf you want to do something else, enter /start")

##########################################################################################
# 2. Check On A Specific Date For Specific Roomtype
checkinformation = {}
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose checking on a specific date. Choose the date to check
    query = update.callback_query
    user = query.from_user
    await query.answer()
    calendar, step = DetailedTelegramCalendar().build()
    await query.message.edit_text(
        "Check if there are any bookings on a specific date\nEnter the check-in date to check" +
        f"\nSelect {LSTEP[step]}",
        reply_markup=calendar
    )

    return CHECKOUTDATETOCHECK

async def checkoutdatetocheck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose checking on a specific date. Choose the date to check
    query = update.callback_query
    user = query.from_user
    await query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        await query.message.edit_text(f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        checkinformation["CheckInDate"] = result
        calendar, step = DetailedTelegramCalendar().build()
        await query.message.edit_text(
            "Check-in Date to check: " + json.dumps(checkinformation["CheckInDate"], indent=4, cls=DateTimeEncoder)+"\nEnter the check-out date to check", reply_markup=calendar
        )
        return DATECHECKED

async def datechecked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store the checked date and choose room type to check
    query = update.callback_query
    user = query.from_user
    await query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        await query.message.edit_text(f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        checkinformation["CheckOutDate"] = result
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
                InlineKeyboardButton("201", callback_data="201"),
                InlineKeyboardButton("202", callback_data="202"),
                InlineKeyboardButton("full house", callback_data="fullhouse"),
            ],
        ]
        await query.message.edit_text(
            "Check-out Date to check: " + json.dumps(checkinformation["CheckOutDate"], indent=4, cls=DateTimeEncoder)+"\nChoose the booking source", reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return CHECKROOMTYPE

async def selectroomtype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Store and display what to check. Choose confirm or cancel.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    keyboard = [
    [
        InlineKeyboardButton("Confirm", callback_data="confirmchecked"),
        InlineKeyboardButton("Cancel", callback_data="cancelchecked"),
    ]]
    checkinformation["CheckRoomType"] = query.data
    await query.message.edit_text("Check-in Date to check: " + json.dumps(checkinformation["CheckInDate"], indent=4, cls=DateTimeEncoder) + "\nCheck-out Date to check: " + json.dumps(checkinformation["CheckOutDate"], indent=4, cls=DateTimeEncoder) + "\nThe room type to check: " + checkinformation["CheckRoomType"] + "\nCheck or Cancel?", reply_markup=InlineKeyboardMarkup(keyboard))

    return CONFIRMSELECTION

async def confirmchecked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Confirm is selected. Check the database
    query = update.callback_query
    user = query.from_user
    await query.answer()
    match checkinformation["CheckRoomType"]:
        case "A":
            RoomNumber = 1
        case "B1":
            RoomNumber = 2
        case "B2":
            RoomNumber = 3
        case "C":
            RoomNumber = 4
        case "101":
            RoomNumber = 5
        case "102":
            RoomNumber = 6
        case "201":
            RoomNumber = 7
        case "202":
            RoomNumber = 8
        case _:
            RoomNumber = 9
    sqlquery = "SELECT * FROM book WHERE ((CheckInDate <= '{}' AND CheckOutDate > '{}') OR (CheckInDate >= '{}' AND CheckInDate < '{}')) AND TypeOfRoom = {}".format(checkinformation["CheckInDate"], checkinformation["CheckInDate"], checkinformation["CheckInDate"], checkinformation["CheckOutDate"], RoomNumber)
    cur.execute(sqlquery)
    records = cur.fetchall()
    displayinfo = ""
    if records:
        for viewmessage in records:
            #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
            match viewmessage[6]:
                case 1:
                    BookingSource = "Agoda"
                case 2:
                    BookingSource = "Booking"
                case _:
                    BookingSource = "Direct booking"
            match viewmessage[8]:
                case 0:
                    paymentstatus="Full payment"
                case _:
                    paymentstatus=f"Deposit: {viewmessage[9]}"
            displayinfo += f"Name: {viewmessage[1]}\nPhone Number: {viewmessage[2]}\nCheck-in date: {viewmessage[4]}\nCheck-out date: {viewmessage[5]}\nBooking Source: {BookingSource}\nPayment Status: {paymentstatus}\n"
        await query.message.edit_text("There are bookings already.\n" + displayinfo + "If you want to do something, else enter /start")
    else:
        await query.message.edit_text("There is no booking for the conditions below.\nCheck-in Date to check: " + json.dumps(checkinformation["CheckInDate"], indent=4, cls=DateTimeEncoder) + "\nCheck-out Date to check: " + json.dumps(checkinformation["CheckOutDate"], indent=4, cls=DateTimeEncoder) + "\nThe room type to check: " + checkinformation["CheckRoomType"] + "\nYou can book.\nIf you want to do something, else enter /start")

##########################################################################################
# 3. Adjust Booking Status
async def adjust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose adjusting booking status. Display all upcoming bookings
    query = update.callback_query
    user = query.from_user
    await query.answer()
    sqlquery = "SELECT * FROM book WHERE CheckInDate >= '{}'".format(datetime.date.today())
    cur.execute(sqlquery)
    records = cur.fetchall()
    displayinfo = ""
    keyboard = []
    if records:
        for viewmessage in records:
            #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
            match viewmessage[3]:
                case 1:
                    Roomtype = "A"
                case 2:
                    Roomtype = "B1"
                case 3:
                    Roomtype = "B2"
                case 4:
                    Roomtype = "C"
                case 5:
                    Roomtype = "101"
                case 6:
                    Roomtype = "102"
                case 7:
                    Roomtype = "201"
                case 8:
                    Roomtype = "202"
                case _:
                    Roomtype = "full house"
            displayinfo = f"Name: {viewmessage[1]}, Type of room: {Roomtype}, Check-in date: {viewmessage[4]}, Check-out date: {viewmessage[5]}"
            keyboard.append([InlineKeyboardButton(displayinfo, callback_data=viewmessage[0])])
        await query.message.edit_text("Select the booking to adjust",reply_markup=InlineKeyboardMarkup(keyboard))

        return SELECTADJUST
    else:
        await query.message.edit_text("There is no upcoming booking data\nIf you want to do something, else enter /start")

async def selectadjust(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected a booking to adjust. Enter the guest's name
    query = update.callback_query
    user = query.from_user
    await query.answer()
    adjustID = query.data
    context.user_data["adjustID"] = adjustID
    sqlquery = "SELECT * FROM book WHERE BookID = {}".format(adjustID)
    cur.execute(sqlquery)
    viewmessage = cur.fetchone()
    displayinfo = ""
    #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
    match viewmessage[6]:
        case 1:
            BookingSource = "Agoda"
        case 2:
            BookingSource = "Booking"
        case _:
            BookingSource = "Direct booking"
    match viewmessage[8]:
        case 0:
            paymentstatus="Full payment"
        case _:
            paymentstatus=f"Deposit: {viewmessage[9]}"
    match viewmessage[3]:
        case 1:
            Roomtype = "A"
        case 2:
            Roomtype = "B1"
        case 3:
            Roomtype = "B2"
        case 4:
            Roomtype = "C"
        case 5:
            Roomtype = "101"
        case 6:
            Roomtype = "102"
        case 7:
            Roomtype = "201"
        case 8:
            Roomtype = "202"
        case _:
            Roomtype = "full house"
    displayinfo += f"Name: {viewmessage[1]}\nPhone Number: {viewmessage[2]}\nType of room: {Roomtype}\nCheck-in date: {viewmessage[4]}\nCheck-out date: {viewmessage[5]}\nBooking Source: {BookingSource}\nPrice: {viewmessage[7]}\nPayment Status: {paymentstatus}\n"
    
    await query.message.edit_text("You are adjusting this booking\n" + displayinfo + "Enter the guest's name")

    ForceReply(selective=True)

    return PHONE
##########################################################################################
# 4. Delete Booking
async def deletebooking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose deleting booking. Select one to delete
    query = update.callback_query
    user = query.from_user
    await query.answer()
    sqlquery = "SELECT * FROM book WHERE CheckInDate >= '{}'".format(datetime.date.today())
    cur.execute(sqlquery)
    records = cur.fetchall()
    displayinfo = ""
    keyboard = []
    if records:
        for viewmessage in records:
            #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
            match viewmessage[3]:
                case 1:
                    Roomtype = "A"
                case 2:
                    Roomtype = "B1"
                case 3:
                    Roomtype = "B2"
                case 4:
                    Roomtype = "C"
                case 5:
                    Roomtype = "101"
                case 6:
                    Roomtype = "102"
                case 7:
                    Roomtype = "201"
                case 8:
                    Roomtype = "202"
                case _:
                    Roomtype = "full house"
            displayinfo = f"Name: {viewmessage[1]}, Type of room: {Roomtype}, Check-in date: {viewmessage[4]}, Check-out date: {viewmessage[5]}"
            keyboard.append([InlineKeyboardButton(displayinfo, callback_data=viewmessage[0])])
        await query.message.edit_text("Select the booking to adjust",reply_markup=InlineKeyboardMarkup(keyboard))

        return VIEWDELETE
    else:
        print(sqlquery)
        await query.message.edit_text("There is no upcoming booking data\nIf you want to do something, else enter /start")

async def viewdelete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected one booking. View selected booking.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    deleteID = query.data
    context.user_data["deleteID"] = deleteID
    sqlquery = "SELECT * FROM book WHERE BookID = {}".format(deleteID)
    cur.execute(sqlquery)
    viewmessage = cur.fetchone()
    displayinfo = ""
    #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
    match viewmessage[6]:
        case 1:
            BookingSource = "Agoda"
        case 2:
            BookingSource = "Booking"
        case _:
            BookingSource = "Direct booking"
    match viewmessage[8]:
        case 0:
            paymentstatus="Full payment"
        case _:
            paymentstatus=f"Deposit: {viewmessage[9]}"
    match viewmessage[3]:
        case 1:
            Roomtype = "A"
        case 2:
            Roomtype = "B1"
        case 3:
            Roomtype = "B2"
        case 4:
            Roomtype = "C"
        case 5:
            Roomtype = "101"
        case 6:
            Roomtype = "102"
        case 7:
            Roomtype = "201"
        case 8:
            Roomtype = "202"
        case _:
            Roomtype = "full house"
    displayinfo += f"Name: {viewmessage[1]}\nPhone Number: {viewmessage[2]}\nType of room: {Roomtype}\nCheck-in date: {viewmessage[4]}\nCheck-out date: {viewmessage[5]}\nBooking Source: {BookingSource}\nPrice: {viewmessage[7]}\nPayment Status: {paymentstatus}\n"
    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data="confirmdelete"),
            InlineKeyboardButton("Cancel", callback_data="canceldelete"),
        ]]
    await query.message.edit_text("You are deleting this booking\n" + displayinfo + "\nConfirm?", reply_markup=InlineKeyboardMarkup(keyboard))

    return CONFIRMDELETE

async def confirmdelete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected one booking. View selected booking.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    #context.user_data["deleteID"]
    sqlquery = "DELETE FROM book WHERE BookID = '{}'".format(context.user_data["deleteID"])
    cur.execute(sqlquery)
    db.commit()
    await query.message.edit_text("Deleted\nIf you want to do something else, enter /start")

##########################################################################################
# 5. Reminder
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected Reminder. View bookings.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    keyboard = [
                [
                    InlineKeyboardButton("Today's check-out bookings", callback_data="TodayCheckout"),
                    InlineKeyboardButton(
                        "Bookings that will continue their stay", callback_data="ContinueStay"),
                ]
            ]
    await query.message.edit_text(
        "Choose which bookings you want to have a look at",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return REMINDER

async def viewreminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected Reminder. View bookings.
    query = update.callback_query
    user = query.from_user
    match query.data:
        case "TodayCheckout":
            replymessage="Today's check-out bookings:\n"
            missmessage="There is no Today's check-out bookings\nIf you want to do something else, enter /start"
            sqlquery = "SELECT * FROM book WHERE CheckOutDate = '{}'".format(datetime.date.today())
        case _:
            replymessage="Bookings that will continue their stay:\n"
            missmessage="There is no Bookings that will continue their stay\nIf you want to do something else, enter /start"
            sqlquery = "SELECT * FROM book WHERE CheckInDate <= '{}' AND CheckOutDate > '{}'".format(datetime.date.today(), datetime.date.today())
    cur.execute(sqlquery)
    records = cur.fetchall()
    displayinfo = ""
    keyboard = []
    if records:
        for viewmessage in records:
            #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
            match viewmessage[3]:
                case 1:
                    Roomtype = "A"
                case 2:
                    Roomtype = "B1"
                case 3:
                    Roomtype = "B2"
                case 4:
                    Roomtype = "C"
                case 5:
                    Roomtype = "101"
                case 6:
                    Roomtype = "102"
                case 7:
                    Roomtype = "201"
                case 8:
                    Roomtype = "202"
                case _:
                    Roomtype = "full house"
            match viewmessage[6]:
                case 1:
                    BookingSource = "Agoda"
                case 2:
                    BookingSource = "Booking"
                case _:
                    BookingSource = "Direct booking"
            match viewmessage[8]:
                case 0:
                    paymentstatus="Full payment"
                case _:
                    paymentstatus=f"Deposit: {viewmessage[9]}"
            displayinfo += f"Name: {viewmessage[1]}\nPhone Number: {viewmessage[2]}\nType of room: {Roomtype}\nCheck-in date: {viewmessage[4]}\nCheck-out date: {viewmessage[5]}\nBooking Source: {BookingSource}\nPrice: {viewmessage[7]}\nPayment Status: {paymentstatus}\n\n"
        replymessage += displayinfo + "If you want to do something else, enter /start"
    else:
        replymessage = missmessage
    keyboard = [
            [
                InlineKeyboardButton("Today's check-out bookings", callback_data="TodayCheckout"),
                InlineKeyboardButton(
                    "Bookings that will continue their stay", callback_data="ContinueStay"),
            ]
        ]
    await query.message.edit_text(replymessage, reply_markup=InlineKeyboardMarkup(keyboard))
    return REMINDER

##########################################################################################
# 6. Check-in and payment marking
async def viewrecent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected Check-in and payment marking. View bookings with check-in date of today, yesterday and tomorrow.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    sqlquery = "SELECT * FROM book WHERE CheckInDate >= DATE_SUB(CURDATE(), INTERVAL 1 DAY) AND CheckInDate <= DATE_ADD(CURDATE(), INTERVAL 1 DAY)"
    cur.execute(sqlquery)
    records = cur.fetchall()
    displayinfo = ""
    keyboard = []
    if records:
        for viewmessage in records:
            #viewmessage:(2, 'Jack', 401, 1, datetime.date(2023, 2, 21), datetime.date(2023, 12, 31), 3, 1320.0, 1, 100.0, None, None) <class 'tuple'
            match viewmessage[3]:
                case 1:
                    Roomtype = "A"
                case 2:
                    Roomtype = "B1"
                case 3:
                    Roomtype = "B2"
                case 4:
                    Roomtype = "C"
                case 5:
                    Roomtype = "101"
                case 6:
                    Roomtype = "102"
                case 7:
                    Roomtype = "201"
                case 8:
                    Roomtype = "202"
                case _:
                    Roomtype = "full house"
            match viewmessage[6]:
                case 1:
                    BookingSource = "Agoda"
                case 2:
                    BookingSource = "Booking"
                case _:
                    BookingSource = "Direct booking"
            match viewmessage[8]:
                case 0:
                    paymentstatus="Full payment"
                case _:
                    paymentstatus=f"Deposit: {viewmessage[9]}"
            displayinfo = f"Name: {viewmessage[1]}, Phone Number: {viewmessage[2]}, Type of room: {Roomtype}, Check-in date: {viewmessage[4]}, Check-out date: {viewmessage[5]}, Booking Source: {BookingSource}, Price: {viewmessage[7]}, Payment Status: {paymentstatus}"
            keyboard.append([InlineKeyboardButton(displayinfo, callback_data=viewmessage[0])])
        await query.message.edit_text("Select the booking to adjust",reply_markup=InlineKeyboardMarkup(keyboard))

        return SELECTMARK
    else:
        await query.message.edit_text("There is no recent checked-in booking\nIf you want to do something, else enter /start")

async def selectmark(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected Reminder. View bookings.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    context.user_data["adjustID"] = query.data
    keyboard = [
                [
                    InlineKeyboardButton("Check-in mark", callback_data="Check-in mark"),
                    InlineKeyboardButton("Absent mark", callback_data="Absent mark"),
                    InlineKeyboardButton(
                        "Payment status", callback_data="Payment status"),
                ]
            ]
    await query.message.edit_text(
        "Choose one mark",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MARKANDPAY

async def markandpay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You selected Reminder. View bookings.
    query = update.callback_query
    user = query.from_user
    await query.answer()
    markID = query.data
    match markID:
        case "Check-in mark":
            sqlquery = "UPDATE book SET CheckedIn = 1 WHERE BookID = '{}'".format(context.user_data["adjustID"])
            markmessage = "CheckedIn Mark is selected"
        case "Absent mark":
            sqlquery = "UPDATE book SET Absent = 1 WHERE BookID = '{}'".format(context.user_data["adjustID"])
            markmessage = "Absent Mark is selected"
        case _:
            sqlquery = "UPDATE book SET Payment = 0, Deposit = 0 WHERE BookID = '{}'".format(context.user_data["adjustID"])
            markmessage = "Payment Status: Full Payment"
    cur.execute(sqlquery)
    keyboard = [
                [
                    InlineKeyboardButton("Check-in mark", callback_data="Check-in mark"),
                    InlineKeyboardButton("Absent mark", callback_data="Absent mark"),
                    InlineKeyboardButton(
                        "Payment status", callback_data="Payment status"),
                ]
            ]
    await query.message.edit_text(markmessage + "\nIf you want to do something, else enter /start", reply_markup=InlineKeyboardMarkup(keyboard))

    return MARKANDPAY
    
    
##########################################################################################


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
            CHOOSE: [CallbackQueryHandler(book, pattern="Book a new room"),
                     CallbackQueryHandler(
                         check, pattern="Check if there are any bookings on a specific date"),
                     CallbackQueryHandler(
                         adjust, pattern="Adjust booking status"),
                     CallbackQueryHandler(deletebooking, pattern="Delete booking"),
                     CallbackQueryHandler(reminder, pattern="Reminder"),
                     CallbackQueryHandler(viewrecent, pattern="Check-in and payment marking")],
            BOOK: [MessageHandler(filters.TEXT, book)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            ROOMTYPE: [MessageHandler(filters.TEXT, roomtype)],
            CHECKIN: [CallbackQueryHandler(checkin)],
            SELECTDATE: [CallbackQueryHandler(selectdate)],
            CHOOSEBOOKINGSOURCE: [CallbackQueryHandler(price)],
            STATUS: [MessageHandler(filters.TEXT, status)],
            PAYMENT: [CallbackQueryHandler(partial, pattern="partial"),
                      CallbackQueryHandler(fullpay, pattern="fullpay"),],
            DEPOSIT: [MessageHandler(filters.TEXT, deposit)],
            DISPLAY: [MessageHandler(filters.TEXT, display)],
            CONFIRM: [CallbackQueryHandler(confirm, pattern="confirm"),
                      CallbackQueryHandler(cancel, pattern="cancel"),],
            CHECKOUTDATETOCHECK: [CallbackQueryHandler(checkoutdatetocheck)],
            DATECHECKED: [CallbackQueryHandler(datechecked)],
            CHECKROOMTYPE: [CallbackQueryHandler(selectroomtype)],
            CONFIRMSELECTION: [CallbackQueryHandler(confirmchecked, pattern="confirmchecked"),
                      CallbackQueryHandler(cancel, pattern="cancelchecked"),],
            SELECTADJUST: [CallbackQueryHandler(selectadjust)],
            VIEWDELETE: [CallbackQueryHandler(viewdelete)],
            CONFIRMDELETE: [CallbackQueryHandler(confirmdelete, pattern="confirmdelete"),
                      CallbackQueryHandler(cancel, pattern="canceldelete"),],
            REMINDER: [CallbackQueryHandler(viewreminder)],
            SELECTMARK: [CallbackQueryHandler(selectmark)],
            MARKANDPAY: [CallbackQueryHandler(markandpay)],
        },
        fallbacks=[CommandHandler("end", end)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
