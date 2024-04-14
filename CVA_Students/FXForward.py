"""
Name:   Future Class
Description:
Author:      YANG YIFAN
Created:     2021
"""

import dateutil.relativedelta as relativedelta
import math
import pandas as pd


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

    def __init__(self, val_date, tenor, strike, for_notional,
                 simu_fx_spot, dom_simu_curve, for_simu_curve):
        self.val_date = val_date
        self.tenor = tenor
        self.strike = strike
        self.simu_fx_spot = simu_fx_spot
        self.for_notional = for_notional
        self.dom_simu_curve = dom_simu_curve
        self.for_simu_curve = for_simu_curve
        self.generate_maturity_date()
        self.simulation_date = 0

    def generate_maturity_date(self):
        tenor_unit = self.tenor[-1].upper()
        tenor_length = int(self.tenor[0:-1])
        if tenor_unit.upper() == 'M':
            self.maturity_date = self.val_date + relativedelta.relativedelta(months=tenor_length)
        else:
            self.maturity_date = self.val_date + relativedelta.relativedelta(years=tenor_length)


    def get_maturity(self):
        return (self.maturity_date - self.val_date).days / 365.

    def set_simulation_date(self, simu_date):
        self.simulation_date = simu_date

    def compute_mtm(self):
        if self.get_maturity() <= self.simulation_date:
            return 0
        pv = self.simu_fx_spot.get_fx_spots() * self.for_simu_curve.get_discount_factor(self.get_maturity()) - \
             self.strike * self.dom_simu_curve.get_discount_factor(self.get_maturity())
        return pv