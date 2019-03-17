# -*- coding: utf-8 -*-
"""Script to run JEN bot. This is also the View layer.

This script starts the telegram bot, which continually polls for messages. 
If this is the first time running the script, a SQLITE database will be
created. This may take some time. JEN checks for updates in prices every 
24 hours, commencing from when the script is deployed.
Example:
    To run the script:
        $ python JEN.py
Todo:
    * Define variables in config.py
Future extensions:
	* Add support for same ticker symbols on different exchanges
	* Implement flexible X/Y moving average thresholds for stocks of different volatilities
"""

# Import telegram bot modules
from telegram.__main__ import main as tmain
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, RegexHandler, ConversationHandler)

# Import common modules
import time
import logging
import emoji
import threading
import datetime

# Import local modules and scripts
import config
from Controllers.botmethods import botmethods
from Controllers.dbhelper import DBHelper

__author__ = "Jordan396"
__copyright__ = "Copyright (c) 2018 Jordan"
__credits__ = ["Jordan396"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Jordan396"
__email__ = "jordan.chyehong@gmail.com"
__status__ = "Production"

# Assign config variables
TOKEN = config.TELEGRAM_BOT_SECRET_KEY
ALPHA_VANTAGE_SECRET_KEY = config.ALPHA_VANTAGE_SECRET_KEY

# Instantiate controller class
bots = botmethods(ALPHA_VANTAGE_SECRET_KEY, DBHelper())

# Start logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initiate keyboards
reply_keyboard_one = [[emoji.emojize(':heavy_plus_sign: Add a stock :heavy_plus_sign:', use_aliases=True)],
                      [emoji.emojize(
                          ':eyes: View all stocks :eyes:', use_aliases=True)],
                      [emoji.emojize(':cross_mark: Delete a stock :cross_mark:', use_aliases=True)]]
markup_one = ReplyKeyboardMarkup(reply_keyboard_one, one_time_keyboard=True)

reply_keyboard_two = [["Yes, that's the one!"], [
    "No, that's not what I was looking for..."]]
markup_two = ReplyKeyboardMarkup(reply_keyboard_two, one_time_keyboard=True)

reply_keyboard_three = [["HIGH"], ["MEDIUM"], ["LOW"]]
markup_three = ReplyKeyboardMarkup(
    reply_keyboard_three, one_time_keyboard=True)

reply_keyboard_four = [["That'd be great, thanks!"],
                       ["Not now. Perhaps some other time!"]]
markup_four = ReplyKeyboardMarkup(reply_keyboard_four, one_time_keyboard=True)

# Declare reference to bot states
MENU, ADDTICKERSYMBOL, ADDTICKERVERIFICATION, ADDTICKERTRIGGER, ADDTICKERCONFIRMATION, VIEWSTOCKS, DELETESTOCK = range(
    7)


#================================#
#    MAIN MESSAGE HANDLERS       #
#================================#

def start(bot, update):
    """Handles conversation initiation.

    Different messages are displayed depending on whether the user
    is new. If the user is new, JEN displays an introduction message.
    Otherwise, JEN displays a 'Welcome back' message.
    Instructions on how to use JEN are also provided.
    Returns:
        MENU state with markup_one keyboard
    """
    if update.message.chat.username is None:
        # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        userExists = bots.checkIfUserExists(update.message.chat.username)
        if userExists:
            update.message.reply_text("Welcome back " + update.message.chat.first_name + "!\n\n" +
                                      "<b>Available Commands:</b>\n" +
                                      "/start : Activates JEN.\n" +
                                      "/help : Displays information guide.\n" +
                                      "/seeya : Stops JEN temporarily. You will still receive notifications (if triggered).\n" +
                                      "/exit : Stops JEN permanently. You will no longer receive notifications.", reply_markup=markup_one, parse_mode='HTML')
            return MENU
        else:
            message = ("Hello " + update.message.chat.first_name + "!\n\nMy name's <b>JEN</b>. My purpose is to keep track of stock prices and notify you when great buying opportunities come by!\n\n" +
                       "To use me, simply look up the stocks you want to track and pick one of my suggested 3/15MA thresholds. When price changes fall below this threshold, I'll send you a notification! \n\n" +
                       "If you're wondering what's a <i>3/15MA</i>, you can find a detailed explanation on my creator's GitHub page: https://github.com/Jordan396/JEN-stocktracker-bot\n\n" +
                       "Although I try my best, you should know that I'm only a bot after all... you should always rely on your own discretion.\n\n" +
                       "<b>Available Commands:</b>\n" +
                       "/start : Activates JEN.\n" +
                       "/help : Displays information guide.\n" +
                       "/seeya : Stops JEN temporarily. You will still receive notifications (if triggered).\n" +
                       "/exit : Stops JEN permanently. You will no longer receive notifications.")
            update.message.reply_text(
                message, reply_markup=markup_one, parse_mode='HTML')
            bots.saveNewUser(update.message.chat.username)
            return MENU


def addNewStock(bot, update):
    """User adds a new stock.

    Displays a message requesting the user to enter a stock symbol.
    Returns:
        ADDTICKERSYMBOL state with normal keyboard
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        update.message.reply_text(
            "Enter the ticker symbol of the stock you'd like to add:")
        return ADDTICKERSYMBOL


def addTickerOffer(bot, update, user_data):
    """Handles user input after requesting for ticker symbol.

    JEN first checks if the ticker symbol added by the user is found.
    If found, display information of company of the stock symbol.
    Otherwise, prompt the user for a different symbol.
    Returns:
        If ticker symbol is found, return ADDTICKERVERIFICATION state with markup_two keyboard.
        Otherwise, return ADDTICKERSYMBOL state with normal keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        text = update.message.text
        result = bots.getCompanyName(text.upper())
        if result is None:
            update.message.reply_text(
                "Sorry, we couldn't find the ticker symbol <b>{}</b>.\nPlease enter a different ticker symbol.".format(text), parse_mode='HTML')
            return ADDTICKERSYMBOL
        else:
            user_data['stockSymbol'] = result[0]
            user_data['stockExchange'] = result[1]
            user_data['companyName'] = result[2]
            update.message.reply_text("Here's what I found: <b>{}:{} - {}</b>.\nIs this the stock you were looking for?".format(
                user_data['stockExchange'], user_data['stockSymbol'], user_data['companyName']), reply_markup=markup_two, parse_mode='HTML')
            return ADDTICKERVERIFICATION


def addTickerVerification(bot, update, user_data):
    """Verify is the company displayed is indeed what the user has requested.

    If the user rejects JEN's suggested company, restart the entire interaction process.
    Otherwise, JEN proceeds to analyze the company's stock using bots.extractKeyStockInformation().
    Results of analysis are then displayed.
    Returns:
        If user accepts, return ADDTICKERTRIGGER state with markup_three keyboard.
        Otherwise, return MENU state with markup_one keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        text = update.message.text
        if (text == "Yes, that's the one!"):
            update.message.reply_text(
                "Awesome! Give me a moment while I analyze this stock...")
            message, currentPrice, highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold = bots.extractKeyStockInformation(
                user_data['stockSymbol'], user_data['stockExchange'], user_data['companyName'])
            user_data['highSensitivityThreshold'] = highSensitivityThreshold
            user_data['medSensitivityThreshold'] = medSensitivityThreshold
            user_data['lowSensitivityThreshold'] = lowSensitivityThreshold
            update.message.reply_text(message, parse_mode='HTML')
            update.message.reply_text(
                "Please select a <i>3/15MA</i> threshold.", reply_markup=markup_three, parse_mode='HTML')
            return ADDTICKERTRIGGER
        else:
            update.message.reply_text(
                "Sorry, I can't find any other company with that ticker symbol.")
            update.message.reply_text(
                "What would you like to do now?", reply_markup=markup_one)
            user_data.clear()
            return MENU


def addTickerTrigger(bot, update, user_data):
    """Handles user input after displaying analysis thresholds.

    Validate user's reply and save selected threshold.
    Returns:
        If reply is valid, return ADDTICKERCONFIRMATION state with markup_four keyboard.
        Otherwise, return MENU state with markup_one keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        text = update.message.text
        if (text == "HIGH" or text == "MEDIUM" or text == "LOW"):
            update.message.reply_text(
                "Great! Shall I proceed to save this stock for you?", reply_markup=markup_four)
            if (text == "HIGH"):
                user_data['selectedThresholdPercentage'] = user_data['highSensitivityThreshold']
            elif (text == "MEDIUM"):
                user_data['selectedThresholdPercentage'] = user_data['medSensitivityThreshold']
            else:
                user_data['selectedThresholdPercentage'] = user_data['lowSensitivityThreshold']
            return ADDTICKERCONFIRMATION
        else:
            update.message.reply_text(
                "I'm sorry, I couldn't understand what you were telling me..")
            update.message.reply_text(
                "Let's try again! What would you like to do?", reply_markup=markup_one)
            user_data.clear()
            return MENU


def addTickerConfirmation(bot, update, user_data):
    """Saves the user's selected stock and threshold.

    Once confirmation is received, save user's selected stock and threshold.
    Returns:
        Return MENU state with normal keyboard.
    """
    if update.message.chat.username is None:
        # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
        # User has username
        text = update.message.text
        if (text == "That'd be great, thanks!"):
            bots.saveUserStock(update.message.chat.id, update.message.chat.username, user_data['stockSymbol'], user_data['stockExchange'], user_data[
                               'companyName'], user_data['selectedThresholdPercentage'], str(datetime.datetime.now().strftime("%Y-%m-%d")))
            update.message.reply_text("<b>{}:{}</b> was added successfully! I'll send you a notification whenever price changes exceed your sensitivity threshold.".format(
                user_data['stockExchange'], user_data['stockSymbol']), parse_mode='HTML')
            update.message.reply_text(
                "What would you like to do next?", reply_markup=markup_one)
            user_data.clear()
            return MENU
        else:
            update.message.reply_text(
                "No problemo! What would you like to do next?", reply_markup=markup_one)
            user_data.clear()
            return MENU


def viewUserStocks(bot, update):
    """Handle user's request to view saved stocks.

    Message returned by bots.viewUserStocks() is shown to the user.
    Returns:
        Return MENU state with normal keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        message, status = bots.viewUserStocks(update.message.chat.username)
        update.message.reply_text(message, parse_mode='HTML')
        update.message.reply_text(
            "What would you like to do next?", reply_markup=markup_one)
        return MENU


def deleteStock(bot, update):
    """Handle user's request to delete a stock.

    Calls on viewUserStocks() first to display user's saved stocks.
    If stocks are available, ask the user to select a stock to delete.
    Returns:
        If user has saved stocks, return DELETESTOCK state with normal keyboard.
        Otherwise, return MENU state with normal keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        message, status = bots.viewUserStocks(update.message.chat.username)
        update.message.reply_text(message, parse_mode='HTML')
        if (status == 1):
            update.message.reply_text(
                "Please enter the stock you'd like to delete in this format: <b>[EXCHANGE:SYMBOL]</b>.\nFor example, enter 'NYSE:MMM'.", parse_mode='HTML')
            return DELETESTOCK
        else:
            return MENU


def deleteIdentifiedStock(bot, update):
    """Deletes the user's selected stock.

    If the user's selected stock is valid, proceed to delete it.
    Returns:
        Return MENU state with normal keyboard.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        text = update.message.text
        message = bots.deleteUserStock(update.message.chat.username, text)
        update.message.reply_text(message, parse_mode='HTML')
        update.message.reply_text(
            "What would you like to do next?", reply_markup=markup_one)
        return MENU


#================================#
#    MISC MESSAGE HANDLERS       #
#================================#

def exit(bot, update, user_data):
    """Permanently removes user from application and ends conversation.
    """
    update.message.reply_text(
        "Thank you for using me! All your data has been cleared and you will no longer receive notifications.")
    bots.clearChatFromApp(update.message.chat.id)
    user_data.clear()
    return ConversationHandler.END


def seeya(bot, update, user_data):
    """Clears temporary user data and ends conversation.
    """
    update.message.reply_text(
        "See you next time! I'll continue to send you notifications (if triggered). /start me up again whenever~ :)")
    user_data.clear()
    return ConversationHandler.END


def instructions(bot, update, user_data):
    """Displays information on how to use JEN.
    """
    update.message.reply_text("To use me, simply look up the stocks you want to track and pick one of my suggested 3/15MA thresholds. When price changes fall below this threshold, I'll send you a notification! \n\n" +
                              "If you're wondering what's a <i>3/15MA</i>, you can find a detailed explanation on my creator's GitHub page: https://github.com/Jordan396/JEN-stocktracker-bot\n\n", reply_markup=markup_one, parse_mode='HTML')
    user_data.clear()
    return MENU


def error(bot, update, error):
    """Logs errors.
    """
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def unknownCommand(bot, update, user_data):
    """Handles unrecognized commands. Redirects user to main MENU.
    """
    if update.message.chat.username is None:
                # User has no username
        update.message.reply_text(
            "It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
                # User has username
        update.message.reply_text(
            "I'm sorry, I couldn't understand what you were trying to say :(")
        update.message.reply_text(
            "Let's try again! What would you like to do?", reply_markup=markup_one)
        user_data.clear()
        return MENU


#================================#
#         NOTIFICATIONS          #
#================================#

def notifyUsersIfThresholdExceeded(bot, job):
    """Sends registered users a notification if their saved threshold was exceeded.

    JEN first updates prices for all stocks saved in the application.
    For each stock with an exceeded threshold, JEN sends a notification
    to the corresponding user.
    Returns:
        None
    """
    bots.updatePriceOfExistingStocks()
    userIDs, messages = bots.extractTriggeredStocks()
    for i in range(len(userIDs)):
        print(userIDs[i], messages[i])
        bot.send_message(chat_id=userIDs[i],
                         text=messages[i], parse_mode='HTML')


#================================#
#             MAIN               #
#================================#

def main():
    """Main function to be executed.

    If database does not exist, JEN proceeds to set it up.
    A job to update existing stock prices is added to the jobQueue
    once every 24 hours. During which, JEN checks if users' threshold
    has been exceeded and proceeds to send a notification accordingly.
    The polling process runs continuously.
    """
    bots.setup_database()
    updater = Updater(token=TOKEN)
    jobQueue = updater.job_queue
    dispatcher = updater.dispatcher

    # Set price updater and notifier to execute every 24 hours
    job_minute = jobQueue.run_repeating(
        notifyUsersIfThresholdExceeded, interval=86400, first=0)

    # Set the conversation handler
    conv_handler = ConversationHandler(  # Handles different commands, states.
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [RegexHandler('^(' + emoji.emojize(':heavy_plus_sign: Add a stock :heavy_plus_sign:', use_aliases=True)+')$', addNewStock),
                   RegexHandler(
                       '^(' + emoji.emojize(':eyes: View all stocks :eyes:', use_aliases=True)+')$', viewUserStocks),
                   RegexHandler(
                '^(' + emoji.emojize(':cross_mark: Delete a stock :cross_mark:', use_aliases=True)+')$', deleteStock),
                MessageHandler(Filters.text, unknownCommand, pass_user_data=True)],
            ADDTICKERSYMBOL: [MessageHandler(Filters.text, addTickerOffer, pass_user_data=True)],
            ADDTICKERVERIFICATION: [MessageHandler(Filters.text, addTickerVerification, pass_user_data=True)],
            ADDTICKERTRIGGER: [MessageHandler(Filters.text, addTickerTrigger, pass_user_data=True)],
            ADDTICKERCONFIRMATION: [MessageHandler(Filters.text, addTickerConfirmation, pass_user_data=True)],
            DELETESTOCK: [MessageHandler(Filters.text, deleteIdentifiedStock)]
        },
        fallbacks=[CommandHandler('exit', exit, pass_user_data=True),
                   CommandHandler('help', instructions, pass_user_data=True),
                   CommandHandler('seeya', seeya, pass_user_data=True),
                   RegexHandler('^Main Menu$', start),
                   CommandHandler('menu', start)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


# Execute the main function
if __name__ == '__main__':
    tmain()
    main()
