# -*- coding: utf-8 -*-
"""
Created on Sat Sep  23 16:31:55 2023

@author: ashwe
"""
import datetime as dt

exch_seg = 'NSE'

startTime = dt.time(9, 15)
endTime = dt.time(15, 00)
waitTime = dt.time(7, 00)

successfulOperation = True

takeProfitMargin = 0.01
stopLossMargin = 0.01

sleepTime = 20 # Delay

f_str = 'TIME\t\t\t\t\t TICKER\t\t\t\tOrder\t\t\t\tPRICE\t\t\t\t QTY\n'

# End here