# -*- coding: utf-8 -*-
"""
Created on Sat Sep  23 16:31:55 2023

@author: ashwe
"""

from logger import *
import gvars
import configparser
import sys
from pya3 import *
import time
from traderlib import *
import datetime as dt
import pandas as pd
import csv 

global username
global api_key
global api

username = None
api_key = None
api = None

def get_user_info():
    # get user info from user for login and authentication.
        # IN: (from user)
        # OUT: True Once successful and exiting otherwise
    global username
    global api_key

    lg.info('getting user info ...')
    username = input("Enter username \n")
    api_key = input("Enter API key \n")

    config_path = './config/'
    config_obj = configparser.ConfigParser()
    config_file = config_path + "config.ini"

    config_obj.add_section('user_info')
    config_obj.set('user_info', 'username', username)
    config_obj.set('user_info', 'api_key', api_key)

    # creating s folder for the config
    try:
        os.mkdir(config_path)
    except OSError:
        lg.info('Creation of the directory %s failed - it does not have to be bad' % config_path)
    except Exception as err:
        lg.error(str(err))
        sys.exit()
    else:
        lg.info('Succesfully created config directory')

    # Write the new structure to the new file
    with open(config_file, 'w') as configfile:
        config_obj.write(configfile)

# initialize bot for trading account
def initialize_bot():
    # initialize the bot
        # IN: None
        # OUT: True initialize successful and exiting otherwise
    global username
    global api_key

    config_path = './config/'
    config_obj = configparser.ConfigParser()
    config_file = config_path + "config.ini"

    try:
        config_obj.read(config_file)
        userinfo = config_obj["user_info"]
        username = userinfo['username']
        api_key = userinfo['api_key']
        lg.info('Account username: %s, \nAccount key: %s \n' %(username, api_key))
    except KeyError as err:
        get_user_info()
    except Exception as err:
        lg.error(str(err))
        sys.exit()

    try:
        config_obj.read(config_file)
        userinfo = config_obj["user_info"]
    except Exception as err:
        lg.error(str(err))
        sys.exit()

    lg.info('Initializing BOT Successfull')
    return True

# check our trading account
def check_account_ok():
    # check whether the account is Active for trading
        # IN: api
        # OUT: True if it exists and is Active / False otherwise
    global api

    try:
        session_id = api.get_session_id() # Get Session ID
        # lg.info('Generated session_id, session_id: %s ' % session_id)
        if session_id['stat'] != 'Ok':
            if('ConnectionError' in str(session_id['emsg'])):
                lg.info('Connection error. Please check the speed of the Internet')
                lg.info('%s ' % session_id)
                sys.exit()
            lg.info('The account is not ACTIVE, aborting')
            sys.exit()
        else:
            if 'emsg' in session_id:
                lg.error('%s ' % session_id['emsg'])
                sys.exit()
    except Exception as err:
        lg.error('Could not get account info, aborting')
        lg.error(str(err))
        sys.exit()

    lg.info('The account is ACTIVE, Good to go ...')
    get_profile = api.get_profile() # get profile

    lg.info('Profile: %s ' % get_profile)

def get_candle_data(ticker, indices = False):
    from_datetime = datetime.now() - dt.timedelta(days=5)
    to_datetime = datetime.now()
    interval = "D" #1/D

    try:
        instrument = api.get_instrument_by_symbol(gvars.exch_seg, ticker)
        candle_data = api.get_historical(instrument, from_datetime, to_datetime, interval, indices)
    except Exception as err:
        lg.error(str(err))

        if('ConnectionError' in err):
            lg.error('Connection error. Please check the speed of the Internet')

    candle_data['datetime'] = pd.to_datetime(candle_data['datetime'])
    candle_data.set_index('datetime', inplace = True)

    return candle_data
    # return live_resampled_data

def hist_data(tickers, indices = False):
    hist_data_tickers = {}
    from_datetime = datetime.now() - dt.timedelta(days=5)
    to_datetime = datetime.now()
    interval = "D" #1/D

    for ticker in tickers:
        try:
            instrument = api.get_instrument_by_symbol(gvars.exch_seg, ticker)
            hist_data = api.get_historical(instrument, from_datetime, to_datetime, interval, indices)
            df_data = hist_data
            df_data['gain'] = ((df_data['close'] - df_data['open']) / df_data['open'])
            hist_data_tickers[ticker] = df_data
        except Exception as err:
            lg.error(str(err))

    return hist_data_tickers

