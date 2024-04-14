"""
Name:   Curve class
Description:
Author:      YANG YIFAN
Created:     2021
"""
import numpy as np
import Curve
import math

class simucurve(Curve.curve):
    '''
    simulation curve class, hull white model
    Attributes
    ==========
    name : string
    curve: curve
    hw_model: hull white model
    interp : scipy interp function

    Methods
    =======
    get_discount_factor(xval):
        return discount factor, for all simulation paths of current simulation time step
    get_forward_rate(start_date, end_date) :
        return forward rate, for all simulation paths of current simulation time step
    __init__(name, val_date, tenors) :
        initiate interest rate curve
    '''

    def __init__(self, curve, hw):
        self.name = curve.name
        self.val_date = curve.val_date
        self.curve = curve
        self.hw_model = hw

    def update(self, y_new):
        self.curve.update(y_new)

    def get_discount_factor(self, xval):
        if xval < self.hw_model.get_current_simu_date():
            raise ValueError('discount factor date can not before current model slice date')
        if abs(xval - self.hw_model.get_current_simu_date()) < 0.0001:
            return 1
        mr = self.hw_model.get_mean_reversion()
        vol = self.hw_model.get_vol()
        current_slice_date = self.hw_model.get_current_simu_date()
        prev_slice_date = self.hw_model.get_prev_simu_date()
        tau = xval - self.hw_model.get_current_simu_date()
        B = (1 - math.exp(-mr * tau)) / mr
        fwd = -(math.log(self.curve.get_discount_factor(current_slice_date))
                - math.log(self.curve.get_discount_factor(prev_slice_date))) / (current_slice_date - prev_slice_date)
        if current_slice_date == 0:
            fwd = self.hw_model.get_initial_short_rate()
        multiplier = self.curve.get_discount_factor(xval) / self.curve.get_discount_factor(current_slice_date)
        multiplier *= math.exp(B * fwd - vol**2 / (4*mr) *
                               (1 - math.exp(-2*mr*current_slice_date)) * B**2)
        return np.exp(-self.hw_model.get_short_rates() * B) * multiplier


    def get_forward_rate(self, start_date, end_date):
        if (start_date - self.val_date).days / 365. < self.hw_model.get_current_simu_date() or end_date <= start_date:
            raise ValueError('forward rate start date or end date is not valid')
        df_start = self.get_discount_factor((start_date - self.val_date).days/365)
        df_end = self.get_discount_factor((end_date - self.val_date).days/365)
        year_frac = (end_date - start_date).days/365
        return (df_start / df_end - 1) / year_frac

    def get_currency(self):
        return self.name[:3]

    def get_running_dfs(self):
        return self.hw_model.get_running_dfs()

    def get_short_rates(self):
        return self.hw_model.get_short_rates()

    def get_num_path(self):
        return self.hw_model.get_num_path()

    def move_to_next_slice(self):
        self.hw_model.move_to_next_slice()



