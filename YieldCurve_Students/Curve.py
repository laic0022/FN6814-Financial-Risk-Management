"""
Name:   Curve class
Description:
Author:      YANG YIFAN
Created:     2020
"""

from scipy.interpolate import interp1d
import math

class curve(object):
    '''
    interest rate curve class
    Attributes
    ==========
    name : string
    val_date : date
    x : numpy double, year frac
    y : numpy double, value
    interp : scipy interp function

    Methods
    =======
    update_curve(y_new) :
        update y value
    get_discount_factor(xval):
        return discount factor
    get_forward_rate(start_date, end_date) :
        return forward rate
    __init__(name, val_date, tenors) :
        initiate interest rate curve
    '''

    def __init__(self, name, val_date, x, y):
        self.name = name
        self.val_date = val_date
        self.x = x
        self.y = y
        self.interp = interp1d(x, y, bounds_error=False, fill_value=(y[0], y[-1]))

    def update(self, y_new):
        if self.y.shape[0] != y_new.shape[0]:
            raise ValueError('new discount factor size is not the same as the current curve')
        self.y = y_new
        self.interp = interp1d(self.x, self.y, bounds_error=False, fill_value=(y_new[0], y_new[-1]))

    def get_discount_factor(self, xval):
        return math.exp(-self.interp(xval) * xval)

    def get_forward_rate(self, start_date, end_date):
        if start_date < self.val_date or end_date <= start_date:
            raise ValueError('forward rate start date or end date is not valid')
        df_start = self.get_discount_factor((start_date - self.val_date).days/365)
        df_end = self.get_discount_factor((end_date - self.val_date).days/365)
        year_frac = (end_date - start_date).days/365
        return (df_start / df_end - 1) / year_frac

    def get_zero_rate(self, end_date):
        yf_end = (end_date - self.val_date).days / 365
        return self.interp(yf_end)

    def get_currency(self):
        return self.name[:3]






