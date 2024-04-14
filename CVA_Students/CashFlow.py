"""
Name:   Cashflow, leg class
Description:
Author:      YANG YIFAN
Created:     2020
"""

import pandas as pd
import Curve

def month_range_day(start=None, periods=None, month_freq='1M'):
    start_date = pd.Timestamp(start).date()
    month_range = pd.date_range(start=start_date, periods=periods, freq=month_freq)
    month_day = month_range.day.values
    month_day[start_date.day < month_day] = start_date.day
    timestamps = pd.to_datetime(month_range.year*10000+month_range.month*100+month_day, format='%Y%m%d')
    return timestamps.to_pydatetime()

class CashFlow(object):
    '''
    cashflow class
    Attributes
    ==========
    name : string
    is_float : bool
    val_date : valuation date
    start_date : cashflow start date
    end_date : cashflow end date
    rate: double
    notional : double
    currency: string
    discount_curve: curve
    forward_curve: curve

    Methods
    =======
    compute_cashflow() :
        compute cashflow at payment date
    compute_cashflow_pv() :
        compute cashflow, discount to valuation date
    __init__(name, is_float, val_date, start_date, end_date, notional, rate, currency, discount_curve, forward_curve) :
        initiate cashflow object
    '''

    def __init__(self, val_date, start_date, end_date, is_float=False, notional=1., rate=0., margin=0.,
                 currency='USD', discount_curve=None, forward_curve=None):
        self.val_date = val_date
        self.start_date = start_date
        self.end_date = end_date
        self.notional = notional
        self.rate = rate
        self.margin = margin
        self.currency = currency
        self.is_float = is_float
        self.discount_curve = discount_curve
        self.forward_curve = forward_curve

    def compute_cashflow(self, include_margin=True):
        '''
        :return:
         cashflow at payment date
        '''
        if self.is_float:
            self.rate = self.forward_curve.get_forward_rate(self.start_date, self.end_date)
        year_frac = (self.end_date - self.start_date).days / 365.
        if include_margin:
            return self.notional * (self.rate + self.margin) * year_frac
        else:
            return self.notional * self.rate * year_frac

    def compute_cashflow_pv(self, include_margin=True):
        '''
        :return:
         cashflow discount to valuation date
        '''
        if (self.end_date - self.val_date).days/365. <= self.simulation_date:
            return 0
        payment_day = (self.end_date - self.val_date).days / 365.
        df = self.discount_curve.get_discount_factor(payment_day)
        return self.compute_cashflow(include_margin) * df

    def set_simulation_date(self, simu_date):
        self.simulation_date = simu_date

class leg(object):
    '''
    leg class, a holder of cashflows

    '''
    def __init__(self, is_float, val_date, cashflows_info, discount_curve=None, forward_curve=None):
        self.is_float = is_float
        self.val_date = val_date
        if not isinstance(cashflows_info, pd.DataFrame):
            raise ValueError('cashflows info are not initialized in dataframe')
        cashflows = []
        for index, row in cashflows_info.iterrows():
            start_date = row['start date']
            end_date = row['end date']
            notional = row['notional']
            rate = row['fixed rate']
            margin = row['margin']
            cashflows.append(CashFlow(val_date, start_date, end_date, is_float, notional, rate, margin,
                                      discount_curve=discount_curve, forward_curve=forward_curve))
        self.cashflows = cashflows

    def compute_leg_pv(self, include_margin=True):
        pv = 0.
        for cf in self.cashflows:
            if include_margin:
                pv += cf.compute_cashflow_pv()
            else:
                pv += cf.compute_cashflow_pv(False)
        return pv

    def is_float_leg(self):
        return self.is_float
