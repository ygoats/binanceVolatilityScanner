# binanceVolatilityScanner

This is a volatility scanner with charts from tradingview for posting on telegram channels. Build for headless servers.

pip3 install telegram-send

pip3 install python-binance

pip3 install selenium

SETUP apiDataVol file with your api keys from kucoin

SETTING UP CHROMEDRIVER AND IMAGE POSTER

make sure to find the ##### portion of the code and write the directory for the script so that it can find the chromedriver and images it downloads

SETTING UP TELEGRAM

Go to @BotFather on telegram and setup an Bot with the easy to follow instructions.

Alternatively please use in the cli

telegram-send --configure

remove the conf = "user1.conf" from the telegram-send() portion of the code

