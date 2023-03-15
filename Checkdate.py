
DATECHECKED, CHECKROOMTYPE, DISPLAYCHECKED, CONFIRMSELECTION = range(4)
checkinformation = {}


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # You chose checking on a specific date. Choose the date to check
    query = update.callback_query
    user = query.from_user
    await query.answer()
    calendar, step = DetailedTelegramCalendar().build()
    await query.message.edit_text(
        "Check if there are any bookings on a specific date\nEnter the date to check" +
        f"\nSelect {LSTEP[step]}",
        reply_markup=calendar
    )

    return DATECHECKED


# async def datechecked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     # Store the checked date and choose room type to check
#     query = update.callback_query
#     user = query.from_user
#     await query.answer()
#     result, key, step = DetailedTelegramCalendar().process(query.data)
#     print(result)
#     if not result and key:
#         await query.message.edit_text(f"Select {LSTEP[step]}", reply_markup=key)
#     elif result:
#         checkinformation["CheckDate"] = result
#         keyboard = [
#             [
#                 InlineKeyboardButton("A", callback_data="A"),
#                 InlineKeyboardButton("B1", callback_data="B1"),
#                 InlineKeyboardButton("B2", callback_data="B2"),
#             ],
#             [
#                 InlineKeyboardButton("C", callback_data="C"),
#                 InlineKeyboardButton("101", callback_data="101"),
#                 InlineKeyboardButton("102", callback_data="102"),
#             ],
#             [
#                 InlineKeyboardButton("201", callback_data="201"),
#                 InlineKeyboardButton("202", callback_data="202"),
#                 InlineKeyboardButton("full house", callback_data="fullhouse"),
#             ],
#         ]
#         await query.message.edit_text(
#             "Date to check: " + json.dumps(checkinformation["CheckDate"], indent=4, cls=DateTimeEncoder)+"\nChoose the booking source", reply_markup=InlineKeyboardMarkup(keyboard)
#         )

#         return PHONE

# async def selectroomtype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     # Store and display what to check. Choose confirm or cancel.
#     query = update.callback_query
#     user = query.from_user
#     await query.answer()
#     keyboard = [
#     [
#         InlineKeyboardButton("Confirm", callback_data="confirmchecked"),
#         InlineKeyboardButton("Cancel", callback_data="cancelchecked"),
#     ]]
#     checkinformation["CheckRoomType"] = query.data
#     await query.message.edit_text("Date to check: " + json.dumps(checkinformation["CheckDate"], indent=4, cls=DateTimeEncoder) + "\nThe room type to check: " + checkinformation["CheckRoomType"] + "\nCheck or Cancel?", reply_markup=InlineKeyboardMarkup(keyboard))

#     return CONFIRMSELECTION

# async def confirmchecked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     # Confirm is selected. Check the database
#     query = update.callback_query
#     user = query.from_user
#     await query.answer()
#     query = "SELECT * FROM BOOK WHERE CheckInDate <= {} AND CheckOutDate >= {} AND BookingSource = {}".format(checkinformation["CheckDate"], checkinformation["CheckDate"], checkinformation["CheckRoomType"])
#     cur.execute(query)
#     records = cur.fetchall()
#     # if records:
#     #     viewmessage = records[0]
#     await query.message.edit_text(viewmessage)
#     return FINISHBOOKING

# DATECHECKED: [CallbackQueryHandler(datechecked)],
            # CHECKROOMTYPE: [CallbackQueryHandler(selectroomtype)],
            # CONFIRMSELECTION: [CallbackQueryHandler(confirmchecked, pattern="confirmchecked"),],
