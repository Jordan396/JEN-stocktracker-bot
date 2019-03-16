from datetime import datetime, timedelta
import requests
import copy
import numpy as np
import time

class botmethods:

    # Bot methods (The Controller or business logic tier)

    def __init__(self, ALPHA_VANTAGE_SECRET_KEY, dbhelper):
        self.ALPHA_VANTAGE_SECRET_KEY = ALPHA_VANTAGE_SECRET_KEY
        self.db = dbhelper

    def setup_database(self):
        self.db.setup_database()

    def checkIfUserExists(self, userID):
        return self.db.select_user(userID)

    def saveNewUser(self, userID):
        self.db.insert_new_user(userID)

    def getCompanyName(self, stockSymbol):
        return self.db.select_company_name(stockSymbol)

    def saveUserStock(self, chatID, userID, stockSymbol, stockExchange, companyName, triggerPercentage, dateAdded):
        self.db.insert_user_stock(chatID, userID, stockSymbol,
                                  stockExchange, companyName, triggerPercentage, dateAdded)

    def viewUserStocks(self, userID):
        message = None
        status = 1
        list = []
        count = 1
        for (a, b, c, d) in self.db.select_all_user_stocks(userID):
            list.append('{}) <b>{}:{}</b>: {}'.format(count, c, b, d))
            count += 1
        message = "{}, here's the list of stocks you saved:\n\n".format(
            userID) + "\n".join(list)
        if not list:
            message = "It appears you do not have any stocks saved. You can save a stock by selecting <b>Add a stock</b>."
            status = 0
        return (message, status)

    def deleteUserStock(self, userID, userInput):
        userInput = userInput.split(':')
        try:
            self.db.delete_user_stock(userID, userInput[1], userInput[0])
            message = "<b>{}:{}</b> has been removed.".format(
                userInput[0], userInput[1])
            return message
        except:
            message = "Sorry, that's not a valid input!"
            return message

    def extractKeyStockInformation(self, stockSymbol, stockExchange, companyName):
        message = None
        Dates, Prices = self.getFullPriceHistory(stockSymbol, stockExchange)
        closingPrices = copy.deepcopy(Prices)
        highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold = self.calculateSensitivityTriggerRates(
            closingPrices)
        message = ("<b>{} Report</b>\n\n" +
                   "The current price of the stock is <i>${}</i>.\n\n" +
                   "Here are the available sensitivities (the greater the sensitivity, the higher the alert rate):\n" +
                   "HIGH (~6 alerts/month): <i>{}%</i>\n" +
                   "MEDIUM (~3 alerts/month): <i>{}%</i>\n" +
                   "LOW (~1 alert/month): <i>{}%</i>\n\n" +
                   "<i>This report is accurate as of {}, which is the latest trading date identified.</i>").format(companyName, round(Prices[0], 2), highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold, Dates[0])
        return (message, Prices[0], highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold)

    def extractTriggeredStocks(self):
        userIDs = []
        messages = []
        for (a, b, c, d, e, f) in self.db.select_all_stocks_triggered():
            userIDs.append(a)
            messages.append(
                "<b>ALERT!</b>\n\nThreshold for <b>{}:{} - {}</b> has been exceeded!\n\n3/15MA threshold set: <i>{}</i>\nLatest 3/15MA calculated: <i>{}</i>".format(c, b, d, e, f))
        return (userIDs, messages)

    def clearChatFromApp(self, chatID):
        self.db.delete_chat_from_app(chatID)

    # 3

    def getFullPriceHistory(self, stockSymbol, stockExchange):
        response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}:{}&outputsize=full&apikey={}".format(
            stockExchange, stockSymbol, self.ALPHA_VANTAGE_SECRET_KEY))
        data = response.json()
        timestamps, aClose = [], []
        for key in data['Time Series (Daily)']:
            timestamps.append(key)
        dates = [datetime.strptime(
            ts, "%Y-%m-%d") for ts in timestamps]
        dates.sort()
        dates.reverse()
        Dates = [datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
        for date in Dates:
            aClose.append(
                float(data['Time Series (Daily)'][date]['5. adjusted close']))
        return (Dates, aClose)

    def getCompactPriceHistory(self, stockSymbol, stockExchange):
        response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}:{}&apikey={}".format(
            stockExchange, stockSymbol, self.ALPHA_VANTAGE_SECRET_KEY))
        data = response.json()
        timestamps, aClose = [], []

        for key in data['Time Series (Daily)']:
            timestamps.append(key)
        dates = [datetime.strptime(
            ts, "%Y-%m-%d") for ts in timestamps]
        dates.sort()
        dates.reverse()
        Dates = [datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
        for date in Dates:
            aClose.append(
                float(data['Time Series (Daily)'][date]['5. adjusted close']))
        return (Dates, aClose)

    def calculateLatestThreeDayMA(self, closingPrices):
        return ((closingPrices[0]+closingPrices[1]+closingPrices[2])/3)

    def calculateLatestFifteenDayMA(self, closingPrices):
        fifteenDayMovingAverage = 0
        for i in range(3, 18):
            fifteenDayMovingAverage = fifteenDayMovingAverage + \
                closingPrices[i]
        fifteenDayMovingAverage = fifteenDayMovingAverage/15
        return fifteenDayMovingAverage

    def calculatePercentChange(self, oldValue, newValue):
        return (((newValue - oldValue)/oldValue)*100)

    def createThreeFifteenPercentChangesList(self, closingPrices):
        percentageChangesList = []
        for i in range(len(closingPrices)-18):
            threeDayMovingAverage = self.calculateLatestThreeDayMA(
                closingPrices)
            fifteenDayMovingAverage = self.calculateLatestFifteenDayMA(
                closingPrices)
            percentageChange = self.calculatePercentChange(
                fifteenDayMovingAverage, threeDayMovingAverage)
            percentageChangesList.append(percentageChange)
            del closingPrices[0]
        return percentageChangesList

    def calculateSensitivityTriggerRates(self, closingPrices):
        '''
        Assuming normal distribution
        High: ~6 triggers per month (6/30 -> 20%) --> z-score = -0.8416212335
        Medium: ~3 triggers per month (3/30 -> 10%) --> z-score = -1.281551567
        Low: ~1 triggers per month (1/30 -> 3.33%) --> z-score = -1.833914682

        z-score = ((threshold - mean)/std)
        threshold = (z-score * std) + mean
        '''
        latestThreeYearsClosingPrices = closingPrices[:1200]
        percentageChangesList = self.createThreeFifteenPercentChangesList(
            closingPrices)
        mean = np.mean(percentageChangesList)
        std = np.std(percentageChangesList)

        highSensitivityThreshold = round((-0.8416212335*std) + mean, 2)
        medSensitivityThreshold = round((-1.281551567*std) + mean, 2)
        lowSensitivityThreshold = round((-1.833914682*std) + mean, 2)

        return(highSensitivityThreshold, medSensitivityThreshold, lowSensitivityThreshold)

    def calculateCurrentPercentageChange(self, Prices):
        threeDayMovingAverage = self.calculateLatestThreeDayMA(Prices)
        fifteenDayMovingAverage = self.calculateLatestFifteenDayMA(Prices)
        percentageChange = self.calculatePercentChange(
            fifteenDayMovingAverage, threeDayMovingAverage)
        return percentageChange


    def retrieveAllDistinctStocks(self):
        return self.db.select_all_distinct_stocks()

    def getLatestPercentageChange(self, stockSymbol, stockExchange, currentDate):
        Dates, Prices = self.getCompactPriceHistory(
            stockSymbol, stockExchange)
        if (Dates[0] == currentDate):
            latestPercentageChange = self.calculateCurrentPercentageChange(
                Prices)
            return latestPercentageChange
        else:
            return None

    def storeLatestPercentageChange(self, stockSymbol, stockExchange, currentDate, latestPercentageChange):
        self.db.insert_stock_latestPercentageChange(
            stockSymbol, stockExchange, currentDate, latestPercentageChange)

    def checkIfPercentageChangesUpdated(self, currentDate):
        updatedStocks = self.db.select_stocks_by_dateAdded(currentDate)
        if (len(updatedStocks) == 0):
            return False
        else:
            return True

    def updatePriceOfExistingStocks(self):
        currentDate = str(datetime.now().strftime("%Y-%m-%d"))
        listOfStocks = self.retrieveAllDistinctStocks()
        isPercentageChangeUpdated = self.checkIfPercentageChangesUpdated(
            currentDate)
        
        if not isPercentageChangeUpdated:
            print("PercentageChanges not updated. Commencing update now...")
            for stockSymbol, stockExchange in listOfStocks:
                latestPercentageChange = self.getLatestPercentageChange(
                    stockSymbol, stockExchange, currentDate)
                if latestPercentageChange is not None:
                    self.storeLatestPercentageChange(
                        stockSymbol, stockExchange, currentDate, latestPercentageChange)
                    print("{} updated.".format(stockSymbol))
            print("Update complete.")
        else:
            print("Prices are already up to date.")
