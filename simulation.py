"""
This script will simulate a strategy of entering once a condition
has been met and exiting once another has been met and
will show a graph of the result and different measures
"""

#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt
from datetime import date 
from time import sleep 
import datetime

from strategy import Strategy 
from get_prices_from_IB import IB_API


#===============================================================================
# CLASSES
#===============================================================================
class Simulation():
    """
    Class that will store all data and functions related to a simulation
    """
    def __init__(self, symbol, from_date=None, to_date=None):
        """
        If dates not entered it will take a default to determine ######### TODO
        """
        
        ## 1. Common data
        self.data = False
        self.symbol = symbol
        self.from_date = from_date
        self.to_date = to_date
        self.df_prices = pd.DataFrame()
        self.open = None # Price of current open trade
        self.close = None # Price of current closed trade
        self.status = 'out' # 'out' not invested, 'in' invested
        self.signal = False  # It will get records in which the signal activates
        self.max_open = 0.0 # Max individual investment (for % profit calculation)
        ### Measures
        self.nperiods = 0
        self.ntrades = 0
        self.abs_profit = 0.0 # Accumulated abs_profit ($ value gained/loss)
        self.pct_compound_profit = 1.0 # Profit over max investment (with reinvestment)
        self.volatility = 0.0 # Volatility of returns (annualized)
        self.sharpe = 0.0 # Sharpe ratio (Rf = 0)
        self.drawdown = 0.0 # It will store the worst abs_profit
        self.df_result = pd.DataFrame()
        
        ## 2. Years calculation
        d_from_date = date(int(from_date[0:4]), int(from_date[4:6]), int(from_date[6:8]))
        d_to_date = date(int(to_date[0:4]), int(to_date[4:6]), int(to_date[6:8]))
        self.years = (d_to_date-d_from_date).days/365.0
        self.profit_trades = []
        
        
        ## 3. Get prices
        ### RNA 04/09/2014 Including prices download from IB, this function will be launch manually
        #self.get_prices_yahoo()
        ### END RNA 04/09/2014
        
    
    def apply_strategy(self, strategy):
        """
        It will apply the selected strategy to this simulation.
        Strategy in this case is a class with all the information it requires
        """
        # 0. In case there is no data, nothing is done
        if not self.data: return 0
        
        # 1. Initialization of variables
        count = 0
        status = 'out'
        s_record = pd.Series()
        pct_profit_temp = 0.0
        self.nperiods = len(self.df_prices.index)-1
        
        # 2. Loop through all the prices
        for pos in range(self.nperiods):
            
            currclose = self.df_prices.ix[pos]['Adj Close']
            change = self.df_prices.ix[pos]['pct Adj Close']
       
            # 3. Check if we are in or out
            if self.status == 'out':
                
                # 4. Check strategy entry condition
                if strategy.check_entry(self.df_prices, pos): ## If performance issue send less
                    self.open_trade(currclose)
                    
            elif self.status == 'in':
                
                # 5. Add profit for measures
                pct_profit_temp += change
                
                # 6. Check stratey exit condition
                if strategy.check_exit(self.df_prices, pos):
                    self.close_trade(currclose, pct_profit_temp)
                    pct_profit_temp = 0.0
            
            # 3. Log
            s_record["date"]=str(self.df_prices.index[pos])
            s_record["price"]=str(currclose)
            s_record["change"]=change
            s_record["status"]=self.status
            s_record["abs_profit"]=self.abs_profit
            s_record["signal"]=self.signal
            self.df_result = self.df_result.append(s_record, ignore_index=True)
            columns = ['date', 'price', 'change', 'status', 'abs_profit', 'signal']
            self.df_result = self.df_result[columns]
            
            prevclose = currclose
            self.signal = False
            
            
        # 3. Print result
