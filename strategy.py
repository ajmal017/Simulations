"""
The class strategy will contain the different parameters
and functions associated to a strategy
"""

#===============================================================================
# LIBRARIES
#===============================================================================



#===============================================================================
# CLASS
#===============================================================================
class Strategy():
    """ 
    Class that contains all parameters and functions associated to an strategy
    """
    def __init__(self, type=None, ndowns=None, nups=None, pctdown=None):
        """ 
        INIT PARAMETERS
        
        * Type:
            1. 'ndowns-nups': 
                    Entry: n periods down
                    Exit: n periods up
            
            2. 'pctdown-nups':
                    Entry: pct down (accumulative in periods)
                    Exit: n periods up
                    
        """
        self.type = type
        self.ndowns = ndowns
        self.nups = nups
        self.pctdown = pctdown
    
    def post_close_conditions(self, nups=None):
        """
        It will store close conditions:
            - nups: Number of days with close above last close
        """
        self.nups = nups
        
        
    def post_open_conditions(self, ndowns=None, pctdown=None):
        """
        It will store open conditions:
            - ndowns: Number of days with close below last close
        """
        self.ndowns = ndowns
        self.pctdown = pctdown
    
    def check_entry(self, df_to_check, pos):
        """
        Depending upon the strategy and data it will return True or False
        if the entry requirements are met
        """
        ## 1. Initialization of parameters
        count = 0
        cum_pct = 0.0
        ## 2. Different strategies
        if self.type == 'ndowns-nups':
            ## 3. Loop for the different periods
            for n in range(self.ndowns):
                if df_to_check.ix[pos-n]['pct Adj Close'] < 0:
                    count += 1
                else:
                    break
            ## 4. Return result
            if count == self.ndowns:
                return True
            else:
                return False
            
            
        elif self.type == 'pctdown-nups':
            ## 3. Loop for the different periods (all until getting the pctdown or exit
            for n in range(pos):
                if df_to_check.ix[pos-n]['pct Adj Close'] < 0:
                    cum_pct += df_to_check.ix[pos-n]['pct Adj Close']
                else:
                    break
            ## 4. Return result
            if cum_pct <= -self.pctdown/100:
                return True
            else:
                return False
    
    def check_exit(self, df_to_check, pos):
        """
        Depending upon the strategy and data it will return True or False
        if the exit requirements are met
        """
        ## 1. Initialization of parameters
        count = 0
        ## 2. Different strategies
        if self.type == 'ndowns-nups':
            ## 3. Loop for the different periods
            for n in range(self.nups):
                if df_to_check.ix[pos-n]['pct Adj Close'] > 0:
                    count += 1
                else:
                    break
            ## 4. Return result
            if count == self.nups:
                return True
            else:
                return False
            
            
        elif self.type == 'pctdown-nups':
            ## 3. Loop for the different periods
            for n in range(self.nups):
                if df_to_check.ix[pos-n]['pct Adj Close'] > 0:
                    count += 1
                else:
                    break
            ## 4. Return result
            if count == self.nups:
                return True
            else:
                return False
        





#===============================================================================
# MAIN
#===============================================================================
if __name__=='__main__':
    pass