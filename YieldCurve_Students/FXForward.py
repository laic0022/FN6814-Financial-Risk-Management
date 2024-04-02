"""
Name:   Future Class
Description:
Author:      YANG YIFAN
Created:     2021
"""

import dateutil.relativedelta as relativedelta
import math
import pandas as pd
import pdb

class fxforward(object):
    '''
    fxforward class
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
    compute_target_rate():
        compute implied target rate
    __init__(self, val_date, tenor, fx_spot, market_quote, dom_curve, for_curve,
                 for_notional=1., is_direct_quote=True):
        initiate fxforward, market quote is fx forward
    '''

    def __init__(self, val_date, tenor, fx_spot, market_quote, dom_curve=None, for_curve=None,
                 for_notional=1., is_direct_quote=True):
        self.val_date = val_date
        self.tenor = tenor
        self.fx_spot = fx_spot
        self.fx_forward = market_quote
        self.for_notional = for_notional
        self.dom_curve = dom_curve
        self.for_curve = for_curve
        self.is_direct_quote = is_direct_quote
        self.generate_maturity_date()

    def generate_maturity_date(self):
        tenor_unit = self.tenor[-1].upper()
        if not (tenor_unit == 'M'):
            raise ValueError('fx forward tenor is not defined in month unit')
        tenor_length = int(self.tenor[0:-1])
        self.maturity_date = self.val_date + relativedelta.relativedelta(months=tenor_length)

    def compute_target_rate(self):
        for_rate = self.for_curve.get_zero_rate(self.maturity_date)
        dom_rate = self.dom_curve.get_zero_rate(self.maturity_date)
        return dom_rate - for_rate

    def get_maturity(self):
        return (self.maturity_date - self.val_date).days / 365.

    def convert_marketquote_to_target(self):
        year_frac = (self.maturity_date - self.val_date).days / 365
        if self.is_direct_quote:
            return 1 / year_frac * math.log(self.fx_forward / self.fx_spot)
        else:
            return 1 / year_frac * math.log(self.fx_spot/ self.fx_forward)