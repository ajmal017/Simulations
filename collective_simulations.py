"""
This script will launch simulations for different strategies
for different stocks/ETFs and will return an excel file
with their results in order to further analize them
"""
#===============================================================================
# LIBRARIES 
#===============================================================================
from pandas.io.data import DataReader
import numpy as np
import pandas as pd
import matplotlib as plt

import excel_management as excel

from strategy import Strategy 
from simulation import Simulation
from time import sleep

#===============================================================================
# CLASSES
#===============================================================================
class Collective_simulation():
    """
    This class will store the relevant information for a Collective Simulation
    and the functions that will operate it
    """
    def __init__(self, strategy, from_date='20000101', to_date='20140610'):
        # 1. Parameters
        self.strategy = strategy
        self.from_date = from_date
        self.to_date = to_date
        self.df_results = pd.DataFrame()
        
        # 2. Get Excel with Stocks to simulate
        self.filename = excel.select_excel_file()
        
        
        # 3. Save in Dataframe of the Stocks to simulate
        xl = pd.ExcelFile(self.filename)
        self.symbols = xl.parse('input')
        print self.symbols
        
    def process_simulations(self):
        """
        This function will iterate over all the symbols and simulate the 
        strategy.
        """
        n=0 # For sleeping and going on getting data from yahoo
        for row in self.symbols.iterrows():
            
            symbol = row[1]['symbol']
            print 'processing ' + str(symbol)
            sim = Simulation(symbol, from_date=self.from_date, to_date=self.to_date)
            sim.get_prices_yahoo()
            sim.apply_strategy(self.strategy)
            s_result = sim.get_result()
            if s_result.empty: continue  ## If it was not possible to make the simulation
            s_result = s_result.append(row[1])
            self.df_results = self.df_results.append(s_result, ignore_index=True)
            columns = ['symbol', 'name', 'category', 'subcategory', 'track index', 
                       'comments', 'commodity', 'sector', 'countries', 'assets',
                       'avg. vol', 'inverse', 'leveraged',
                       'from_date', 'to_date', 'nperiods', 'ntrades', 
                       'max_open', 'drawdown', 'abs_profit', 'pct_simple_profit',
                       'pct_compound_profit', 'annual_pct_simple_profit', 
                       'annual_pct_compound_profit', 'volatility', 'sharpe']
            self.df_results = self.df_results[columns]
        
            ## Time for not overuse Yahoo API
            n += 1
            if n == 350:
#                 sleep(10)
                n=0
                
    def save_result(self):
        """
        It will save the result in a new tab of the same excel file
        called Results
        """
        excel.save_in_new_tab_of_excel(self.filename, self.df_results, self.strategy.type)
        
        
#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    
    #===========================================================================
    # OLD TEST
    #===========================================================================
#     strategy = Strategy()
#     strategy.post_open_conditions(ndowns = 4)
#     strategy.post_close_conditions(nups = 1)
#     col = Collective_simulation(strategy)
#     col.process_simulations()
#     col.save_result()
    
    #===========================================================================
    # NDOWNS-NUPS
    #===========================================================================
    strategy = Strategy(type='ndowns-nups', ndowns=4, nups=1)
    col = Collective_simulation(strategy)
    col.process_simulations()
    col.save_result()
    
    #===========================================================================
    # PCTDOWN-NUPS
    #===========================================================================
    strategy = Strategy(type='pctdown-nups', pctdown=5.0, nups=1)
    col = Collective_simulation(strategy)
    col.process_simulations()
    col.save_result() 
    