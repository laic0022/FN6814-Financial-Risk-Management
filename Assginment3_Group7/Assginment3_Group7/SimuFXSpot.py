"""
Name:   Curve class
Description:
Author:      YANG YIFAN
Created:     2021
"""
import numpy as np
import math

class simufxspot():
    '''
    simulation fx spot class, GBM model with stochastic rates
    Attributes
    ==========
    dom_simu_curve: domestic currency simulated curve
    for_simu_curve: foreign currency simulated curve
    simu_fx_spots: simulated fx spot rates of current step

    Methods
    =======
    simulate_fx_spot(xval):
        step wise simulation for fx spot, from prev step to current step
    '''

    def __init__(self, initial_fx_spot, fx_vol, simu_dates_dfc, dom_simu_curve, for_simu_curve):
        self.initial_fx_spot = initial_fx_spot
        self.fx_vol = fx_vol
        self.simu_dates = simu_dates_dfc
        self.dom_simu_curve = dom_simu_curve
        self.for_simu_curve = for_simu_curve
        self.current_slice = 0
        self.simu_fx_spots = []

    def simulate_fx_spot(self, rns):
        if self.current_slice == 0:
            self.simu_fx_spots = np.ones(len(rns)) * self.initial_fx_spot
            start_date = 0
        else:
            prev_slice = self.current_slice -1
            start_date = self.simu_dates[prev_slice]

        end_date = self.simu_dates[self.current_slice]
        delta_t = end_date - start_date
        drift = (self.dom_simu_curve.hw_model.get_short_rates() - self.dom_simu_curve.hw_model.get_short_rates() - 0.5 * self.fx_vol**2) * delta_t
        diffusion = self.fx_vol * rns * np.sqrt(delta_t)
        self.simu_fx_spots = self.simu_fx_spots * np.exp(drift + diffusion)

    def get_fx_spots(self):
        return self.simu_fx_spots


    def move_to_next_slice(self):
        self.current_slice += 1

