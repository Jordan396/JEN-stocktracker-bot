import time, logging, emoji, threading
import datetime

import config

from telegram.__main__ import main as tmain
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

from Controllers.botmethods import botmethods
from Controllers.dbhelper import DBHelper

TOKEN = config.TELEGRAM_BOT_SECRET_KEY
ALPHA_VANTAGE_SECRET_KEY = config.ALPHA_VANTAGE_SECRET_KEY
DEPLOYMENT_DATETIME = datetime.datetime.strptime(config.DEPLOYMENT_DATETIME, '%m/%d/%y %H:%M:%S')

bots = botmethods(ALPHA_VANTAGE_SECRET_KEY)
db = DBHelper()

# Start logging
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initiation of keyboards
reply_keyboard_one = [[emoji.emojize(':heavy_plus_sign: Add a stock :heavy_plus_sign:', use_aliases=True)], 
				  [emoji.emojize(':eyes: View all stocks :eyes:', use_aliases=True)],
				  [emoji.emojize(':cross_mark: Delete a stock :cross_mark:', use_aliases=True)]]
markup_one = ReplyKeyboardMarkup(reply_keyboard_one, one_time_keyboard=True)

reply_keyboard_two = [["Yes, that's the one!"], ["No, that's not what I was looking for..."]]
markup_two = ReplyKeyboardMarkup(reply_keyboard_two, one_time_keyboard=True)

reply_keyboard_three = [["HIGH"], ["MEDIUM"],["LOW"]]
markup_three = ReplyKeyboardMarkup(reply_keyboard_three, one_time_keyboard=True)

reply_keyboard_four = [["That'd be great, thanks!"], ["Not now. Perhaps some other time!"]]
markup_four = ReplyKeyboardMarkup(reply_keyboard_four, one_time_keyboard=True)

MENU, ADDTICKERSYMBOL, ADDTICKERVERIFICATION, ADDTICKERTRIGGER, ADDTICKERCONFIRMATION, VIEWSTOCKS, DELETESTOCK = range(7)

### Starting Menu ###
def start(bot, update):
    if  update.message.chat.username is None:
        update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
    else:
    	userExists = bots.checkIfUserExists(update.message.chat.username)
    	if userExists:
    		update.message.reply_text("Welcome back "+ update.message.chat.first_name + "!\n\n" +
    			"<b>Available Commands:</b>\n"+
          "/start : Activates JEN.\n"+
    			"/help : Displays information guide.\n"+
    			"/seeya : Closes JEN. You will continue to receive notifications (if triggered).\n"+
    			"/exit : Clears your data. You will no longer receive notifications.\n", reply_markup=markup_one, parse_mode='HTML')
    		return MENU
    	else:
    		message = ("Hello " + update.message.chat.first_name + "!\n\nMy name's <b>JEN</b>. My purpose is to keep track of stock prices and notify you when great buying opportunities come by!\n\n" +
    			"To use me, simply look up the stocks you want to track and pick one of my suggested 3/15MA thresholds. When price changes fall below this threshold, I'll send you a notification! \n\n" +
    			"If you're wondering what's a <i>3/15MA</i>, you can find a detailed explanation on my creator's GitHub page: https://github.com/Jordan396/JEN-stocktracker-bot\n\n" +
    			"Although I try my best, you should know that I'm only a bot after all... you should always rely on your own discretion before taking any action.\n\n"+
    			"<b>Available Commands:</b>\n"+
          "/start : Activates JEN.\n"+
    			"/help : Displays information guide.\n"+
    			"/seeya : Closes JEN. You will continue to receive notifications (if triggered).\n"+
    			"/exit : Clears all your data. You will no longer receive notifications.\n")
    		update.message.reply_text(message, reply_markup=markup_one, parse_mode='HTML')
    		bots.saveNewUser(update.message.chat.username)
    		return MENU

def addNewStock(bot, update):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		update.message.reply_text("Enter the ticker symbol of the stock you'd like to add:")
		return ADDTICKERSYMBOL

def addTickerOffer(bot, update, user_data):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		text = update.message.text
		result = bots.getCompanyName(text.upper())
		if result is None:
			update.message.reply_text("Sorry, we couldn't find the ticker symbol <b>{}</b>.\nPlease enter a different ticker symbol.".format(text), parse_mode='HTML')
			return ADDTICKERSYMBOL
		else:
			user_data['stockSymbol'] = result[0]
			user_data['stockExchange'] = result[1]
			user_data['companyName'] = result[2]
			update.message.reply_text("Here's what I found: <b>{}:{} - {}</b>.\nIs this the stock you were looking for?".format(user_data['stockExchange'],user_data['stockSymbol'],user_data['companyName']), reply_markup=markup_two, parse_mode='HTML')
			return ADDTICKERVERIFICATION

def addTickerVerification(bot, update, user_data):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		text = update.message.text
		if (text == "Yes, that's the one!"):
			update.message.reply_text("Awesome! Give me a moment while I analyze this stock...")
			# try:
			message, currentPrice, highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold = bots.extractKeyStockInformation(user_data['stockSymbol'], user_data['stockExchange'], user_data['companyName'])
			user_data['highSensitivityThreshold'] = highSensitivityThreshold
			user_data['medSensitivityThreshold'] = medSensitivityThreshold
			user_data['lowSensitivityThreshold'] = lowSensitivityThreshold
			update.message.reply_text(message, parse_mode='HTML')
			update.message.reply_text("Please select a 3/15MA threshold.", reply_markup=markup_three)
			return ADDTICKERTRIGGER
			# except:
			# 	update.message.reply_text("Sorry, an unexpected error has occurred! I'll notify my creator and he'll handle it.")
			# 	update.message.reply_text("What would you like to do now?", reply_markup=markup_one)
			# 	user_data.clear()
			# 	return MENU
		else:
			update.message.reply_text("Sorry, I can't find any other company with that ticker symbol.")
			update.message.reply_text("What would you like to do now?", reply_markup=markup_one)
			user_data.clear()
			return MENU

