# -*- coding: utf-8 -*-
"""
Created on Sat Sep  23 16:31:55 2023

@author: ashwe
"""

# import needed libraries
import threading
import gvars
from logger import *
from pya3 import *
import time, sys
import datetime as dt

class Trader(threading.Thread):
    def __init__(self, api, ticker, trend, trigger):
        # Initialize with ticker and api
        self.api = api
        self.ticker = ticker
        self.trend = trend
        self.trigger = float(trigger) * 1.00125
        self.thread_name = self.ticker + '_' + self.trend + '_at_' + str(self.trigger)
        threading.Thread.__init__(self, name=self.thread_name)
        lg.info('Trader initialized with ticker %s' % self.ticker)
        lg.info('Trend: %s, trigger price: %f' % (self.trend, self.trigger))

    def set_takeprofit(self, entryPrice):
        # takes a price as an input and sets the takeprofit
            # IN: entry price, trend (long/short)
            # OUT: take profit ($)

        try:
            if self.trend == 'long':
                # example: 10 + (10*0.1) = 11$
                takeProfit = entryPrice + (entryPrice * gvars.takeProfitMargin)
                lg.info('Take profit set for long at %.2f' % takeProfit)
                return takeProfit
            elif self.trend == 'short':
                # example: 10 - (10*0.1) = 9$
                takeProfit = entryPrice - (entryPrice * gvars.takeProfitMargin)
                lg.info('Take profit set for short at %.2f' % takeProfit)
                return takeProfit
            else:
                raise ValueError

        except Exception as err:
            lg.error('The trend value is not understood: %s' % str(self.trend))
            lg.error(str(err))
            sys.exit()

    def set_stoploss(self, entryPrice):
        # takes an entry price and sets the stoploss (trend)
            # IN: entry price, trend (long/short)
            # OUT: stop loss ($)

        try:
            if self.trend == 'long':
                # example: 10 - (10*0.05) = 9.5
                stopLoss = entryPrice - (entryPrice * gvars.stopLossMargin)
                lg.info('Stop loss set for long at %.2f' % stopLoss)
                return stopLoss
            elif self.trend == 'short':
                # example: 10 + (10*0.05) = 10.5
                stopLoss = entryPrice + (entryPrice * gvars.stopLossMargin)
                lg.info('Stop loss set for long at %.2f' % stopLoss)
                return stopLoss
            else:
                raise ValueError

        except Exception as err:
            lg.error('The trend value is not understood: %s' % str(self.trend))
            lg.error(str(err))
            sys.exit()
    
    def trail_SL(self):
        pass

    def get_current_price(self):
        # get the current price of an ticker with a position open
            # IN: ticker
            # OUT: price ($)

        currentPrice = 0.0
        # get current price
        try:
            instrument = self.api.get_instrument_by_symbol(gvars.exch_seg, self.ticker)
            ltp_data = self.api.get_scrip_info(instrument)
            currentPrice = float(ltp_data['Ltp'])
        except Exception as err:
            lg.error('Something went wrong at get current price')
            lg.error(str(err))

        return currentPrice

    def confirm_trend(self):
        # confirm trend: confirm the trend detected
            # IN: ticker, trend (long / short)
            # OUT: True (trend confirmed) / False (not a good moment to enter)

        lg.info('confirm Trend analysis entered for %s ' % self.ticker)
        instrument = self.api.get_instrument_by_symbol(gvars.exch_seg, self.ticker)
        ltp_data = self.api.get_scrip_info(instrument)
        currentPrice = float(ltp_data['Ltp'])

        lg.info('currentPrice for %s: %f ' % (self.ticker, currentPrice))

        try:
            if (self.trend == 'long') and (currentPrice > self.trigger):
                lg.info('Long trend confirmed for %s' % self.ticker)
                return True
            elif (self.trend == 'short') and (currentPrice < self.trigger):
                lg.info('Short trend confirmed for %s' % self.ticker)
                return True
            else:
                return False
        except Exception as err:
            lg.error('Something went wrong at confirm trend')
            lg.error(str(err))
            return False

    def submit_order(self, sharesQty, exit = False):
        # IN: order data (number of shares, order type)
        # OUT: boolean (True = order went through, False = order did not)

        lg.info('Submitting %s Order for %s' % (self.trend, self.ticker))
        ortype = None

        currentPrice = self.get_current_price()
        if self.trend == 'long' and not exit:
            side = TransactionType.Buy
            ortype = 'BUY'
            currentPrice = -currentPrice
            # limitPrice = round(currentPrice + currentPrice * gvars.maxVar, 2)
        elif self.trend == 'short' and not exit:
            side = TransactionType.Sell
            ortype = 'SELL'
            # limitPrice = round(currentPrice - currentPrice * gvars.maxVar, 2)
        elif self.trend == 'long' and exit:
            side = TransactionType.Sell
            ortype = 'SELL'
        elif self.trend == 'short' and exit:
            side = TransactionType.Buy
            ortype = 'BUY'
            currentPrice = -currentPrice
        else:
            lg.error('Trend was not understood')
            sys.exit()
        try:
            lg.info('Current price: %.2f' % currentPrice)
            order = self.api.place_order(transaction_type = side,
                instrument = self.api.get_instrument_by_symbol(gvars.exch_seg, self.ticker),
                quantity = sharesQty,
                order_type = OrderType.Market,
                product_type = ProductType.Intraday,
                price = 0.0,
                trigger_price = None,
                stop_loss = None,
                square_off = None,
                trailing_sl = None,
                is_amo = False,
                order_tag ='order1')

            lg.info('order response: %s' % order)
            status = 'NA'
            if(order['stat'] == 'Ok'):
                self.orderId = order['NOrdNo']
                lg.info('%s order submitted correctly!' % self.trend)
                lg.info('%d shares %s for %s' % (sharesQty, side, self.ticker))
                lg.info('order ID: %s' % self.orderId)

                status = self.get_oder_status(self.orderId)
                lg.info('order status: %s' % status)

            while (status == 'open'):
                lg.info('Still order in open')

            cur_time = dt.datetime.now().time()
            gvars.f_str = gvars.f_str + str(cur_time)[:-7] + '\t\t\t\t' + str(self.ticker) + '\t\t\t\t' + str(ortype) + '\t\t\t\t' + str(currentPrice) + '\t\t\t\t' + str(sharesQty) + '\n'
            if(status == 'complete'):
                lg.info('Order excecuted')
                return True
            else:
                lg.info('Order NOT excecuted')
                return False

        except Exception as err:
            lg.error('Something happend when submitting order')
            lg.error(str(err))
            sys.exit()

    def get_oder_status(self, orderID):

        status = 'NA'
        order_history_response = self.api.get_order_history('')

        # lg.info('order_history_response: ', order_history_response)

        for i in order_history_response:
            try:
                if(i['Nstordno'] == orderID):
                    status = i['Status'] # complete/rejected/open/cancelled
                    break
            except Exception as err:
                lg.error('Something happend in get order status')
                lg.error(str(err))

        return status


    def get_oder_status_by_ticker(self):

        status = 'NA'
        order_history_response = self.api.get_order_history('')

        for i in order_history_response:
            try:
                if(i['Sym'] == self.ticker):
                    status = i['Status'] # complete/rejected/open
                    break
            except Exception as err:
                lg.error(str(err))

        return status

    def enter_position_mode(self):
        # check the conditions in parallel once inside the position
        # depending on the trend
            # IN: ticker, trend
            # OUT: True if Success / False if Fail/Time out

        # get average entry price
        entryPrice = self.get_current_price()

        # set the take profit
        takeProfit = self.set_takeprofit(entryPrice)

        # set the stop loss
        stopLoss = self.set_stoploss(entryPrice)

        while True:
            try:
                time.sleep(gvars.sleepTime)
                currentPrice = self.get_current_price()
                lg.info('Waiting inside %s position for %s ... ' % (self.trend, self.ticker))
                lg.info('SL %.2f <-- %.2f --> %.2f TP' % (stopLoss, currentPrice, takeProfit))

                if self.trend == 'long':
                    if((currentPrice < stopLoss) or (currentPrice > takeProfit)):
                        lg.info('Exiting the %s position for %s. Current price is %.2f' % (self.trend, self.trend, currentPrice))
                        return True

                elif self.trend == 'short':
                    if((currentPrice > stopLoss) or (currentPrice < takeProfit)):
                        lg.info('Exiting the %s position for %s. Current price is %.2f' % (self.trend, self.trend, currentPrice))
                        return True

                cur_time = dt.datetime.now().time()
                if(cur_time < gvars.startTime or cur_time > gvars.endTime):
                    lg.info('Timeout reached at enter position, for %s' % self.ticker)
                    break
            except Exception as err:
                lg.error('Something happend at enter position function')
                lg.error(str(err))
                return False
        
        return True

    def run(self):
        # check the trends in parallel once confirm tred enter position mode
        # depending on the trend take tarde
        # IN: None
        # OUT: True if Success / False if Fail/Time out

        #POINT DELTA: LOOP until timeout reached (ex. 2h)
        while True:
            lg.info('Running %s trade for %s' % (self.trend, self.ticker))
            time.sleep(gvars.sleepTime)

            cur_time = dt.datetime.now().time()
            if(cur_time < gvars.startTime or cur_time > gvars.endTime):
                break

            # confirm instant trend
            if not self.confirm_trend():
                lg.info('Trend is not confirmed. Going back.')
                continue # If failed go back to POINT DELTA

            lg.info('All filtering passed, carrying on with the order!')
            break # get out of the loop

        # decide the total amount to invest
        sharesQty = 1#self.get_shares_amount(currentPrice)

        # submit order (limit)
        success = self.submit_order(sharesQty)
        print('ENTER: ', success)

        # if(success):
        lg.info('%s Position ENTER for %s!' % (self.trend, self.ticker))

        ### Skiping these steps for now
        # # check position
        # if not self.check_position():
        #     self.cancel_pending_order()
        #     continue # go back to POINT ECHO

        # enter position mode
        successfulOperation = self.enter_position_mode()

        #GET OUT
        success = self.submit_order(sharesQty, exit = True)
        print('EXIT: ', success)

        lg.info('%s Position EXIT for %s!' % (self.trend, self.ticker))

        ### Skiping these steps for now
        # while True:
        #     # check the position is cleared
        #     if not self.check_position(self.ticker, doNotFind = True):
        #         break # GET OUT OF THE MAIN WHILE

        #     lg.info('\nWARNING! THE POSITION SHOULD BE CLOSED! Retrying...')
        #     time.sleep(gvars.sleepTimeCP) # wait 10 seconds

        # end of execution
        gvars.successfulOperation = gvars.successfulOperation & successfulOperation
        lg.info('\n%s: Trade is completed ...!!' % (self.ticker))
        time.sleep(gvars.sleepTime)