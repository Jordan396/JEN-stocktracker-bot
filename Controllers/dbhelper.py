# -*- coding: utf-8 -*-
"""Model/Database layer for JEN.py.

This script defines the class `DBHelper`. The DBHelper
class interacts directly with the SQLITE database. 
By creating a separate object, we avoid mixing the
control and model layer in the MVC design pattern.

This script is not to be executed on it's own!
"""

# Import common modules
import sqlite3
import json
import csv


class DBHelper:
    """The Model/Database layer for JEN.

    Please ensure that your ALPHA_VANTAGE_SECRET_KEY has
    been configured correctly.
    Attributes:
        dbname (str): The name of the database.
    """
    def __init__(self, dbname="JEN.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname,  check_same_thread=False)
        self.c = self.conn.cursor()

    def create_Stocks_table(self):
        stmt = "CREATE TABLE IF NOT EXISTS Stocks (chatID text NOT NULL, userID text NOT NULL, stockSymbol text NOT NULL, stockExchange text NOT NULL, companyName text NOT NULL, triggerPercentage real NOT NULL, dateAdded text NOT NULL);"
        self.conn.execute(stmt)
        self.conn.commit()

    def create_PercentageChanges_table(self):
        stmt = "CREATE TABLE IF NOT EXISTS PercentageChanges (stockSymbol text NOT NULL, stockExchange text NOT NULL, dateAdded text NOT NULL, latestPercentageChange real NOT NULL);"
        self.conn.execute(stmt)
        self.conn.commit()

    def create_Users_table(self):
        stmt = "CREATE TABLE IF NOT EXISTS Users (userID text NOT NULL);"
        self.conn.execute(stmt)
        self.conn.commit()

    def create_AllStocks_table(self):
        stmt = "CREATE TABLE IF NOT EXISTS AllStocks (stockSymbol text PRIMARY KEY, stockExchange text NOT NULL, companyName text NOT NULL);"
        self.conn.execute(stmt)
        self.conn.commit()

    def check_if_table_empty(self, tableName):
        stmt = "SELECT COUNT(*) FROM {};".format(tableName)
        result = self.c.execute(stmt).fetchone()
        self.conn.commit()
        return result[0]

    def insert_AllStocks_values(self):
        with open("Datasets/companylist_full.csv", "r") as read_file:
            csvreader = csv.reader(read_file, delimiter=',', quotechar='"')
            for entry in csvreader:
                stmt = "INSERT INTO AllStocks (stockSymbol, stockExchange, companyName) VALUES (?, ?, ?);"
                args = (entry[0], entry[-1], entry[1])
                self.conn.execute(stmt, args)
                self.conn.commit()

    def insert_user_stock(self, chatID, userID, stockSymbol, stockExchange, companyName, triggerPercentage, dateAdded):
        stmt = "INSERT INTO Stocks (chatID, userID, stockSymbol, stockExchange, companyName, triggerPercentage, dateAdded) VALUES (?, ?, ?, ?, ?, ?, ?);"
        args = (chatID, userID, stockSymbol, stockExchange,
                companyName, triggerPercentage, dateAdded)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def insert_stock_latestPercentageChange(self, stockSymbol, stockExchange, dateAdded, latestPercentageChange):
        stmt = "INSERT INTO PercentageChanges (stockSymbol, stockExchange, dateAdded, latestPercentageChange) VALUES (?, ?, ?, ?);"
        args = (stockSymbol, stockExchange, dateAdded, latestPercentageChange)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def insert_new_user(self, userID):
        stmt = "INSERT INTO Users (userID) VALUES (?)"
        args = (userID,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def select_company_name(self, stockSymbol):
        stmt = "SELECT stockSymbol, stockExchange, companyName FROM AllStocks WHERE stockSymbol = (?);"
        args = (stockSymbol,)
        result = self.c.execute(stmt, args).fetchone()
        self.conn.commit()
        return result

    def select_user(self, userID):
        stmt = "SELECT userID FROM Users WHERE userID = (?);"
        args = (userID,)
        result = self.c.execute(stmt, args).fetchone()
        self.conn.commit()
        return result

    def select_all_user_stocks(self, userID):
        stmt = "SELECT userID, stockSymbol, stockExchange, companyName FROM Stocks WHERE userID = (?);"
        args = (userID,)
        result = self.c.execute(stmt, args).fetchall()
        self.conn.commit()
        return result

    def select_all_distinct_stocks(self):
        stmt = "SELECT DISTINCT stockSymbol, stockExchange FROM Stocks;"
        result = self.c.execute(stmt).fetchall()
        self.conn.commit()
        return result

    def select_stocks_by_dateAdded(self, dateAdded):
        stmt = "SELECT stockSymbol FROM PercentageChanges WHERE dateAdded = (?);"
        args = (dateAdded,)
        result = self.c.execute(stmt, args).fetchall()
        self.conn.commit()
        return result

    def select_all_stocks_triggered(self):
        stmt = "SELECT S.chatID, S.stockSymbol, S.stockExchange, S.companyName, S.triggerPercentage, P.latestPercentageChange FROM Stocks AS S INNER JOIN PercentageChanges AS P ON S.stockSymbol = P.stockSymbol AND S.stockExchange = P.stockExchange WHERE P.latestPercentageChange < S.triggerPercentage;"
        result = self.c.execute(stmt).fetchall()
        self.conn.commit()
        return result

    def delete_user_stock(self, userID, stockSymbol, stockExchange):
        stmt = "DELETE FROM Stocks WHERE userID = (?) AND stockSymbol = (?) AND stockExchange = (?);"
        args = (userID, stockSymbol, stockExchange)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_chat_from_app(self, chatID):
        stmt = "DELETE FROM Stocks WHERE chatID = (?);"
        args = (chatID,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def setup_database(self):
        print("Creating Stocks table...")
        self.create_Stocks_table()
        print("Creating Users table...")
        self.create_Users_table()
        print("Creating AllStocks table...")
        self.create_PercentageChanges_table()
        print("Creating PercentageChanges table...")
        self.create_AllStocks_table()
        print("Creating AllStocks table...")
        if (self.check_if_table_empty("AllStocks") == 0):
            print(
                "AllStocks table created. Inserting values from Datasets/companylist_full.csv...")
            self.insert_AllStocks_values()
        else:
            print("AllStocks table already exists.")
