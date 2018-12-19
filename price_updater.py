import config
import sqlite3
import datetime
import requests

from Controllers.dbhelper import DBHelper
import Controllers.alphavmethods as alphavmethods

'''
NOTE: This script is to be executed by a cronjob DAILY @ 2100 GMT-5.
'''

ALPHA_VANTAGE_SECRET_KEY = config.ALPHA_VANTAGE_SECRET_KEY

db = DBHelper()


def retrieveAllDistinctStocks():
	return db.select_all_distinct_stocks()

def getLatestPercentageChange(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY, currentDate):
	Dates, Prices = alphavmethods.getCompactPriceHistory(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY)
	if (Dates[0] == currentDate):
		latestPercentageChange = alphavmethods.calculateCurrentPercentageChange(Prices)
		return latestPercentageChange
	else:
		return None

def storeLatestPercentageChange(stockSymbol, stockExchange, currentDate, latestPercentageChange):
	db.insert_stock_latestPercentageChange(stockSymbol, stockExchange, currentDate, latestPercentageChange)

def checkIfPercentageChangesUpdated(currentDate):
	updatedStocks = db.select_stocks_by_dateAdded(currentDate)
	if (len(updatedStocks) == 0):
		return False
	else:
		return True

def main():
	currentDate = str(datetime.datetime.now().strftime("%Y-%m-%d"))
	print(currentDate)
	listOfStocks = retrieveAllDistinctStocks()
	isPercentageChangeUpdated = checkIfPercentageChangesUpdated(currentDate)

	if not isPercentageChangeUpdated: 
		print("PercentageChanges not updated. Commencing update now...")
		for stockSymbol, stockExchange in listOfStocks:
			latestPercentageChange = getLatestPercentageChange(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY, currentDate)
			if latestPercentageChange is not None:
				storeLatestPercentageChange(stockSymbol, stockExchange, currentDate, latestPercentageChange)
				print("{} updated.".format(stockSymbol))
		print("Update complete.")
	else:
		print("Prices are already up to date.")

if __name__ == '__main__':
	main()