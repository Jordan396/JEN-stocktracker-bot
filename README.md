# JEN-stocktracker-bot

[![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)
[![Project License](https://img.shields.io/github/license/jordan396/JEN-stocktracker-bot.svg)](https://img.shields.io/github/license/jordan396/JEN-stocktracker-bot.svg)
[![Latest Commit](https://img.shields.io/github/last-commit/jordan396/JEN-stocktracker-bot/master.svg)](https://img.shields.io/github/last-commit/jordan396/JEN-stocktracker-bot/master.svg)
[![Repo Size](https://img.shields.io/github/repo-size/jordan396/JEN-stocktracker-bot.svg)](https://img.shields.io/github/repo-size/jordan396/JEN-stocktracker-bot.svg)
[![GitHub Followers](https://img.shields.io/github/followers/jordan396.svg?label=Follow)](https://img.shields.io/github/followers/jordan396.svg?label=Follow)

![JEN_logo](img/JEN.JPG?raw=true "JEN_logo")

_JEN_ is a telegram bot which notifies users when prices of their favourite stocks fall.

**To use _JEN_:** 
1. Click on this [link](https://t.me/stocktracker_JENbot); or 
2. Search for **@stocktracker_JENbot** on Telegram

---

## Project Overview

*“Opportunities come infrequently. When it rains gold, put out the bucket, not the thimble.” - Warren Buffet*

Stock prices may fall drastically when market participants are pessimistic. This presents _fantastic buying opportunities_ for investors. However, for [passive investors](https://www.investopedia.com/terms/p/passiveinvesting.asp) who do not monitor stock prices on a daily basis, it is easy to miss out on such opportunities.

_JEN_ was created to tackle this issue. Using statistical theory, _JEN_ formulates various _3/15MA_ thresholds for users. At the end of each day, if the latest stock price changes exceed the user's selected threshold, _JEN_ sends a notification. Each threshold corresponds to a sensitivity level and this affects the frequency of notifications sent.

Currently, _JEN_ only supports stocks traded on the _NYSE_ and _NASDAQ_ as of _16 March 2019_.

---


## Installation
### 1) Obtaining Credentials
To access the AlphaVantage API, you'll need an API key which can be obtained [here](https://www.alphavantage.co/support/#api-key).
You'll also need to obtain a token from Telegram's [BotFather](https://core.telegram.org/bots#6-botfather).

### 2) Setting up Environment
Clone this repository.
```
git clone https://github.com/Jordan396/JEN-stocktracker-bot.git
cd JEN-stocktracker-bot/
```

Create virual environment and install dependencies.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need to create a _config.py_ file to store your API keys and other configuration settings.

`vim config.py`

Add the following lines.
```
TELEGRAM_BOT_SECRET_KEY = [TELEGRAM BOT TOKEN]
ALPHA_VANTAGE_SECRET_KEY = [ALPHAVANTAGE API KEY]
```

### 3) Start JEN bot
The last thing we'll have to do is start _JEN_!
```
python JEN.py
```

---

## Future Improvements
* Add support for same ticker symbols on different exchanges
* Implement flexible X/Y moving average thresholds for stocks of different volatilities

If you'd like to contribute to _JEN_, or to improve anything at all really, I'd love to have a chat with you! Please feel free to contact me at [jordan.chyehong@gmail.com](mailto:jordan.chyehong@gmail.com).

---

## Disclaimer

Do your Own Research. _JEN_ is intended to be used and must be used for informational purposes only. It is very important to do your own analysis before making any investment based on your own personal circumstances. You should take independent financial advice from a professional in connection with, or independently research and verify, any information that you find using _JEN_ and wish to rely upon, whether for the purpose of making an investment decision or otherwise.

_This disclaimer has been adapted from [stockopedia](https://www.stockopedia.com/page/disclaimer/)_.