#         print "The result is:" + str(self.abs_profit)
#         print "The log is:"
#         print df_result
        
    def close_trade(self, close, pct_profit_trade):
        self.close = close
        self.abs_profit += self.close - self.open 
        self.pct_compound_profit = np.sqrt((1+self.pct_compound_profit)*(1+pct_profit_trade)) - 1.0
        self.status = 'out'
        self.ntrades += 1
        self.profit_trades.append(pct_profit_trade)
        if self.abs_profit < self.drawdown:   # Calculation of drawdown
            self.drawdown = self.abs_profit     
        
        
    def get_prices_yahoo(self):
        """
        It get prices data from yahoo
        """
        try:
            self.df_prices = DataReader(self.symbol, "yahoo", self.from_date,
                                              self.to_date)
            self.df_prices['pct Adj Close'] = self.df_prices.pct_change()['Adj Close'] 
            self.data = True
        except Exception, e:
            print e
            sleep(20)
            
    
    def get_prices_IB(self):
        """
        It get prices data from Interactive Brokers
        """
        try:
            # Connection
            ib = IB_API()
    
            # Input data and call 
            contract_values = {
                       'm_symbol': self.symbol,
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
    
            self.df_prices = pd.DataFrame(ib.d_hist_data)
            self.df_prices = self.df_prices.T
            print self.df_prices.head()
        
        except Exception, e:
            print e
            sleep(20)
        
        
    
            
    def get_result(self):
        
        
        # 0. Serie which will store the result
        s_result = pd.Series()
        # 1. In case there is no data, nothing is done
        if not self.data: return s_result
        # 3. Else
        s_result['from_date'] = self.from_date
        s_result['to_date'] = self.to_date 
        s_result['nperiods'] = self.nperiods
        s_result['ntrades'] = self.ntrades 
        s_result['abs_profit'] = self.abs_profit 
        s_result['drawdown'] = self.drawdown
        s_result['max_open'] = self.max_open
        if self.max_open > 0: s_result['pct_simple_profit'] = self.abs_profit / self.max_open
        else: s_result['pct_simple_profit'] = 0.0 
        s_result['pct_compound_profit'] = self.pct_compound_profit
        s_result['annual_pct_simple_profit'] = (1+s_result['pct_simple_profit'])**(1/self.years)-1
        s_result['annual_pct_compound_profit'] = (1+s_result['pct_compound_profit'])**(1/self.years)-1
        s_result['volatility'] = np.std(self.profit_trades) * (1/self.years)**(1/2) # Annual volatility
        if s_result['volatility'] <> 0: s_result['sharpe'] = s_result['annual_pct_simple_profit'] / s_result['volatility']
        else: s_result['sharpe'] = np.nan 
        print s_result['sharpe']
        return s_result
        
    
        
                
            
    def open_trade(self, open):
        self.open = open
        if self.open > self.max_open:
            self.max_open = self.open 
        self.status = 'in'
        self.signal = True
        
    
        
        
    
    
    def save_result(self):
        # 0. In case there is no data, nothing is done
        if not self.data: return 0
        
        writer = pd.ExcelWriter("test_simulation.xlsx")
        self.df_result.to_excel(writer,"simulation")

#===============================================================================
# FUNCTIONS
#===============================================================================



#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    #===========================================================================
    # NDOWNS-NUPS
    #===========================================================================
#     strategy = Strategy(type='ndowns-nups')
#     strategy.post_open_conditions(ndowns = 4)
#     strategy.post_close_conditions(nups = 1)
#     sim = Simulation("SPY", from_date='20000101', to_date='20140612')
#     sim.apply_strategy(strategy)
#     s_result = sim.get_result()
#     print 'ndowns-nups: '
#     print s_result 
    
    
    #===========================================================================
    # PCTDOWN-NUPS - INTERDAY WITH YAHOO PRICES
    #===========================================================================
    strategy = Strategy(type='pctdown-nups', pctdown=5.0, nups=1)
    sim = Simulation("SPY", from_date='20000101', to_date='20140612')
    sim.get_prices_yahoo()
    sim.apply_strategy(strategy)
    s_result = sim.get_result()
    sim.save_result()
    print 'pctdown-nups: '
    print s_result
    
    #===========================================================================
    # PCTDOWN-NUPS - INTRADAY WITH IB PRICES
    #===========================================================================
    strategy = Strategy(type='pctdown-nups', pctdown=5.0, nups=1)
    sim = Simulation("AAPL", from_date='20000101', to_date='20140612')
    sim.get_prices_IB()
    sim.apply_strategy(strategy)
    s_result = sim.get_result()
    sim.save_result()
    print 'pctdown-nups: '
    print s_result
    
    
    
    
    
    