def gen_report():
    print(gvars.f_str)
    with open('report.txt', 'w') as f:
        f.write(gvars.f_str)
        f.flush()
        f.close()

    # writing to csv file 
    with open(gvars.filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
        
        # writing the fields 
        csvwriter.writerow(gvars.csv_headr) 
        
        # writing the data rows 
        csvwriter.writerows(gvars.csv_body)

def main():
    global username
    global api_key
    global api

    # initialize the logger (imported from logger)
    initialize_logger()

    lg.info('Trading Bot running ... !')
    lg.info('------------------------------------')
    if(len(sys.argv) > 2):
        lg.info('STARTED ON: %s %s \r' %(sys.argv[1], sys.argv[2]))
    else:
        lg.info('STARTED ON: %s %s \r' %("0-0-0000", "00:00:00"))
    lg.info('------------------------------------ \n')

    # initialize bot
    initialize_bot()
    api = Aliceblue(user_id = username, api_key = api_key)

    # check our trading account
    check_account_ok()

    tickers = ["ABB",  "ACC",  "AUBANK",  "ABBOTINDIA",  "ADANIENT",  "ADANIGREEN",  "ADANIPORTS",  "ADANIPOWER",  "ATGL",  
                "ADANITRANS",  "AWL",  "ABCAPITAL",  "ABFRL",  "ALKEM",  "AMBUJACEM",  "APOLLOHOSP",  "APOLLOTYRE",  "ASHOKLEY",  
                "ASIANPAINT",  "ASTRAL",  "AUROPHARMA",  "DMART",  "AXISBANK",  "BAJAJ-AUTO",  "BAJFINANCE",  "BAJAJFINSV",  
                "BAJAJHLDNG",  "BALKRISIND",  "BANDHANBNK",  "BANKBARODA",  "BANKINDIA",  "BATAINDIA",  "BERGEPAINT",  "BEL",  
                "BHARATFORG",  "BHEL",  "BPCL",  "BHARTIARTL",  "BIOCON",  "BOSCHLTD",  "BRITANNIA",  "CGPOWER",  "CANBK",  
                "CHOLAFIN",  "CIPLA",  "COALINDIA",  "COFORGE",  "COLPAL",  "CONCOR",  "COROMANDEL",  "CROMPTON",  "CUMMINSIND",  
                "DLF",  "DABUR",  "DALBHARAT",  "DEEPAKNTR",  "DELHIVERY",  "DEVYANI",  "DIVISLAB",  "DIXON",  "LALPATHLAB",  
                "DRREDDY",  "EICHERMOT",  "ESCORTS",  "NYKAA",  "FEDERALBNK",  "FORTIS",  "GAIL",  "GLAND",  "GODREJCP",  
                "GODREJPROP",  "GRASIM",  "FLUOROCHEM",  "GUJGASLTD",  "HCLTECH",  "HDFCAMC",  "HDFCBANK",  "HDFCLIFE",  "HAVELLS",
                "HEROMOTOCO",  "HINDALCO",  "HAL",  "HINDPETRO",  "HINDUNILVR",  "HINDZINC",  "HONAUT",  "HDFC",  "ICICIBANK",  
                "ICICIGI",  "ICICIPRULI",  "IDFCFIRSTB",  "ITC",  "INDIANB",  "INDHOTEL",  "IOC",  "IRCTC",  "IRFC",  "IGL",  
                "INDUSTOWER",  "INDUSINDBK",  "NAUKRI",  "INFY",  "INDIGO",  "IPCALAB",  "JSWENERGY",  "JSWSTEEL",  "JINDALSTEL",  
                "JUBLFOOD",  "KOTAKBANK",  "L&TFH",  "LTTS",  "LICHSGFIN",  "LTIM",  "LT",  "LAURUSLABS",  "LICI",  "LUPIN",  "MRF",  
                "M&MFIN",  "M&M",  "MARICO",  "MARUTI",  "MFSL",  "MAXHEALTH",  "MSUMI",  "MPHASIS",  "MUTHOOTFIN",  "NHPC",  "NMDC",  
                "NTPC",  "NAVINFLUOR",  "NESTLEIND",  "OBEROIRLTY",  "ONGC",  "OIL",  "PAYTM",  "OFSS",  "POLICYBZR",  "PIIND",  
                "PAGEIND",  "PATANJALI",  "PERSISTENT",  "PETRONET",  "PIDILITIND",  "PEL",  "POLYCAB",  "POONAWALLA",  "PFC",  
                "POWERGRID",  "PRESTIGE",  "PGHH",  "PNB",  "RECLTD",  "RELIANCE",  "SBICARD",  "SBILIFE",  "SRF",  "MOTHERSON",  
                "SHREECEM",  "SHRIRAMFIN",  "SIEMENS",  "SONACOMS",  "SBIN",  "SAIL",  "SUNPHARMA",  "SUNTV",  "SYNGENE",  "TVSMOTOR",  
                "TATACHEM",  "TATACOMM",  "TCS",  "TATACONSUM",  "TATAELXSI",  "TATAMOTORS",  "TATAPOWER",  "TATASTEEL",  "TTML",  
                "TECHM",  "RAMCOCEM",  "TITAN",  "TORNTPHARM",  "TORNTPOWER",  "TRENT",  "TRIDENT",  "TIINDIA",  "UPL",  "ULTRACEMCO",  
                "UNIONBANK",  "UBL",  "MCDOWELL-N",  "VBL",  "VEDL",  "IDEA",  "VOLTAS",  "WHIRLPOOL",  "WIPRO",  "YESBANK",  "ZEEL",  
                "ZOMATO",  "ZYDUSLIFE"]

    # tickers = ["ABB",  "ACC",  "AUBANK",  "ABBOTINDIA",  "ADANIENT",  "ADANIGREEN",  "ADANIPORTS",  "ADANIPOWER",  "ATGL", 'INFY']
    # tickers = ["ADANIPORTS", 'INFY', 'TEST', 'SBIN'] # FOR DEBUG Only
    # tickers = ['GOLDM'] # FOR DEBUG Only

    # # for DEBUG only
    # obj = Trader(api, 'GOLDM', "long", 200)
    # obj.run()

    hist_data_tickers = hist_data(tickers)
    sorted_hist_data_tickers = {k:hist_data_tickers[k] for k in sorted(hist_data_tickers, key=lambda x: hist_data_tickers[x]['gain'].iloc[-1], reverse=True)}

    g_list = []
    l_list = []

    for ticker in list(sorted_hist_data_tickers)[0:5]:
    # for ticker in tickers: # FOR DEBUG Only
        obj = Trader(api, ticker, "long", sorted_hist_data_tickers[ticker]['high'].iloc[-1])
        # obj = Trader(api, ticker, "long", 0.0) # FOR DEBUG Only
        g_list.append(obj)

    for ticker in list(reversed(list(sorted_hist_data_tickers)))[0:5]:
    # for ticker in tickers: # FOR DEBUG Only
        obj = Trader(api, ticker, "short", sorted_hist_data_tickers[ticker]['low'].iloc[-1])
        # obj = Trader(api, ticker, "short", 9999.99) # FOR DEBUG Only
        l_list.append(obj)

    gvars.successfulOperation = True

    cur_time = dt.datetime.now().time()
    if(cur_time > gvars.waitTime and cur_time < gvars.startTime):
        lg.info("Market is NOT opened waiting ... !")
        time.sleep(gvars.sleepTime)

    while True:
        cur_time = dt.datetime.now().time()
        if(cur_time > gvars.startTime):
            break

        lg.info("Market is NOT opened waiting ... !")
        time.sleep(gvars.sleepTime)

    for i in g_list:
        i.start()

    for i in l_list:
        i.start()

    for i in g_list:
        i.join()

    for i in l_list:
        i.join()

    if not gvars.successfulOperation:
        lg.info('Trading was not successful, locking asset')
    else:
        lg.info('Trading was successful!')

    gen_report()
    lg.info('Trading Bot finished ... ')

    lg.info ("Exiting Main Thread")

if __name__ == '__main__':
    main()
