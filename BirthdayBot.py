from telegram.ext import (
    MessageHandler,
    Filters,
    CommandHandler,
    Updater,
    PicklePersistence,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from datetime import datetime, date, time, timedelta
import logging
import telegram
from pytz import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BIRTHDAY, BIRTHYEAR, NAME, INPUTID, PRIORITY = range(5)
LOW, MEDIUM, HIGH = range(3)

pp = PicklePersistence(filename="birthdayBot.pickle")
bot = telegram.Bot(token="1190164594:AAG3HWiPHY-6xmJvoPqt58vYKrvogZUnUjQ")
updater = Updater(
    token="1190164594:AAG3HWiPHY-6xmJvoPqt58vYKrvogZUnUjQ",
    persistence=pp,
    use_context=True,
)
dispatcher = updater.dispatcher
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
jobber = updater.job_queue
timezone = timezone("Europe/Berlin")


def daily_callback(context: telegram.ext.CallbackContext):
    user_data = context.job.context
    today = datetime.today()
    week = today + timedelta(days=7)
    month = today + timedelta(days=30)

    payload = []

    if today.strftime("%d.%m") in user_data["dates"].keys():
        payload.append("Today is the Birthday of:")
        for id in user_data["dates"][today.strftime("%d.%m")]:
            payload.append(
                "\n"
                + user_data["persons"][id]["name"]
                + (
                    ", turned "
                    + str(today.year - int(user_data["persons"][id]["birthyear"]))
                    + " today"
                    if "birthyear" in user_data["persons"][id].keys()
                    else ""
                )
            )
        payload.append("\n")

    if week.strftime("%d.%m") in user_data["dates"].keys():
        payload.append("In a week is the Birthday of:")
        for id in user_data["dates"][week.strftime("%d.%m")]:
            payload.append(
                "\n" + user_data["persons"][id]["name"]
                if user_data["persons"][id]["priority"] == MEDIUM
                or user_data["persons"][id]["priority"] == HIGH
                else ""
            )
        payload.append("\n")

    if month.strftime("%d.%m") in user_data["dates"].keys():
        payload.append("In a month is the Birthday of:")
        for id in user_data["dates"][month.strftime("%d.%m")]:
            payload.append(
                "\n" + user_data["persons"][id]["name"]
                if user_data["persons"][id]["priority"] == HIGH
                else ""
            )

    if payload == "" and (user_data["admin"] or user_data["manualCheck"]):
        user_data["manualCheck"] = False
        payload.append("I'm alive. No Birthdays today.")

    context.bot.send_message(
        chat_id=user_data["chat-id"],
        text="".join(payload),
    )


def check_todays_birthdays(update, context):
    context.user_data["manualCheck"] = True
    jobber.run_once(daily_callback, 0, context=context.user_data)


def enableAdminInfo(update, context):
    context.user_data["admin"] = True
    update.message.reply_text("Enabled Admin Info")


def disableAdminInfo(update, context):
    context.user_data["admin"] = False
    update.message.reply_text("Disabled Admin Info")


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hey, I'm a birthday reminder Bot!\nTo add a new Birthday send /add. It will start a conversation where you can provide all information.\nI will remind you daily of the Birthdays you added.\nI will even remind you of important birthdays in time!\nFor Birthdays with high priority a month in advance and for medium priority birthdays a week in advance.\nView the other commands with /help\nThanks for using me!",
    )
    if not "birthday-count" in context.user_data.keys():
        context.user_data["birthday-count"] = 0
        context.user_data["dates"] = {}
        context.user_data["persons"] = {}
        context.user_data["admin"] = False
    context.user_data["chat-id"] = update.effective_chat.id

    # time(hour, minute and second)
    jobber.run_daily(
        daily_callback,
        time(8, tzinfo=timezone),
        context=context.user_data,
    )
    pp.flush()
    print("New User:" + str(update.message.chat))


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="/start Start the Bot \n/add Add a new Birthday\n/del Delete a Birthday by ID \n/list List all entries with ID, Name, Birthday and Priority\n/listDates Show a list sorted by Birthdays\n/check Check manually todays birthdays, and the bots status\n/cancel Send during any procedure to cancel the process",
    )


def add(update: Updater, context: CallbackContext) -> int:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, please send me the Birthday in this format: dd.mm . You can quit this process at any point with /cancel",
    )
    return BIRTHDAY


def addBirthday(update: Updater, context: CallbackContext) -> int:
    value = "".join(update.message.text)
    try:
        day = datetime.strptime(value, "%d.%m")
        context.user_data["t_birthday"] = day.strftime("%d.%m")
    except Exception:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Something went wrong. Try again in this Format: dd.mm",
        )
        return BIRTHDAY
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Good, if you know the Birthyear of the Person you can send it now in this format: yyyy\nElse send /skip or /s",
    )
    return BIRTHYEAR


def addBirthyear(update: Updater, context: CallbackContext) -> int:
    value = "".join(update.message.text)
    try:
        context.user_data["t_birthyear"] = datetime.strptime(value, "%Y").strftime("%Y")
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Something went wrong. Try again in this Format: yyyy or send /skip",
        )
        return BIRTHYEAR
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Good, now please send me the Name of the Person",
    )
    return NAME


def skip(update: Updater, context: CallbackContext) -> int:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, now please send me the Name of the Person",
    )
    return NAME


