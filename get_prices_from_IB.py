"""
This script will access the IB API and download price data
"""

#===============================================================================
# LIBRARIES
#===============================================================================
from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
import quantacademy.excel_management as excel
import pandas as pd
from time import sleep, strftime
import datetime
from collections import defaultdict

#===============================================================================
# Class IB_API
#===============================================================================
class IB_API:
    """
    This class will establish a connection to IB and group the different 
    operations
    """
    
    # Variables
    d_ticker_reqId = {}
    reqId = 1
    d_opt_contracts = defaultdict(dict)
    d_contracts = {}
    d_hist_data = {}
    
    # Functions
    def __init__(self):
        """
        Connection to the IB API
        """
        print "Calling connection"
        # Creation of Connection class
        self.connection = ibConnection()
        # Register data handlers
        self.connection.registerAll(self.process_messages)
        # Connect
        self.connection.connect()
        
    def process_messages(self, msg):
        """
        Function that indicates how to process each different message
        """
        if msg.typeName == "contractDetails":
            print msg
            opt_contract = msg.values()[1]
            self.save_option_contracts_to_dict(opt_contract)
        elif msg.typeName == "historicalData":
            self.save_historical_data_to_dict(msg)
                
        else:
            print msg
    
    
    def get_historical_data(self, reqId, contract_values, endDateTime, durationStr,
                            barSizeSetting, whatToShow = 'TRADES'):
        """
        Call for the historial data of the contract passed as argument
        """
        print "Calling Historial Data"
        # Contract creation
        contract = Contract()
        contract.m_symbol = contract_values['m_symbol']
        contract.m_exchange = contract_values['m_exchange']
        contract.m_currency = contract_values['m_currency']
        contract.m_secType = contract_values['m_secType']
        # Call Historical Data
        self.connection.reqHistoricalData(
                                          tickerId = reqId,
                                          contract = contract,
                                          endDateTime = endDateTime,
                                          durationStr = durationStr,
                                          barSizeSetting = barSizeSetting,
                                          whatToShow = whatToShow,
                                          useRTH = 1,    # Only regular hours
                                          formatDate = 1 # format: yyyymmdd  hh:mm:dd 
                                         )
        sleep(20)
    
    
    def save_historical_data_to_dict(self, hist_data):
        time = hist_data.values()[1]
        keys = ['open', 'high', 'low', 'close', 'volume', 'count', 'WAP', 'hasGAPS']
        values = hist_data.values()[2:9]
        self.d_hist_data[time] = dict(zip(keys,values))
        
    
    
    
    
 
if __name__ == '__main__':
    # Connection
    ib = IB_API()
    
    # Input data and call 
    contract_values = {
                       'm_symbol': 'AAPL',
                       'm_exchange': 'SMART',
                       'm_secType': 'STK',
                       'm_currency': 'USD'
                       }
    now = datetime.datetime.now()
    endDateTime = now.strftime('%Y%m%d %H:%M:%S')
    durationStr = '1 W'
    barSizeSetting = '5 mins'
    ib.get_historical_data(1, contract_values, endDateTime = endDateTime, 
                           durationStr = durationStr, barSizeSetting = barSizeSetting)
    
    
    print ib.d_hist_data
    #sleep(10000)
    
    
    
    
    
    
    
    ############################################################
    
    
    

 
 
 
 
 
 
 
 