def addTickerTrigger(bot, update, user_data):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		text = update.message.text
		if (text == "HIGH" or text == "MEDIUM" or text == "LOW"):
			update.message.reply_text("Great! Shall I proceed to save this stock for you?", reply_markup=markup_four)
			if (text == "HIGH"):
				user_data['selectedThresholdPercentage'] = user_data['highSensitivityThreshold']
			elif (text == "MEDIUM"):
				user_data['selectedThresholdPercentage'] = user_data['medSensitivityThreshold']
			else:
				user_data['selectedThresholdPercentage'] = user_data['lowSensitivityThreshold']
			return ADDTICKERCONFIRMATION
		else:
			update.message.reply_text("I'm sorry, I couldn't understand what you were telling me..")
			update.message.reply_text("Let's try again! What would you like to do?", reply_markup=markup_one)
			user_data.clear()
			return MENU

def addTickerConfirmation(bot, update, user_data):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		text = update.message.text
		if (text == "That'd be great, thanks!"):
			bots.saveUserStock(update.message.chat.id ,update.message.chat.username, user_data['stockSymbol'], user_data['stockExchange'], user_data['companyName'], user_data['selectedThresholdPercentage'], str(datetime.datetime.now().strftime("%Y-%m-%d")))
			update.message.reply_text("<b>{}:{}</b> was added successfully! I'll send you a notification whenever price changes exceed your threshold.\nWhat would you like to do next?".format(user_data['stockExchange'],user_data['stockSymbol']), reply_markup=markup_one, parse_mode='HTML')
			user_data.clear()
			return MENU
		else:
			update.message.reply_text("No problemo! What would you like to do next?", reply_markup=markup_one)
			user_data.clear()
			return MENU

def viewUserStocks(bot, update):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		message, status = bots.viewUserStocks(update.message.chat.username)
		update.message.reply_text(message, parse_mode='HTML')
		update.message.reply_text("What would you like to do next?", reply_markup=markup_one)
		return MENU

def deleteStock(bot, update):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		message, status = bots.viewUserStocks(update.message.chat.username)
		update.message.reply_text(message, parse_mode='HTML')
		if (status == 1):
			update.message.reply_text("Please enter the stock you'd like to delete in this format: <b>[EXCHANGE:SYMBOL]</b>.\nFor example, enter 'NYSE:MMM'.", parse_mode='HTML')
			return DELETESTOCK
		else:
			return MENU
	
def deleteIdentifiedStock(bot, update):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		text = update.message.text
		message = bots.deleteUserStock(update.message.chat.username, text)
		update.message.reply_text(message, parse_mode='HTML')
		update.message.reply_text("What would you like to do next?", reply_markup=markup_one)
		return MENU

def notifyUsersIfThresholdExceeded(bot, job):
	userIDs, messages = bots.extractTriggeredStocks()
	for i in range(len(userIDs)):
		print(userIDs[i], messages[i])
		bot.send_message(chat_id=userIDs[i], text=messages[i], parse_mode='HTML')


def unknownCommand(bot, update, user_data):
	if  update.message.chat.username is None:
		update.message.reply_text("It seems you do not have a Telegram Username.\nI'll need your username in order to function :( /start me up when you have one! (You can set your username in Settings.)")
	else:
		update.message.reply_text("I'm sorry, I couldn't understand what you were trying to say :(")
		update.message.reply_text("Let's try again! What would you like to do?", reply_markup=markup_one)
		user_data.clear()
		return MENU

## Misc ###
def exit(bot, update, user_data):
    update.message.reply_text("Thank you for using me! All your data has been cleared and you will no longer receive notifications.")
    bots.clearChatFromApp(update.message.chat.id)
    user_data.clear()
    return ConversationHandler.END

def seeya(bot, update, user_data):
    update.message.reply_text("See you next time! I'll continue to send you notifications (if triggered). /start me up again whenever~ :)")
    user_data.clear()
    return ConversationHandler.END

def instructions(bot, update, user_data):
    update.message.reply_text("To use me, simply look up the stocks you want to track and pick one of my suggested 3/15MA thresholds. When price changes fall below this threshold, I'll send you a notification! \n\n" +
    						  "If you're wondering what's a <i>3/15MA</i>, you can find a detailed explanation on my creator's GitHub page: https://github.com/Jordan396/JEN-stocktracker-bot\n\n", reply_markup=markup_one, parse_mode='HTML')
    user_data.clear()
    return MENU

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
	db.setup()
	updater = Updater(token=TOKEN)
	jobQueue = updater.job_queue
	dispatcher = updater.dispatcher
	job_minute = jobQueue.run_repeating(notifyUsersIfThresholdExceeded, interval=86400, first=DEPLOYMENT_DATETIME)

	conv_handler = ConversationHandler( # Handles different commands, states. 
        entry_points=[CommandHandler('start', start)],

        states={
            MENU: [ RegexHandler('^('+ emoji.emojize(':heavy_plus_sign: Add a stock :heavy_plus_sign:', use_aliases=True)+')$', addNewStock),
            		RegexHandler('^('+ emoji.emojize(':eyes: View all stocks :eyes:', use_aliases=True)+')$', viewUserStocks),
                    RegexHandler('^('+ emoji.emojize(':cross_mark: Delete a stock :cross_mark:', use_aliases=True)+')$', deleteStock),
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

if __name__ == '__main__':
	tmain()
	main()