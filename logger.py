# -*- coding: utf-8 -*-
"""
Created on Sat Sep  23 16:31:55 2023

@author: ashwe
"""

import logging as lg
import os
from datetime import datetime

def initialize_logger():
    # creating s folder for the log
    logs_path = './logs/'
    try:
        os.mkdir(logs_path)
    except OSError:
        print('Creation of the directory %s failed - it does not have to be bad' % logs_path)
    else:
        print('Succesfully created log directory')

    # renaming each log depending on time Creation
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    # date = "debug_20012023"
    log_name = date + '.log'
    currentLog_path = logs_path + log_name

    # log parameter
    # lg.basicConfig(filename = currentLog_path, format = '%(asctime)s {%(pathname)s:%(lineno)d} - %(levelname)s: %(message)s', level = lg.DEBUG)
    lg.basicConfig(filename = currentLog_path, format = '%(asctime)s {%(pathname)s:%(lineno)d} [%(threadName)s] - %(levelname)s: %(message)s', level = lg.DEBUG)

    # print the log in console
    lg.getLogger().addHandler(lg.StreamHandler())

    # init message
    lg.info('Log initialized')
