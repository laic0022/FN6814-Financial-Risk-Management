import numpy as np
import pandas as pd
import math
import CashFlow

class XccySwap(object):
    def __init__(self, val_date, tenor, leg1_freq, leg2_freq, is_basis_swap, target_rate, 
                 notional_dom, notional_for, leg1_discount_curve, leg1_forward_curve, 
                 leg2_discount_curve, leg2_forward_curve, fx_spot, is_notional_exchange, is_MTM):
        self.val_date = val_date
        self.tenor = tenor
        self.leg1_freq = leg1_freq
        self.leg2_freq = leg2_freq
        self.is_basis_swap = is_basis_swap
        self.target_rate = target_rate
        self.notional_dom = notional_dom
        self.notional_for = notional_for
        self.leg1_discount_curve = leg1_discount_curve
        self.leg1_forward_curve = leg1_forward_curve
        self.leg2_discount_curve = leg2_discount_curve
        self.leg2_forward_curve = leg2_forward_curve
        self.fx_spot = fx_spot
        self.is_notional_exchange = is_notional_exchange
        self.is_MTM = is_MTM
    
    def leg1_cashflow(self):
        tenor_unit = self.tenor[-1].upper()
        tenor_length = int(self.tenor[0:-1])
        freq_unit = self.leg1_freq[-1].upper()
        if not freq_unit == 'M':
            raise ValueError('leg frequency mut be defined in month unit')
        freq_length = int(self.leg1_freq[0:-1])
        start_dates = np.array([self.val_date])
        end_dates = np.array([self.val_date])
        if tenor_unit == 'Y':
            periods = math.ceil(tenor_length * 12 / freq_length)
            sub_period = tenor_length * 12 % freq_length
        else:
            periods = math.ceil(tenor_length / freq_length)
            sub_period = tenor_length % freq_length
        if sub_period != 0:
            sub_dates = CashFlow.month_range_day(self.val_date, 2, str(sub_period) + 'm')
            start_dates[0] = sub_dates[0]
            end_dates[0] = sub_dates[1]
            ## 1 stub period, 1 full period
            if periods == 2:
                start_dates = np.insert(start_dates, 1, sub_dates[1])
                end_dates = np.insert(end_dates, 1, CashFlow.month_range_day(sub_dates[1], 2, self.leg1_freq)[-1])
            ## multiple full periods
            elif periods > 2:
                start_dates = CashFlow.month_range_day(sub_dates[1], periods - 1, self.leg1_freq)
                end_dates = CashFlow.month_range_day(start_dates[1], periods - 1, self.leg1_freq)
                start_dates = np.insert(start_dates, 0, sub_dates[0])
                end_dates = np.insert(end_dates, 0, sub_dates[1])
        else:
            start_dates = CashFlow.month_range_day(self.val_date, periods, self.leg1_freq)
            if periods == 1:
                end_dates[0] = CashFlow.month_range_day(start_dates[0], 2, self.leg1_freq)[-1]
            else:
                end_dates = CashFlow.month_range_day(start_dates[1], periods, self.leg1_freq)

        cashflow_df = pd.DataFrame()
        cashflow_df['start dates'] = start_dates
        cashflow_df['end dates'] = end_dates

        maturity = [i.days / 365 for i in (cashflow_df['end dates'] - self.val_date)]
        daycount = [i.days / 365 for i in (cashflow_df['end dates'] - cashflow_df['start dates'])]
        cashflow_df['discount factor'] = [self.leg1_discount_curve.get_discount_factor(i) for i in maturity]
        cashflow_df['rate fixing date'] = start_dates
        cashflow_df['day count'] = daycount
        
        libor = []
        for i, row in cashflow_df.iterrows():
            libor.append(self.leg1_forward_curve.get_forward_rate(row['start dates'], row['end dates']))
        cashflow_df[self.leg1_freq + ' Libor'] = libor
        cashflow_df['margin'] = -0.002
        cashflow_df['notional'] = self.notional_dom
        cashflow_df['coupon pv'] = -cashflow_df['notional'] * (cashflow_df[self.leg1_freq + ' Libor'] + cashflow_df['margin']) * cashflow_df['discount factor'] * cashflow_df['day count']
        
        return cashflow_df
    def leg2_cashflow(self):
        tenor_unit = self.tenor[-1].upper()
        tenor_length = int(self.tenor[0:-1])
        freq_unit = self.leg2_freq[-1].upper()
        if not freq_unit == 'M':
            raise ValueError('leg frequency mut be defined in month unit')
        freq_length = int(self.leg2_freq[0:-1])
        start_dates = np.array([self.val_date])
        end_dates = np.array([self.val_date])
        if tenor_unit == 'Y':
            periods = math.ceil(tenor_length * 12 / freq_length)
            sub_period = tenor_length * 12 % freq_length
        else:
            periods = math.ceil(tenor_length / freq_length)
            sub_period = tenor_length % freq_length
        if sub_period != 0:
            sub_dates = CashFlow.month_range_day(self.val_date, 2, str(sub_period) + 'm')
            start_dates[0] = sub_dates[0]
            end_dates[0] = sub_dates[1]
            ## 1 stub period, 1 full period
            if periods == 2:
                start_dates = np.insert(start_dates, 1, sub_dates[1])
                end_dates = np.insert(end_dates, 1, CashFlow.month_range_day(sub_dates[1], 2, self.leg2_freq)[-1])
            ## multiple full periods
            elif periods > 2:
                start_dates = CashFlow.month_range_day(sub_dates[1], periods - 1, self.leg2_freq)
                end_dates = CashFlow.month_range_day(start_dates[1], periods - 1, self.leg2_freq)
                start_dates = np.insert(start_dates, 0, sub_dates[0])
                end_dates = np.insert(end_dates, 0, sub_dates[1])
        else:
            start_dates = CashFlow.month_range_day(self.val_date, periods, self.leg2_freq)
            if periods == 1:
                end_dates[0] = CashFlow.month_range_day(start_dates[0], 2, self.leg2_freq)[-1]
            else:
                end_dates = CashFlow.month_range_day(start_dates[1], periods, self.leg2_freq)

        cashflow_df = pd.DataFrame()
        cashflow_df['start dates'] = start_dates
        cashflow_df['end dates'] = end_dates

        maturity = [i.days / 365 for i in (cashflow_df['end dates'] - self.val_date)]
        daycount = [i.days / 365 for i in (cashflow_df['end dates'] - cashflow_df['start dates'])]
        cashflow_df['discount factor'] = [self.leg2_discount_curve.get_discount_factor(i) for i in maturity]
        cashflow_df['fx fixing date'] = start_dates
        cashflow_df['day count'] = daycount
        
        libor = []
        rl = []
        rf = []
        for i, row in cashflow_df.iterrows():
            libor.append(self.leg2_forward_curve.get_forward_rate(row['start dates'], row['end dates']))
            
            rl.append(self.leg1_discount_curve.get_zero_rate(row['end dates']))
            rf.append(self.leg2_discount_curve.get_zero_rate(row['end dates']))
            
        rl = np.array(rl)
        rf = np.array(rf)
        cashflow_df[self.leg1_freq + ' Libor'] = libor
        
        t = [(i - self.val_date).days / 365 for i in cashflow_df['fx fixing date']]
        cashflow_df['fx fwd'] = self.fx_spot * np.exp((rl - rf) * t)
        cashflow_df['notional'] = self.notional_dom / cashflow_df['fx fwd']
        cashflow_df['mtm notional'] = (cashflow_df['notional'].shift(1) - cashflow_df['notional']) * cashflow_df['discount factor'].shift(1)
        cashflow_df['coupon'] = cashflow_df['notional'] * (cashflow_df[self.leg2_freq + ' Libor']) * cashflow_df['discount factor'] * cashflow_df['day count']
        
        return cashflow_df
    
    def compute_mtm(self):
        leg1_cashflow = self.leg1_cashflow()
        leg2_cashflow = self.leg2_cashflow()
        
        leg1_coupon = leg1_cashflow['coupon pv'].sum()
        leg1_notional = self.notional_dom - self.notional_dom * leg1_cashflow['discount factor'].iloc[-1]
        leg2_mtm = leg2_cashflow['mtm notional'].sum()
        leg2_coupon = leg2_cashflow['coupon'].sum()
        leg2_notional = -self.notional_for + leg2_cashflow['notional'].iloc[-1] * leg2_cashflow['discount factor'].iloc[-1]
        
        return leg1_coupon + leg1_notional + self.fx_spot * (leg2_mtm + leg2_coupon + leg2_notional)
    
    def compute_annuity(self):
        annuity = 0.
        cashflows = self.leg1_cashflow()
        for index, cf in cashflows.iterrows():
            year_frac = (cf['end dates'] - cf['start dates']).days / 365.
            payment_date = (cf['end dates'] - self.val_date).days / 365.
            annuity += year_frac * self.leg1_discount_curve.get_discount_factor(payment_date) * cf.notional
        return annuity 
    
    
    def compute_target_rate(self):
        leg1_cashflow = self.leg1_cashflow()
        leg2_cashflow = self.leg2_cashflow()
        if not self.is_basis_swap:
            return leg2_cashflow['coupon'].sum() / self.compute_annuity() * self.fx_spot
        else:
            return (leg2_cashflow['coupon'].sum() - leg1_cashflow['coupon pv'].sum() / self.fx_spot) / self.compute_annuity() * self.fx_spot