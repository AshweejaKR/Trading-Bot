# -*- coding: utf-8 -*-
"""
Created on Sat Sep  23 16:31:55 2023

@author: ashwe
"""

import logging as lg
import os, sys
from datetime import datetime
import gvars

class MyStreamHandler(lg.Handler):
    terminator = '\n'
    def __init__(self):
        lg.Handler.__init__(self)
        self.stream = sys.stdout
    def emit(self, record):
        if (record.levelno == lg.INFO or record.levelno == lg.WARNING or record.levelno == lg.ERROR):
            try:
                msg = self.format(record)
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except RecursionError:
                raise
            except Exception:
                self.handleError(record)

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
    gvars.filename = date + '_report.csv'
    log_name = date + '.log'
    currentLog_path = logs_path + log_name

    # log parameter
    lg.basicConfig(filename = currentLog_path, format = '%(asctime)s {%(pathname)s:%(lineno)d} [%(threadName)s] - %(levelname)s: %(message)s', level = lg.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

    # print the log in console
    console_formatter = lg.Formatter("%(asctime)s {%(pathname)s:%(lineno)d} [%(threadName)s] - %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = MyStreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # lg.getLogger().addHandler(lg.StreamHandler())
    lg.getLogger().addHandler(console_handler)

    # init message
    lg.info('Log initialized')
