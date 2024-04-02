"""
Name:   Future Class
Description:
Author:      YANG YIFAN
Created:     2020
"""

import dateutil.relativedelta as relativedelta
import pandas as pd
import pdb

class future(object):
    '''
    future class
    Attributes
    ==========
    val_date : date
    start_tenor : start date tenor
    index_tenor : future index ternor, e.g., 3M
    is_fedfuture: bool
    target_rate: double
    notional: double
    discount_curve: Curve
    forward_curve: Curve

    Methods
    =======
    compute_mtm() :
        compute mtm of future
    compute_target_rate():
        compute implied target rate
    __init__(val_date, tenor, leg1_freq, leg2_freq, is_basis_swap, target_rate, notional,
    leg1_discount_curve, leg1_forward_curve, leg2_discount_curve, leg2_forward_curve) :
        initiate swap
    '''

    def __init__(self, val_date, start_tenor, future_tenor, is_fedfuture=False, future_quote=100., notional=1.,
                 discount_curve=None, forward_curve=None):
        self.val_date = val_date
        self.start_tenor = start_tenor
        self.future_tenor = future_tenor
        self.is_fedfuture = is_fedfuture
        self.target_rate = 0.01 * (100 - future_quote)
        self.notional = notional
        self.discount_curve = discount_curve
        self.forward_curve = forward_curve
        self.generate_future_dates()

    def generate_future_dates(self):
        if self.start_tenor.upper() == 'SPOT':
            self.start_tenor = '0M'
        start_tenor_unit = self.start_tenor[-1].upper()
        if not (start_tenor_unit == 'M'):
            raise ValueError('future start date tenor is not defined in month unit')
        start_tenor_length = int(self.start_tenor[0:-1])
        future_unit = self.future_tenor[-1].upper()
        if not future_unit == 'M':
            raise ValueError('future index mut be defined in month unit')
        future_length = int(self.future_tenor[0:-1])
        self.start_date = self.val_date + relativedelta.relativedelta(months=start_tenor_length)
        self.end_date = self.start_date + relativedelta.relativedelta(months=future_length)

    def compute_target_rate(self):
        if not self.is_fedfuture:
            return self.forward_curve.get_forward_rate(self.start_date, self.end_date)
        current_date = self.start_date
        next_day = current_date + relativedelta.relativedelta(days=1)
        rate = 0.
        number_of_days = 1
        while next_day <= self.end_date:
            rate += self.forward_curve.get_forward_rate(current_date, next_day)
            current_date = next_day
            number_of_days += 1
            next_day = next_day + relativedelta.relativedelta(days=1)
        rate = rate / number_of_days
        return rate

    def get_maturity(self):
        return (self.end_date - self.val_date).days / 365.




