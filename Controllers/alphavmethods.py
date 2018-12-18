import json
import requests
import numpy as np
import copy

def getFullPriceHistory(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY):
	response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}:{}&outputsize=full&apikey={}".format(stockExchange, stockSymbol, ALPHA_VANTAGE_SECRET_KEY))
	data = response.json()
	Dates, aClose = [],[]
	for key, value in data['Time Series (Daily)'].items():
		Dates.append(key)	
		aClose.append(float(value['5. adjusted close']))
	return (Dates, aClose)

def getCompactPriceHistory(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY):
	response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}:{}&apikey={}".format(stockExchange, stockSymbol, ALPHA_VANTAGE_SECRET_KEY))
	data = response.json()
	Dates, aClose = [],[]
	for key, value in data['Time Series (Daily)'].items():
		Dates.append(key)	
		aClose.append(float(value['5. adjusted close']))
	return (Dates, aClose)

def calculateLatestThreeDayMA(closingPrices):
    return ((closingPrices[0]+closingPrices[1]+closingPrices[2])/3)

def calculateLatestFifteenDayMA(closingPrices):
	fifteenDayMovingAverage = 0
	for i in range(3, 18):
		fifteenDayMovingAverage = fifteenDayMovingAverage + closingPrices[i]
	fifteenDayMovingAverage = fifteenDayMovingAverage/15
	return fifteenDayMovingAverage

def calculatePercentChange(oldValue, newValue):
	return (((newValue - oldValue)/oldValue)*100)

def createThreeFifteenPercentChangesList(closingPrices):
	percentageChangesList = []
	for i in range(len(closingPrices)-18):
		threeDayMovingAverage = calculateLatestThreeDayMA(closingPrices)
		fifteenDayMovingAverage = calculateLatestFifteenDayMA(closingPrices)
		percentageChange = calculatePercentChange(fifteenDayMovingAverage, threeDayMovingAverage)
		percentageChangesList.append(percentageChange)
		del closingPrices[0]
	return percentageChangesList

def calculateSensitivityTriggerRates(Prices):
	'''
	ADD DOCUMENTATION
	# Assuming normal distribution
	High: ~6 triggers per month (6/30 -> 20%) --> z-score = -0.8416212335
	Medium: ~3 triggers per month (3/30 -> 10%) --> z-score = -1.281551567
	Low: ~1 triggers per month (1/30 -> 3.33%) --> z-score = -1.833914682

	z-score = ((threshold - mean)/std)
	threshold = (z-score * std) + mean
	'''
	closingPrices = copy.deepcopy(Prices)
	latestThreeYearsClosingPrices = closingPrices[:1200]
	percentageChangesList = createThreeFifteenPercentChangesList(closingPrices)
	mean = np.mean(percentageChangesList)
	std = np.std(percentageChangesList)
	
	highSensitivityThreshold = round((-0.8416212335*std) + mean, 2)
	medSensitivityThreshold = round((-1.281551567*std) + mean, 2)
	lowSensitivityThreshold = round((-1.833914682*std) + mean, 2)

	return(highSensitivityThreshold,medSensitivityThreshold,lowSensitivityThreshold)

def calculateCurrentPercentageChange(Prices):
	threeDayMovingAverage = calculateLatestThreeDayMA(Prices)
	fifteenDayMovingAverage = calculateLatestFifteenDayMA(Prices)
	percentageChange = calculatePercentChange(fifteenDayMovingAverage, threeDayMovingAverage)
	return percentageChange