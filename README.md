# JEN-stocktracker-bot

**DISCLAIMER**

Do your Own Research. _JEN_ is intended to be used and must be used for informational purposes only. It is very important to do your own analysis before making any investment based on your own personal circumstances. You should take independent financial advice from a professional in connection with, or independently research and verify, any information that you find using _JEN_ and wish to rely upon, whether for the purpose of making an investment decision or otherwise.

_This disclaimer has been adapted from [stockopedia](https://www.stockopedia.com/page/disclaimer/)_.

---

## Project Overview

To access this bot: 
1. Click on this [link](t.me/stocktracker_JENbot); or 
2. Search for **@stocktracker_JENbot** on Telegram

---

_JEN_ is a Telegram bot that keeps track of stock prices. This bot has been designed for [passive investors](https://www.investopedia.com/terms/p/passiveinvesting.asp) who prefer not to monitor stock prices on a daily basis. 

Essentially, _JEN_ performs statistical analysis on your selected stock and presents various sensitivity thresholds. Once a threshold is chosen, _JEN_ keeps track of the stock's daily [adjusted closing price](https://www.investopedia.com/terms/a/adjusted_closing_price.asp). Whenever price changes exceed this threshold, _JEN_ sends you a notification.

**NOTE: Currently, _JEN_ only supports stocks traded on the _NYSE_ and _NASDAQ_ as of _16 December 2018_.** If you'd like to lend your support to expand _JEN_ to other stock exchanges, or to improve anything at all really, please feel free to contact me at [jordan.chyehong@gmail.com](jordan.chyehong@gmail.com). 

## Application Details
### Technical Details
In general, _JEN's_ inner workings can be broken down into two main segments - the **Telegram bot** and a supplementary **cronjob**.

The Telegram bot segment can be further divided into four layers:
* **Bot framework layer** (_JEN.py_). This bot relies on the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework.
* **Bot support layer** (_Controllers/botmethods.py_). Acts as an intermediate layer between framework layer and the other layers, hence supporting the [Interface Segregation Principle](https://en.wikipedia.org/wiki/Interface_segregation_principle).
* **Database access layer** (_Controllers/dbhelper.py_). Handles interactions with the _SQLITE_ database.
* **AlphaVantage interface layer** (_Controllers/alphavmethods.py_). Handles interactions with the [AlphaVantage API](https://www.alphavantage.co/).

In addition, a cronjob which executes the *price_updater.py* script is deployed. This script extracts the latest daily adjusted closing price from the AlphaVantage API and updates the database.

The table below describes the sequence of events that occur and their respective triggers.

| Event                                                     | Trigger                             |
|:---------------------------------------------------------:|:-----------------------------------:|
| User adds a stock to DB                                   | Upon confirmation of addition       |
| AlphaVantage API begins updating endpoint                 | 0930 GMT-5 (when markets open)      |
| AlphaVantage API stops updating endpoint                  | 1600 GMT-5 (when markets close)     |
| AlphaVantage API submits final adjusted closing price     | 2030 GMT-5                          |
| Cronjob fetches prices for all stocks saved in DB         | 2100 GMT-5                          |
| JEN compares latest 3/15MA against users' threshold       | 2115 GMT-5                          |

*Due to the above configuration, stocks saved after 2100 GMT-5 will only be evaluated against the latest 3/15MA the following day at 2115 GMT-5 .*

### Statistical Analysis
TODO

![68–95–99.7_rule_histogram](img/Empirical_rule_histogram.svg.png?raw=true "Empirical_rule_histogram")



## Setting up the Application
TODO


## Future Improvements
* Add support for same ticker symbols on different exchanges