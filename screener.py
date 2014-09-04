"""
This script will check if there are signals for different 
strategies in a group of securities
"""

#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt
import datetime as dt
from time import sleep

import excel_management as excel

from strategy import Strategy 


#===============================================================================
# CLASS: INDIVIDUAL SCREENER (Only 1 security)
#===============================================================================
class Individual_screener():
    """
    This class will store the relevant information and functions for the 
    signal detection of entry points of one Strategy in one Security
    """
    def __init__(self, symbol, to_date=dt.datetime.today()):
        self.data = False
        self.symbol = symbol
        self.to_date = to_date  
        self.from_date = self.to_date.replace(to_date.year - 1)
        self.signal = False
        
        self.get_prices_yahoo()
        
    def get_prices_yahoo(self):
        """
        It get prices data from yahoo (last year)
        """
        try:
            self.df_prices = DataReader(self.symbol, "yahoo", self.from_date,
                                              self.to_date)
            
            self.df_prices['pct Adj Close'] = self.df_prices.pct_change()['Adj Close'] 
            self.data = True
            
            
        except Exception, e:
            print e
            sleep(5)
            
    
    
    def check_signal(self, strategy):
        """"
        It will check if the conditions for this strategy are met in the specified
        date (by default the date in which is run) 
        """
        # 0. In case there is no data, nothing is done
        if not self.data: 
            self.signal = None
            return 0
        # 1. Check last returns to see how many downs in a row
        pos = len(self.df_prices.index)-1
        self.signal = strategy.check_entry(self.df_prices, pos)
        
        
        

#===============================================================================
# CLASS: COLLECTIVE SCREENER (List of securities)
#===============================================================================
class Collective_screener():
    """
    It will launch a collective checking of the signal of an strategy
    """
    def __init__(self, strategy, to_date=dt.datetime.today()):
        # 1. Parameters
        self.strategy = strategy
        self.to_date = to_date
        self.df_results = pd.DataFrame()
        
        # 2. Get Excel with Stocks to simulate
        self.filename = excel.select_excel_file()

        # 3. Save in Dataframe of the stocks to simulate
        xl = pd.ExcelFile(self.filename)
        self.symbols = xl.parse('input')
        
        # 4. Process Screeners
        self.process_screeners()
        
        # 5. Save the result
        self.save_result()
        
        
    def process_screeners(self):
        """
        This function will iterate over all the securities and check
        if a signal is triggered
        """
        s_result = pd.Series()
        for row in self.symbols.iterrows():
            symbol = row[1]['symbol']
            print 'processing: ' + str(symbol)
            ind_screener = Individual_screener(symbol)
            if ind_screener.data==False: continue # It was not possible to get data
            ind_screener.check_signal(self.strategy)
            s_result['symbol'] = symbol
            s_result['signal'] = ind_screener.signal
            self.df_results = self.df_results.append(s_result, ignore_index=True)

    def save_result(self):
        """
        It will save the result in a new tab of the same excel file
        called Signals
        """
        self.df_results = self.df_results[['symbol', 'signal']]
        excel.save_in_new_tab_of_excel(self.filename, self.df_results, 'Signals')
        
        





#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    
    #===========================================================================
    # 1st Strategy
    #===========================================================================
    strategy = Strategy(type='ndowns-nups', ndowns=4, nups=1)
    col = Collective_screener(strategy)
        

    #===========================================================================
    # 2nd Strategy
    #===========================================================================
    strategy = Strategy(type='pctdown-nups', pctdown=5.0, nups=1)
    col = Collective_screener(strategy)








