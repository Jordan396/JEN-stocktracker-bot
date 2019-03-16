# -*- coding: utf-8 -*-
"""Example Google style docstrings.
This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.
Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::
        $ python example_google.py
Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.
Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.
        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.
Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension
.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html
"""

import config
import sqlite3
import datetime
import requests

from Controllers.dbhelper import DBHelper
import Controllers.alphavmethods as alphavmethods

ALPHA_VANTAGE_SECRET_KEY = config.ALPHA_VANTAGE_SECRET_KEY

db = DBHelper()

def retrieveAllDistinctStocks():
    return db.select_all_distinct_stocks()


def getLatestPercentageChange(stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY, currentDate):
    Dates, Prices = alphavmethods.getCompactPriceHistory(
        stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY)
    if (Dates[0] == currentDate):
        latestPercentageChange = alphavmethods.calculateCurrentPercentageChange(
            Prices)
        return latestPercentageChange
    else:
        return None


def storeLatestPercentageChange(stockSymbol, stockExchange, currentDate, latestPercentageChange):
    db.insert_stock_latestPercentageChange(
        stockSymbol, stockExchange, currentDate, latestPercentageChange)


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
            latestPercentageChange = getLatestPercentageChange(
                stockSymbol, stockExchange, ALPHA_VANTAGE_SECRET_KEY, currentDate)
            if latestPercentageChange is not None:
                storeLatestPercentageChange(
                    stockSymbol, stockExchange, currentDate, latestPercentageChange)
                print("{} updated.".format(stockSymbol))
        print("Update complete.")
    else:
        print("Prices are already up to date.")


if __name__ == '__main__':
    main()
