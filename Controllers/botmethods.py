from Controllers.dbhelper import DBHelper
from datetime import datetime, timedelta
import Controllers.alphavmethods as alphavmethods
import requests
import copy 

db = DBHelper()

class botmethods:

    ## Bot methods (The Controller or business logic tier)

    def __init__(self, ALPHA_VANTAGE_SECRET_KEY):
        self.ALPHA_VANTAGE_SECRET_KEY = ALPHA_VANTAGE_SECRET_KEY

    def checkIfUserExists(self, userID):
        return db.select_user(userID)

    def saveNewUser(self, userID):
        db.insert_new_user(userID)

    def getCompanyName(self, stockSymbol):
        return db.select_company_name(stockSymbol)

    def saveUserStock(self, chatID, userID, stockSymbol, stockExchange, companyName, triggerPercentage, dateAdded):
        db.insert_user_stock(chatID, userID, stockSymbol, stockExchange, companyName, triggerPercentage, dateAdded)

    def viewUserStocks(self, userID):
        message = None
        status = 1
        list = []
        count = 1
        for (a, b, c, d) in db.select_all_user_stocks(userID): 
            list.append('{}) <b>{}:{}</b>: {}'.format(count, c, b, d))
            count += 1
        message = "{}, here's the list of stocks you saved:\n\n".format(userID) + "\n".join(list)
        if not list:
            message = "It appears you do not have any stocks saved. You can save a stock by selecting <b>Add a stock</b>."
            status = 0
        return (message, status)

    def deleteUserStock(self, userID, userInput):
        userInput = userInput.split(':')
        try:
            db.delete_user_stock(userID, userInput[1], userInput[0])
            message = "<b>{}:{}</b> has been removed.".format(userInput[0], userInput[1])
            return message
        except:
            message = "Sorry, that's not a valid input!"
            return message

    def extractKeyStockInformation(self, stockSymbol, stockExchange, companyName):
        message = None
        Dates, Prices = alphavmethods.getFullPriceHistory(stockSymbol, stockExchange, self.ALPHA_VANTAGE_SECRET_KEY)
        closingPrices = copy.deepcopy(Prices)
        highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold = alphavmethods.calculateSensitivityTriggerRates(closingPrices)
        message = ("<b>{} Report</b>\n\n"+
            "The current price of the stock is <i>${}</i>.\n\n"+
            "Here are the available thresholds:\n"+
            "HIGH (~6 alerts/month): <i>{}%</i>\n"+
            "MEDIUM (~3 alerts/month): <i>{}%</i>\n"+
            "LOW (~1 alert/month): <i>{}%</i>\n\n"+
            "<i>This report is accurate as of {}, which is the latest trading date identified.</i>").format(companyName, round(Prices[0],2), highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold, Dates[0])
        return (message, Prices[0], highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold)

    def extractTriggeredStocks(self):
        userIDs = []
        messages = []
        for (a, b, c, d, e, f) in db.select_all_stocks_triggered():
            userIDs.append(a)
            messages.append("<b>ALERT!</b>\n\nThreshold for <b>{}:{} - {}</b> has been exceeded!\n\n3/15MA threshold set: <i>{}</i>\nLatest 3/15MA calculated: <i>{}</i>".format(c,b,d,e,f))
        return (userIDs, messages)

    def clearChatFromApp(self, chatID):
        db.delete_chat_from_app(chatID)