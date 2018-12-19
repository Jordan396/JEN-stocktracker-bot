# JEN-stocktracker-bot

**DISCLAIMER**

Do your Own Research. _JEN_ is intended to be used and must be used for informational purposes only. It is very important to do your own analysis before making any investment based on your own personal circumstances. You should take independent financial advice from a professional in connection with, or independently research and verify, any information that you find using _JEN_ and wish to rely upon, whether for the purpose of making an investment decision or otherwise.

_This disclaimer has been adapted from [stockopedia](https://www.stockopedia.com/page/disclaimer/)_.

---

## Project Overview

![JEN_logo](img/JEN.JPG?raw=true "JEN_logo")

*“Opportunities come infrequently. When it rains gold, put out the bucket, not the thimble.” - Warren Buffet*

Stock prices often fall drastically when market participants are pessimistic and desperate to get rid of their stocks. While this is terrible for those in the selling position, it presents _fantastic buying opportunities_ for other investors. However, for [passive investors](https://www.investopedia.com/terms/p/passiveinvesting.asp) like myself who do not monitor stock prices on a daily basis, it is easy to miss out on such opportunities.

---

_JEN_ was created to tackle this issue. Using statistical theory, this **Telegram** bot formulates various _3/15MA_ thresholds for users. At the end of each day, if the latest stock price changes exceed the user's selected threshold, _JEN_ sends a notification. Each threshold corresponds to a sensitivity level and this affects the frequency of notifications.

Currently, _JEN_ only supports stocks traded on the _NYSE_ and _NASDAQ_ as of _16 December 2018_.

**To access _JEN_:** 

1. Click on this [link](https://t.me/stocktracker_JENbot); or 
2. Search for **@stocktracker_JENbot** on Telegram

---

## How does JEN work?
### Technical Details
_JEN's_ inner workings can be broken down into two main segments - the **Telegram bot** and a supplementary **cronjob**.

The Telegram bot segment can be further divided into four layers:
* **Bot framework layer** (_JEN.py_). This bot relies on the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework.
* **Bot support layer** (_Controllers/botmethods.py_). Acts as an intermediary layer between the framework layer and the other layers, which supports the [Interface Segregation Principle](https://en.wikipedia.org/wiki/Interface_segregation_principle).
* **Database access layer** (_Controllers/dbhelper.py_). Handles interactions with the _SQLITE_ database.
* **AlphaVantage interface layer** (_Controllers/alphavmethods.py_). Handles interactions with the [AlphaVantage API](https://www.alphavantage.co/).

In addition, a cronjob which executes the *price_updater.py* script is deployed. This script extracts the latest daily [adjusted closing price](https://www.investopedia.com/terms/a/adjusted_closing_price.asp) from the AlphaVantage API and updates the database.

The table below describes the sequence of events and their respective triggers.

| Event                                                     | Trigger                             |
|:---------------------------------------------------------:|:-----------------------------------:|
| User adds a stock to DB                                   | Upon confirmation of addition       |
| AlphaVantage API begins updating endpoint                 | 0930 GMT-5 (when markets open)      |
| AlphaVantage API stops updating endpoint                  | 1600 GMT-5 (when markets close)     |
| AlphaVantage API submits final adjusted closing price     | 2030 GMT-5                          |
| Cronjob fetches prices for all stocks saved in DB         | 2100 GMT-5                          |
| JEN compares latest 3/15MA against users' threshold       | 2115 GMT-5                          |

_Due to the above configuration, stocks submitted after 2100 GMT-5 will only be evaluated against the latest 3/15MA on the following day, at 2115 GMT-5._

### Statistical Analysis
From the stock prices extracted from AlphaVantage, we calculate the [moving averages](https://www.investopedia.com/terms/m/movingaverage.asp) over a three day period (3DMA) and a fifteen day period (15DMA) for each day. Note that the fifteen days used in the 15DMA calculation refers to the fifteen days _prior_ to the three days used in 3DMA calculation. 

The above time periods were chosen based on analyzing the **medium volatility SPDR500 market index stock**. Ideally, each stock should have its own X/Y moving average ratio depending on its volatility. However, since _JEN_ is only in its initial stage, the stock above was chosen. 

With our lists of 3DMA and 15DMA values, we can calculate the percentage change from the 15DMA to its corresponding 3DMA, for each of the MA values.

![3_15_MAs_percentage_change_graph](img/3_15_MAs_percentage_change_graph.JPG?raw=true "315MA_percentage_change_graph")

Observe that the graph above follows an **approximate normal distribution** (and we shall assume it to be as such). 

![68–95–99.7_rule_histogram](img/Empirical_rule_histogram.svg.png?raw=true "Empirical_rule_histogram")

With the aid of the **68–95–99.7 rule**, three notification frequencies are proposed. Using the *mean*, *standard deviation* and the *z-score formula* for a normal distribution, we can calculate the z-score for each notification frequency as shown.

| Threshold Options         | Notification Frequency        | Z-Score                             |
|:-------------------------:|:-----------------------------:|:-----------------------------------:|
| HIGH                      | ~6 notifs/month (6/30 = 20%)  | -0.8416212335                       |
| MEDIUM                    | ~3 notifs/month (3/30 = 10%)  | -1.281551567                        |
| LOW                       | ~1 notifs/month (1/30 = 3.33%)| -1.833914682                        |

We can then use these z-scores to find the threshold percentage for each option. 

`ThresholdPercentage = (z-score * std) + mean`

## Setting up the Application

These instructions assume setup on an **Ubuntu 16.04.5 LTS** operating system and the server timezone is **GMT+0**.

*Take note of the timezone as it affects DEPLOYMENT_DATETIME and CRONJOB below! Refer to timing table above.*

#### 1) Obtaining Credentials
To access the AlphaVantage API, you'll need an API key which can be obtained [here](https://www.alphavantage.co/support/#api-key).
You'll also need to obtain a token from Telegram's [BotFather](https://core.telegram.org/bots#6-botfather).

#### 2) Setting up Environment
Clone this repository.

`git clone https://github.com/Jordan396/JEN-stocktracker-bot.git`

`cd JEN-stocktracker-bot/`

You'll need to create a _config.py_ file to store your API keys and other configuration settings.

`vim config.py`

Add the following lines. Note that DEPLOYMENT_DATETIME must be @2115 GMT-5.
```
TELEGRAM_BOT_SECRET_KEY = [TELEGRAM BOT TOKEN]
ALPHA_VANTAGE_SECRET_KEY = [ALPHAVANTAGE API KEY]
DEPLOYMENT_DATETIME = [DEPLOYMENT DATETIME (e.g. 'MM/DD/YY 02:15:00')]
```

#### 3) Install Cronjob
We'll need to install the cronjob to update prices every day @2100 GMT-5.

`crontab -e`

Add the following line.

`0 2 * * * cd [PATH TO JEN-stocktracker-bot] && [PATH TO JEN-stocktracker-bot/venv/bin/python] [PATH TO JEN-stocktracker-bot/price_updater.py]`

Once you save the file, the cronjob will be installed.

#### 4) Start JEN bot
The last thing we'll have to do is start _JEN_!

Open up a _tmux_ terminal.

`tmux`

Navigate back to JEN-stocktracker-bot and activate the virtual environment where all dependencies are already installed (if not, install requirements.txt).

`source venv/bin/activate`

Lastly, run _JEN.py_.

`python JEN.py`

Detach from the terminal and you're done!

## Future Improvements
* Add support for same ticker symbols on different exchanges
* Implement flexible X/Y moving average thresholds for stocks of different volatilities

If you'd like to contribute to _JEN_, or to improve anything at all really, I'd love to have a chat with you! Please feel free to contact me at [jordan.chyehong@gmail.com](jordan.chyehong@gmail.com).