def addName(update: Updater, context: CallbackContext) -> int:
    name = "".join(update.message.text)
    context.user_data["t_name"] = name

    keyboard = [
        [
            InlineKeyboardButton("Low", callback_data=LOW),
            InlineKeyboardButton("Medium", callback_data=MEDIUM),
            InlineKeyboardButton("High", callback_data=HIGH),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "How important is this Birthday to you?", reply_markup=reply_markup
    )

    return PRIORITY


def priority(update: Updater, context: CallbackContext) -> int:
    # handle Inline Keyboard
    query = update.callback_query
    query.answer()

    t_name = context.user_data["t_name"]
    t_birthday = context.user_data["t_birthday"]

    priority = int(query.data)

    context.user_data["birthday-count"] += 1
    index = context.user_data["birthday-count"]
    # Lege Datenstruktur persons an
    context.user_data["persons"][index] = {}
    context.user_data["persons"][index]["name"] = t_name
    context.user_data["persons"][index]["birthday"] = t_birthday
    context.user_data["persons"][index]["priority"] = priority
    # Lege Date Datenstruktur an
    if t_birthday in context.user_data["dates"].keys():
        context.user_data["dates"][t_birthday].append(index)
    else:
        context.user_data["dates"][t_birthday] = [index]

    # check ob birthyear hinzugefügt wurde
    if "t_birthyear" in context.user_data.keys():
        context.user_data["persons"][index]["birthyear"] = context.user_data[
            "t_birthyear"
        ]
        birthstring = (
            context.user_data["persons"][index]["birthday"]
            + "."
            + context.user_data["persons"][index]["birthyear"]
        )
    else:
        birthstring = context.user_data["persons"][index]["birthday"]
    # Stelle Antwort zusammen
    query.edit_message_text(
        text="I added "
        + context.user_data["persons"][index]["name"]
        + "'s Birthday "
        + birthstring
        + " with this ID: "
        + str(index)
        + ". Priority is "
        + (
            "low"
            if priority == LOW
            else (
                "medium" if priority == MEDIUM else ("high" if priority == HIGH else "")
            )
        ),
    )
    try:
        context.user_data.pop("t_birthday")
        context.user_data.pop("t_name")
        context.user_data.pop("t_birthyear")
    except:
        pass
    # Speicher in Pickle File
    pp.flush()

    return ConversationHandler.END


def cancel(update, context):
    try:
        context.user_data.pop("t_birthday")
        context.user_data.pop("t_name")
        context.user_data.pop("t_birthyear")
    except:
        pass
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, cancelled procedure",
    )
    return ConversationHandler.END


def deleteStart(update, context) -> int:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Okay, please send me the ID of the Birthday you want to delete. To show a list of all birthdays send /list",
    )
    return INPUTID


def delete(update, context) -> int:
    id = int("".join(update.message.text))
    try:
        date = context.user_data["persons"][id]["birthday"]
        person = context.user_data["persons"].pop(id)
    except:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ID not found, please try again. To show a list of all birthdays send /list",
        )
        return INPUTID

    context.user_data["dates"][date].remove(id)

    payload = (
        "Delete complete. Deletet " + person["name"] + "'s Birthday with ID:" + str(id)
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=payload,
    )
    return ConversationHandler.END


def listPersons(update, context) -> int:
    birthdayList = "ID - Name - Birthday - Priority\n"

    for key in context.user_data["persons"].keys():
        birthdayList += (
            str(key)
            + " - "
            + context.user_data["persons"][key]["name"]
            + " - "
            + context.user_data["persons"][key]["birthday"]
            + (
                "." + context.user_data["persons"][key]["birthyear"]
                if "birthyear" in context.user_data["persons"][key].keys()
                else ""
            )
            + " - "
            + (
                "low"
                if context.user_data["persons"][key]["priority"] == LOW
                else (
                    "medium"
                    if context.user_data["persons"][key]["priority"] == MEDIUM
                    else (
                        "high"
                        if context.user_data["persons"][key]["priority"] == HIGH
                        else ""
                    )
                )
            )
            + "\n"
        )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=birthdayList,
    )


def listDates(update, context):
    birthdayList = "Birthday - Names\n"

    for key in context.user_data["dates"].keys():
        birthdayList += (
            key
            + " - "
            + ", ".join(
                [
                    context.user_data["persons"][id]["name"]
                    for id in context.user_data["dates"][key]
                ]
            )
            + "\n"
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=birthdayList,
    )
    return INPUTID


def credits(update, context):
    update.message.reply_text(
        "Version 0.1\nMade by:\nKim Leidolf\nFeedback to:\nkim.leidolf@gmx.de"
    )


dispatcher.add_handler(CommandHandler("enableAdmin", enableAdminInfo))
dispatcher.add_handler(CommandHandler("disableAdmin", disableAdminInfo))
dispatcher.add_handler(CommandHandler("check", check_todays_birthdays))
dispatcher.add_handler(CommandHandler("listDates", listDates))
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("list", listPersons))
dispatcher.add_handler(CommandHandler("credits", credits))


convAdd_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add)],
    states={
        BIRTHDAY: [MessageHandler(Filters.text & ~Filters.command, addBirthday)],
        BIRTHYEAR: [
            MessageHandler(Filters.text & ~Filters.command, addBirthyear),
            CommandHandler("skip", skip),
            CommandHandler("s", skip),
        ],
        NAME: [MessageHandler(Filters.text & ~Filters.command, addName)],
        PRIORITY: [CallbackQueryHandler(priority)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
dispatcher.add_handler(convAdd_handler)

convDel_handler = ConversationHandler(
    entry_points=[CommandHandler("del", deleteStart)],
    states={
        INPUTID: [
            MessageHandler(Filters.text & ~Filters.command, delete),
            CommandHandler("list", listDates),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
dispatcher.add_handler(convDel_handler)

updater.start_polling()
updater.idle()
