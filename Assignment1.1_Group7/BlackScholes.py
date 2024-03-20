"""
Name:   BlackScholes Class
Description:
Author:      YANG YIFAN
Created:     2023
"""
import numpy as np
import math
from scipy.stats import norm

class BlackScholes(object):
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
        d1 = (np.log(self.s / self.k) + (self.r + 0.5 * self.vol**2) * self.maturity) / (self.vol * np.sqrt(self.maturity))
        return d1

    def d2(self):
        d2 = (np.log(self.s / self.k) + (self.r - 0.5 * self.vol**2) * self.maturity) / (self.vol * np.sqrt(self.maturity))
        return d2

    def price(self):
        d1 = self.d1()
        d2 = self.d2()
        if self.is_call:
            price = self.s * norm.cdf(d1) - self.k * np.exp(-self.r * self.maturity) * norm.cdf(d2)
        else:
            price = self.k * np.exp(-self.r * self.maturity) * norm.cdf(-d2) - self.s * norm.cdf(-d1)
        return price

    def delta(self):
        d1 = self.d1()
        if self.is_call:
            delta = norm.cdf(d1)
        else:
            delta = -norm.cdf(-d1)
        return delta

    def gamma(self):
        d1 = self.d1()
        gamma = norm.pdf(d1) / (self.s * self.vol * np.sqrt(self.maturity))
        return gamma

    def theta(self):
        d1 = self.d1()
        d2 = self.d2()
        if self.is_call:
            theta = (-self.s * norm.pdf(d1) * self.vol) / (2 * np.sqrt(self.maturity)) - self.r * self.k * np.exp(-self.r * self.maturity) * norm.cdf(d2)
        else:
            theta = (-self.s * norm.pdf(d1) * self.vol) / (2 * np.sqrt(self.maturity)) + self.r * self.k * np.exp(-self.r * self.maturity) * norm.cdf(-d2)
        return theta

    def vega(self):
        d1 = self.d1()
        vega = norm.pdf(d1) * self.s * np.sqrt(self.maturity)
        return vega

