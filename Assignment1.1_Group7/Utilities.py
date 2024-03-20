"""
Name:   Utilities for dynamic delta hedging
Description:
Author:      YANG YIFAN
Created:     2023
"""
import BlackScholes as bs
import numpy as np
import math

def simuale_share_prices(share_prices, simu_dates, num_path, s0, r, simu_vol):
    '''
    simulate share price on each path and each simulation date
    :param share_prices: output, numpy array, size the number of simulation dates * the number of path
    :param simu_dates:
    :param num_path:
    :param r: interest free rate
    :param simu_vol: const vol in log normal model
    :return:
    '''
    # student implementation #
    num_dates = simu_dates.shape[0]
    delta_times = np.diff(simu_dates).reshape(num_dates-1,1)
    share_prices[0, :] = s0
    rd = np.random.normal(0, 1, size=(num_dates-1,num_path))
    for j in range(num_dates-1):
        share_prices[j + 1, :] = share_prices[j, :] * np.exp((r - 0.5 * simu_vol**2) * delta_times[j] + simu_vol * np.sqrt(delta_times[j]) * rd[j])
    return share_prices

def compute_hedge_costs(hedge_costs, simu_prices, simu_dates, k, r, implied_vol, is_call, simu_vol, num_option):
    '''
    compute hedging costs, per simulation path, per rebalance perid
    :param share_prices: output, numpy array, size the number of simulation dates * the number of path
    :param simu_dates: generated by rebalance freq
    :param k: strike
    :param r: interest free rate
    :param implied_vol: for option pricing
    :param simu_vol: for share pricing simulation, realized vol
    :param r: the number of option to be hedged
    :return:
    '''
    # student implementation #
    num_dates = simu_dates.shape[0]
    last_date_index = num_dates - 1
    delta_times = np.diff(simu_dates)
    
    shares = np.zeros(hedge_costs.shape[1])
    cash_cost = np.zeros(hedge_costs.shape[1])
    for i in range(num_dates-1):
        option = bs.BlackScholes(simu_prices[i], k, implied_vol, r, simu_dates[-1] - simu_dates[i], is_call)
        # get delta
        delta = option.delta() * num_option
        # calculate the number of difference in shares to buy
        buy = delta - shares
        shares = delta
        delta_time = delta_times[i-1] if i>0 else 0
        cash_cost = cash_cost * np.exp(r * delta_time) + buy * simu_prices[i]
        # calculate the hedge cost
        hedge_costs[i] = cash_cost - shares * simu_prices[i] + option.price() * num_option
    
    # Last date, delta = 0
    cash_cost = cash_cost * np.exp(r * delta_times[last_date_index - 1]) - shares * simu_prices[last_date_index]
    shares = 0
    option_price = np.maximum(simu_prices[last_date_index] - k, 0) if is_call else np.maximum(k - simu_prices[last_date_index], 0)
    hedge_costs[last_date_index] = cash_cost - shares * simu_prices[last_date_index] + option_price * num_option
    
    return hedge_costs

def process_hedge_costs(hedge_cost, bs_price, rebalace_weeks):
    mean_hedge_cost = hedge_cost.mean()
    std_hedge_cost = np.std(hedge_cost)
    hedge_ratio = std_hedge_cost/ bs_price[0]
    print("#rebalance weeks is", rebalace_weeks, "#")
    print("mean hedge cost is", round(mean_hedge_cost, 2))
    print("standard deviation hedge cost is", round(std_hedge_cost, 2))
    print("hedge ratio is", round(hedge_ratio , 2))
    print("#end rebalance weeks", rebalace_weeks, "#")
