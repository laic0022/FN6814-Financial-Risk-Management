"""
Name:   Hull White Class
Description:
Author:      YANG YIFAN
Created:     2021
"""
import numpy as np
import math

class HullWhite(object):
    '''
    interest rate curve class
    Attributes
    ==========
    ccy : string
    val_date : date
    mr : double, mean reversion
    vol : double, const vol
    num_path : int, the number of simulation paths
    simu_dates: double vector, simulate dates in year frac
    current_slice: int, current simulation date index count

    Methods
    =======
    evolve():
        evolve model, simulate short rates for next slice date
        current_slice will increase
    get_hw_discount_factor(path):
        return hw discount factor for the current path and current slice date
    '''

    def __init__(self, val_date, mr, vol, num_path, simu_dates_dfc, initial_short_rate):
        self.val_date = val_date
        self.mr = mr
        self.vol = vol
        self.num_path = num_path
        self.simu_dates = simu_dates_dfc
        self.current_slice = 0
        self.initial_short_rate = initial_short_rate
        self.short_rates = np.ones(num_path) * initial_short_rate
        self.running_dfs = np.ones(num_path)
        self.beta_ts = np.zeros(simu_dates_dfc.shape[0])

    def compute_short_rate(self, fwd_rate, rns):
        if self.current_slice == self.simu_dates.shape[0]:
            raise ValueError('evolve date exceeds the number of simulation dates')
        self.beta_ts[self.current_slice] = fwd_rate + (self.vol * (1 - math.exp(-self.mr * self.simu_dates[self.current_slice])) /
                                               (math.sqrt(2) * self.mr))**2
        if self.current_slice == 0:
            return
        prev_slice = self.current_slice -1
        delta_t = self.simu_dates[self.current_slice] - self.simu_dates[prev_slice]
        param1 = math.exp(-self.mr * delta_t)
        param2 = math.sqrt((1 - math.exp(-self.mr * 2 * delta_t)) / (2 * self.mr))
        self.short_rates = self.short_rates * param1 + self.beta_ts[self.current_slice] - \
                           self.beta_ts[prev_slice] * param1 + \
                           rns * self.vol * param2
        self.running_dfs = self.running_dfs * np.exp(-self.short_rates * delta_t)

    def get_mean_reversion(self):
        return self.mr

    def get_vol(self):
        return self.vol

    def get_current_simu_date(self):
        return self.simu_dates[self.current_slice]

    def get_current_slice(self):
        return self.current_slice

    def get_prev_simu_date(self):
        return self.simu_dates[self.current_slice -1]

    def get_short_rates(self):
        return self.short_rates

    def move_to_next_slice(self):
        self.current_slice = self.current_slice + 1

    def get_running_dfs(self):
        return self.running_dfs

    def get_initial_short_rate(self):
        return self.initial_short_rate

    def get_num_path(self):
        return self.num_path






