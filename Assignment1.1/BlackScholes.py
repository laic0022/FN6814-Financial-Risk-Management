# """
# Name:   BlackScholes Class
# Description:
# Author:      YANG YIFAN
# Created:     2023
# """

# import math
import numpy as np
# from scipy.stats import norm

class BlackScholes:
    '''
    interest rate curve class
    Attributes
    ==========
    r : double, interest rate
    s : numpy array, stock price
    k : double, strike
    vol : double, const vol
    maturity : double, option maturity in year fraction
    is_call: bool, call or put

    Methods
    =======
    d1():
        d1 in bs formula
    d2():
        d2 in bs formula
    price():
        option price
    delta():
        bs delta
    gamma():
        bs gamma
    theta():
        bs theta
    vega():
        bs vega
    '''

    def __init__(self, s, k, vol, r, maturity, is_call = True):
        if not isinstance(s, np.ndarray):
            self.s = np.array([s])
        else:
            self.s = s
        self.k = k
        self.vol = vol
        self.r = r
        if maturity <= 0:
            raise ValueError('maturity must be greater 0')
        self.maturity = maturity
        self.is_call = is_call
    def d1(self):
        return (np.log(self.s/self.k)+(self.r+0.5*self.vol**2)*self.maturity)/(self.vol*np.sqrt(self.maturity))

    def d2(self):
        return (np.log(self.s/self.k)+(self.r-0.5*self.vol**2)*self.maturity)/(self.vol*np.sqrt(self.maturity))