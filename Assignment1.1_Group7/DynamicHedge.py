"""
Name:   Dynamic Delta Hedge
Description:
Author:      YANG YIFAN
Created:     2023
"""
# %%
import numpy as np
import math
import BlackScholes as bs
import Utilities

def test_bs(s, k, implied_vol, r, maturity, is_call, position):
    bs_model = bs.BlackScholes(s, k, implied_vol, r, maturity, is_call)
    price = position * bs_model.price()
    delta = position * bs_model.delta()
    gamma = position * bs_model.gamma()
    vega = position * bs_model.vega()
    theta = position * bs_model.theta()
    print("option price", round(price[0], 2))
    print("delta", round(delta[0], 2))
    print("gamma", round(gamma[0], 2))
    print("vega", round(vega[0], 2))
    print("theta", round(theta[0], 2))

def test_share_distribution(share_prices, simu_dates, r, vol):
    ''' test last simulation date'''
    ''' test E[s(t)] and Var[ln(s(t)]'''
    maturity = simu_dates[-1]
    mean_price = share_prices[-1].mean()
    log_share_price = np.log(share_prices[-1])
    var = np.var(log_share_price)
    exp_mean_price = share_prices[0][0] * math.exp(r * maturity)
    exp_var = vol**2 * maturity
    print("simulated share mean price is", round(mean_price, 2))
    print("expected mean price is", round(exp_mean_price, 2))
    print("simulated log share variance is", round(var, 2))
    print("expected log share variance is", round(exp_var, 2))

if __name__ == '__main__':
    '''
    # input parameters #
    rebalace_freq in weeks, T in weeks
    '''
    num_path = 1000
    rebalace_weeks = 1
    s0 = 49
    k = 50
    r = 0.05
    implied_vol = 0.2
    simu_vol = 0.2
    T = 20
    is_call = True
    num_option = 100000
    ''' 
    # end input parameters #
    '''
    ''' 1 test BS implementation'''
    test_bs(s0, k, implied_vol, r, T / 52, is_call, num_option)

    ''' 2 test share price simulation'''
    simu_dates = np.array([x *  rebalace_weeks / 52 for x in range(int(T / rebalace_weeks) + 1)])
    simu_prices = np.zeros([simu_dates.shape[0], num_path])
    Utilities.simuale_share_prices(simu_prices,simu_dates, num_path, s0, r, simu_vol)
    test_share_distribution(simu_prices, simu_dates, r, simu_vol)

    ''' 3 hedge performance evaluation'''
    hedge_costs = np.zeros([simu_dates.shape[0], num_path])
    Utilities.compute_hedge_costs(hedge_costs, simu_prices, simu_dates, k, r, implied_vol, is_call, simu_vol, num_option)
    bs_model = bs.BlackScholes(s0, k, implied_vol, r, T / 52, is_call)
    bs_price = num_option * bs_model.price()
    Utilities.process_hedge_costs(hedge_costs[-1], bs_price, rebalace_weeks)


    ''' Our test results are as follows: '''

    print('\nOur test results are as follows: ')
    # Set seed to generate the same result
    np.random.seed(999)

    print('\nTask 2: ')
    simu_prices = np.zeros([simu_dates.shape[0], num_path])
    Utilities.simuale_share_prices(simu_prices,simu_dates, num_path, s0, r, simu_vol)
    test_share_distribution(simu_prices, simu_dates, r, simu_vol)

    print('\nTask 3: ')
    # Change option spot price and strike both to 48, and is_call parameter set to false
    s0 = 48
    k =48
    is_call = False

    #  Changing rebalance frequency (in weeks) and evaluate the performance at week 20
    for i in [0.25, 0.5, 1, 2, 4]:
        # Generate simulated prices
        rebalace_weeks = i    
        simu_dates = np.array([x *  rebalace_weeks / 52 for x in range(int(T / rebalace_weeks) + 1)])
        simu_prices = np.zeros([simu_dates.shape[0], num_path])
        Utilities.simuale_share_prices(simu_prices,simu_dates, num_path, s0, r, simu_vol)
        
        # Calculate hedge costs
        hedge_costs = np.zeros([simu_dates.shape[0], num_path])
        Utilities.compute_hedge_costs(hedge_costs, simu_prices, simu_dates, k, r, implied_vol, is_call, simu_vol, num_option)

        # Evaluate the hedging performance at T
        bs_model = bs.BlackScholes(s0, k, implied_vol, r, T / 52, is_call)
        bs_price = num_option * bs_model.price()
        Utilities.process_hedge_costs(hedge_costs[-1], bs_price, rebalace_weeks)
        
        # Evaluate the hedging performance at week 12   
        print ("\nAt Week 12: ")
        index_12 = int (12 / rebalace_weeks)
        Utilities.process_hedge_costs(hedge_costs[index_12], bs_price, rebalace_weeks)
        print('')

    #  Set simu_vol to different values of 10%, 15%, 20%, 25%, 30%
    print ("Different volatility: ")
    rebalace_weeks = 1
    for i in [0.1, 0.15, 0.2, 0.25, 0.3]:
        print("\n#simu_vol is", i, "#")
        simu_vol = i    
        simu_dates = np.array([x *  rebalace_weeks / 52 for x in range(int(T / rebalace_weeks) + 1)])

        # Generate simulated prices
        simu_prices = np.zeros([simu_dates.shape[0], num_path])
        Utilities.simuale_share_prices(simu_prices,simu_dates, num_path, s0, r, simu_vol)

        # Calculate hedge costs
        hedge_costs = np.zeros([simu_dates.shape[0], num_path])
        Utilities.compute_hedge_costs(hedge_costs, simu_prices, simu_dates, k, r, implied_vol, is_call, simu_vol, num_option)

        # Evaluate the hedging performance at T
        bs_model = bs.BlackScholes(s0, k, implied_vol, r, T / 52, is_call)
        bs_price = num_option * bs_model.price()
        Utilities.process_hedge_costs(hedge_costs[-1], bs_price, rebalace_weeks)

# %%
