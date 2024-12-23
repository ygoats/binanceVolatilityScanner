#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 05:17:10 2020

@ygoats
"""

from binance.client import Client
from binance.enums import *

import apiDataVol

import telegram_send

from time import sleep

from datetime import datetime

from requests import exceptions

##############################################################################################
#############PARSING SELENIUM#################################################################
##############################################################################################

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC1
from selenium.webdriver.common.by import By

##############################################################################################

import os

usdtList = []
symbol_list = []
client = Client(apiDataVol.APIKey, apiDataVol.SecretKey)
symbols = client.get_ticker()

lensymbol = len(symbols)

usdt = 'USDT'

for s in range(lensymbol):
    string = symbols[s]['symbol']
    if usdt in string:
        usdtList.append(string)

symbol_list = usdtList
#print(symbol_list)

def listUpdate():
    now = datetime.now()
    tt = now.strftime("%H:%M:%S")
            
    if tt >= "18:00:00" and tt <= "18:00:30":
        usdtList = []
        symbol_list = []
        client = Client(apiDataVol.APIKey, apiDataVol.SecretKey)
        symbols = client.get_ticker()

        lensymbol = len(symbols)

        usdt = 'USDT'

        for s in range(lensymbol):
            string = symbols[s]['symbol']
            if usdt in string:
                usdtList.append(string)

        symbol_list = usdtList
        #print(symbol_list)
        
def trade():
    
    lenList = len(symbol_list)
    now = datetime.now()
    t = now.strftime("%m/%d/%Y, %H:%M:%S")
    LITR = True
    conNode = False
        
    for s in range(lenList):
        sleep(.30)
        print(symbol_list[s])
        atrList = []
        volList = []
        try:
            client = Client(apiDataVol.APIKey, apiDataVol.SecretKey)
            klines = client.get_klines(symbol=symbol_list[s],interval=KLINE_INTERVAL_15MINUTE, limit=21)
        except Exception as e:
            pd = open('logs/binanceVolAtr.log', 'a')
            pd.write("\n" + str(t) + str(e))
            pd.close()
            print(str(e))
            sleep(60)
            conNode = True
            
        while conNode == True:
            try:
                client = Client(apiDataVol.APIKey, apiDataVol.SecretKey)
                klines = client.get_klines(symbol=symbol_list[s],interval=KLINE_INTERVAL_15MINUTE, limit=21)
                conNode = False  
            except Exception as e:
                pd = open('logs/binanceVolAtr.log', 'a')
                pd.write("\n" + str(t) + str(e))
                pd.close()
                print(str(e))
                sleep(60)
                conNode = True 
           
        try:
            for b in range(21):
                volNodeFinder = float(klines[b][5])
                volList.append(volNodeFinder)
                pRise = float(klines[b][2])-float(klines[b][3])
                atrList.append(pRise)
        except IndexError as e:
            print(e)
            lenList = float(lenList) - 1 
            continue
        except KeyError as e:
            print(e)
            lenList = float(lenList) - 1 
            continue
            
        index = volList.index(max(volList))
        index2 = atrList.index(max(atrList))
        
        volList.sort()
        atrList.sort()
        
        volNode = float(volList[20])
        vol2Node = float(volList[19])
        
        atrNode = float(atrList[20])
        atr2Node = float(atrList[19])
        
        try:
            volMult = float(volNode)/float(vol2Node) #highest vol node vs second highest node
            atrMult = float(atrNode)/float(atr2Node) #high atr node vs second highest
        except ZeroDivisionError as e:
            volMult = 1
            atrMult = 1
            
        currentOpen = float(klines[20][1])
        currentClose = float(klines[20][4])

        if index == 20 and index2 == 20 and volMult > 2 and atrMult > 2:
            
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            wait_time = 25 # a very long wait time
            options = webdriver.ChromeOptions()
            options.headless = True
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--window-size=1920,1080")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument("--disable-extensions")
            options.add_argument("--proxy-server='direct://'")
            options.add_argument("--proxy-bypass-list=*")
            options.add_argument("--start-maximized")
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            driver = webdriver.Chrome(executable_path="/home/nord/66/chromedriver", options=options)
            
            sleep(1)
            
            driver.get ("https://in.tradingview.com/chart/?symbol=" + str(symbol_list[s]))
            
            driver.maximize_window()
            sleep(1)
            ActionChains(driver).send_keys('1').perform()
            sleep(1)
            ActionChains(driver).send_keys('5').perform()
            sleep(1)
            ActionChains(driver).key_down(Keys.ENTER).perform()
            sleep(1)
            ActionChains(driver).key_down(Keys.ALT).send_keys('s').perform()
            
            element = WebDriverWait(driver, wait_time).until(EC1.element_to_be_clickable((By.LINK_TEXT, 'Save image')))
            element.click()
            time.sleep(1)
            driver.close()
            
            filelist= list([file for file in os.listdir('/home/nord/66/') if file.endswith('.png')])
            
            with open(filelist[0], "rb") as f:
            	telegram_send.send(disable_web_page_preview=True, conf='user1.conf', images=[f], captions=["|||||Volatility [Binance]||||| " + str(symbol_list[s]) + " " + str(currentClose) \
                                    + "\n" + "https://www.binance.com/en/trade/" + str(symbol_list[s]) + "?type=spot"])
            
            os.remove(filelist[0])

            filelist = []
                
            symbol_list.remove(symbol_list[s])
            break
  
def Main():        
    now = datetime.now()
    t = now.strftime("%m/%d/%Y, %H:%M:%S")
    
    print("Connection Established [BinanceVolAtr]")
    print(str(t))

    conNode = False  
    
    while conNode == False:
        trade()
        listUpdate()
        
if __name__ == '__main__':
    Main()
