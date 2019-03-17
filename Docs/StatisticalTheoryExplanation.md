# Statistical Theory Explanation

## Application Details
_JEN_ follows the Model-View-Control design pattern.
* **View layer** (_JEN.py_): Handles interactions with the user.
* **Control layer** (_Controllers/botmethods.py_): Handles logic of the bot.
* **Database/Model layer** (_Controllers/dbhelper.py_). Handles interactions with the _SQLITE_ database.

In addition, a cronjob which executes the *price_updater.py* script is deployed. This script extracts the latest daily [adjusted closing price](https://www.investopedia.com/terms/a/adjusted_closing_price.asp) from the AlphaVantage API and updates the database.

## Statistical Analysis
From the stock prices extracted from AlphaVantage, we calculate the [moving averages](https://www.investopedia.com/terms/m/movingaverage.asp) over a three day period (3DMA) and a fifteen day period (15DMA) for each day. Note that the fifteen days used in the 15DMA calculation refers to the fifteen days _prior_ to the three days used in 3DMA calculation. 

The above time periods were chosen based on analyzing the **medium volatility SPDR500 market index stock**. Ideally, each stock should have its own X/Y moving average ratio depending on its volatility. However, since _JEN_ is only in its initial stage, the stock above was chosen. 

With our lists of 3DMA and 15DMA values, we can calculate the percentage change from the 15DMA to its corresponding 3DMA, for each of the MA values.

![3_15_MAs_percentage_change_graph](../img/3_15_MAs_percentage_change_graph.JPG?raw=true "315MA_percentage_change_graph")

Observe that the graph above follows an **approximate normal distribution** (and we shall assume it to be as such). 

![68–95–99.7_rule_histogram](../img/Empirical_rule_histogram.svg.png?raw=true "Empirical_rule_histogram")

With the aid of the **68–95–99.7 rule**, three notification frequencies are proposed. Using the *mean*, *standard deviation* and the *z-score formula* for a normal distribution, we can calculate the z-score for each notification frequency as shown.

| Threshold Sensitivity Options | Notification Frequency        | Z-Score                             |
|:-----------------------------:|:-----------------------------:|:-----------------------------------:|
| HIGH                          | ~6 notifs/month (6/30 = 20%)  | -0.8416212335                       |
| MEDIUM                        | ~3 notifs/month (3/30 = 10%)  | -1.281551567                        |
| LOW                           | ~1 notifs/month (1/30 = 3.33%)| -1.833914682                        |

We can then use these z-scores to find the threshold percentage for each option. 

`ThresholdPercentage = (z-score * std) + mean`