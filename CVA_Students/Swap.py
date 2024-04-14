"""
Name:   Swap Class
Description:
Author:      YANG YIFAN
Created:     2020
"""

import CashFlow
import numpy as np
import pandas as pd
import math
import pdb

class swap(object):
    '''
    swap class
    Attributes
    ==========
    val_date : date
    tenor: string, like 6m 10y etc
    is_basis_swap: bool
    target_rate: double
    notional: double
    leg1: Leg
    leg2: Leg
    leg1_discount_curve: Curve
    leg1_forward_curve: Curve
    leg2_discount_curve: Curve
    leg2_forward_curve: Curve

    Methods
    =======
    compute_mtm() :
        compute mtm of swap
    compute_target_rate():
        compute implied target rate
    __compute_annuity() :
        return sum of df*year_frac
    __init__(val_date, tenor, leg1_freq, leg2_freq, is_basis_swap, target_rate, notional,
    leg1_discount_curve, leg1_forward_curve, leg2_discount_curve, leg2_forward_curve) :
        initiate swap
    '''

    def __init__(self, val_date, tenor, leg1_freq, leg2_freq, is_basis_swap=False, target_rate=0., notional=1.,
                 leg1_discount_curve=None, leg1_forward_curve=None, leg2_discount_curve=None, leg2_forward_curve=None):
        self.val_date = val_date
        self.tenor = tenor
        self.is_basis_swap = is_basis_swap
        self.target_rate = target_rate
        self.notional = notional
        self.leg1_discount_curve = leg1_discount_curve
        self.leg1_forward_curve = leg1_forward_curve
        self.leg2_discount_curve = leg2_discount_curve
        self.leg2_forward_curve = leg2_forward_curve
        '''
        generate cashflows for both legs
        '''
        leg1_cashflow_info = self.generate_cashflows(val_date, tenor, leg1_freq, notional, target_rate)
        leg2_cashflow_info = self.generate_cashflows(val_date, tenor, leg2_freq, notional)
        is_leg1_float = True
        if not is_basis_swap:
            is_leg1_float = False
        self.leg1 = CashFlow.leg(is_leg1_float, val_date, leg1_cashflow_info, leg1_discount_curve, leg1_forward_curve)
        self.leg2 = CashFlow.leg(True, val_date, leg2_cashflow_info, leg2_discount_curve, leg2_forward_curve)

    # private method to generate cashflowinfo
    # return DataFrame
    # leg_freq is in tenor format, in unit of month, e.g., '3M'
    def generate_cashflows(self, val_date, tenor, leg_freq, notional=1., target_rate=0.):
        tenor_unit = tenor[-1].upper()
        tenor_length = int(tenor[0:-1])
        freq_unit = leg_freq[-1].upper()
        if not freq_unit == 'M':
            raise ValueError('leg frequency mut be defined in month unit')
        freq_length = int(leg_freq[0:-1])

        ## generate period start dates and end dates, incomplete period up front (stub period)
        ## e.g., leg period freq 12m, trade tenor 18m, we have a stub period 6m, and a full period 12m
        start_dates = np.array([val_date])
        end_dates = np.array([val_date])
        if tenor_unit == 'Y':
            periods = math.ceil(tenor_length * 12 / freq_length)
            sub_period = tenor_length * 12 % freq_length
        else:
            periods = math.ceil(tenor_length / freq_length)
            sub_period = tenor_length % freq_length
        if sub_period != 0:
            sub_dates = CashFlow.month_range_day(val_date, 2, str(sub_period) + 'm')
            start_dates[0] = sub_dates[0]
            end_dates[0] = sub_dates[1]
            ## 1 stub period, 1 full period
            if periods == 2:
                start_dates = np.insert(start_dates, 1, sub_dates[1])
                end_dates = np.insert(end_dates, 1, CashFlow.month_range_day(sub_dates[1], 2, leg_freq)[-1])
            ## multiple full periods
            elif periods > 2:
                start_dates = CashFlow.month_range_day(sub_dates[1], periods - 1, leg_freq)
                end_dates = CashFlow.month_range_day(start_dates[1], periods - 1, leg_freq)
                start_dates = np.insert(start_dates, 0, sub_dates[0])
                end_dates = np.insert(end_dates, 0, sub_dates[1])
        else:
            start_dates = CashFlow.month_range_day(val_date, periods, leg_freq)
            if periods == 1:
                end_dates[0] = CashFlow.month_range_day(start_dates[0], 2, leg_freq)[-1]
            else:
                end_dates = CashFlow.month_range_day(start_dates[1], periods, leg_freq)
        cashflow_size = start_dates.shape[0]
        notionals = notional * np.ones(cashflow_size)
        margins = np.zeros(cashflow_size)
        rates = np.zeros(cashflow_size)
        if self.is_basis_swap:
            margins = target_rate * np.ones(cashflow_size)
        else:
            rates = target_rate * np.ones(cashflow_size)
        columns = ['start date', 'end date', 'notional', 'fixed rate', 'margin']
        cashflow_info = pd.DataFrame(columns=columns)
        cashflow_info['start date'] = start_dates
        cashflow_info['end date'] = end_dates
        cashflow_info['notional'] = notionals
        cashflow_info['fixed rate'] = rates
        cashflow_info['margin'] = margins
        return cashflow_info

    def compute_mtm(self):
        pv = self.leg1.compute_leg_pv()
        pv -= self.leg2.compute_leg_pv()
        return pv

    def compute_annuity(self):
        annuity = 0.
        cashflows = self.leg1.cashflows
        for cf in cashflows:
            year_frac = (cf.end_date - cf.start_date).days / 365.
            payment_date = (cf.end_date - self.val_date).days / 365.
            annuity += year_frac * self.leg1_discount_curve.get_discount_factor(payment_date) * cf.notional
        return annuity

    def update_cashflow_curves(self):
        for cf in self.leg1.cashflows:
            cf.discount_curve = self.leg1_discount_curve
            cf.forward_curve = self.leg1_forward_curve
        for cf in self.leg2.cashflows:
            cf.discount_curve = self.leg2_discount_curve
            cf.forward_curve = self.leg2_forward_curve

    # if it is fixed float swap, target is swap rate
    # if it is basis swap, target is the basis spread on leg1
    def compute_target_rate(self):
        if not self.is_basis_swap:
            return self.leg2.compute_leg_pv() / self.compute_annuity()
        else:
            exclude_margin_pv = self.leg1.compute_leg_pv(False)
            return (self.leg2.compute_leg_pv() - exclude_margin_pv) / self.compute_annuity()

    def get_maturity(self):
        end_date = self.leg1.cashflows[-1].end_date
        return (end_date - self.val_date).days / 365

    def set_simulation_date(self, simu_date):
        for cf in self.leg1.cashflows:
            cf.set_simulation_date(simu_date)
        for cf in self.leg2.cashflows:
            cf.set_simulation_date(simu_date)






