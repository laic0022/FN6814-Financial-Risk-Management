"""
Name:   FRA Class
Description:
Author:      YANG YIFAN
Created:     2021
"""

import dateutil.relativedelta as relativedelta

class fra(object):
    '''
    future class
    Attributes
    ==========
    val_date : date
    start_tenor : start date tenor
    index_tenor : future index ternor, e.g., 3M
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
    '''

    def __init__(self, val_date, start_tenor, end_tenor, target_rate, notional=1.,
                 discount_curve=None, forward_curve=None):
        self.val_date = val_date
        self.start_tenor = start_tenor
        self.end_tenor = end_tenor
        self.target_rate = target_rate
        self.notional = notional
        self.discount_curve = discount_curve
        self.forward_curve = forward_curve
        self.generate_fra_dates()

    def generate_fra_dates(self):
        if self.start_tenor.upper() == 'SPOT':
            self.start_tenor = '0M'
        start_tenor_unit = self.start_tenor[-1].upper()
        if not (start_tenor_unit == 'M'):
            raise ValueError('future start date tenor is not defined in month unit')
        start_tenor_length = int(self.start_tenor[0:-1])
        fra_unit = self.end_tenor[-1].upper()
        if not fra_unit == 'M':
            raise ValueError('fra index mut be defined in month unit')
        fra_length = int(self.end_tenor[0:-1])
        if start_tenor_length == 0:
            self.start_date = self.val_date
        else:
            self.start_date = self.val_date + relativedelta.relativedelta(months=start_tenor_length)
        self.end_date = self.start_date + relativedelta.relativedelta(months=fra_length)

    def compute_target_rate(self):
        return self.forward_curve.get_forward_rate(self.start_date, self.end_date)

    def get_maturity(self):
        return (self.end_date - self.val_date).days / 365.





