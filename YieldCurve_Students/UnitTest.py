"""
Name:   Unit Test
Description:
Author:      YANG YIFAN
Created:     2020
"""
# %%
import Curve
import Swap
import Future
import FRA
import FXForward
# import MTMXccySwap
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

def test_curve(val_date):
    name = 'test_curve'
    x = np.arange(0, 10)
    y = np.array([0.005 for xx in range(1, 11)])
    test_curve = Curve.curve(name, val_date, x, y)
    fwd_date_start = val_date + relativedelta(years=+5)
    fwd_date_end = val_date + relativedelta(years=+6)
    fwd_rate = test_curve.get_forward_rate(fwd_date_start, fwd_date_end)
    print('extrapolation at 15Y', test_curve.get_discount_factor(15), fwd_rate)
    y_update = np.array([0.007 for xx in range(1, 11)])
    test_curve.update(y_update)
    fwd_rate = test_curve.get_forward_rate(fwd_date_start, fwd_date_end)
    print('extrapolation at 15Y', test_curve.get_discount_factor(15), fwd_rate)

def test_swap(val_date):
    x = np.arange(1, 11)
    y = 0.02 * np.ones(10)
    leg1_discount_curve = Curve.curve("dis_curve1", val_date, x, y)
    leg2_discount_curve = Curve.curve("dis_curve1", val_date, x, y)
    y = 0.03 * np.ones(10)
    leg1_forward_curve = Curve.curve("fwd_curve1", val_date, x, y)
    leg2_forward_curve = Curve.curve("fwd_curve1", val_date, x, y)
    # test fixed flow vanilla swap
    vanilla_swap = Swap.swap(val_date, '5Y', '6M', '3M', False, 0.04, 1000000,
                             leg1_discount_curve, leg1_forward_curve, leg2_discount_curve, leg2_forward_curve)
    print('5Y fixed float vanilla swap mtm is:', str(vanilla_swap.compute_mtm()))
    print('5Y implied fixed rate is:', str(vanilla_swap.compute_target_rate()))
    y_update = 0.05 * np.ones(10)
    leg2_forward_curve.update(y_update)
    print('Updated 5Y implied fixed rate is:', str(vanilla_swap.compute_target_rate()))
    # test basis swap
    # leg1 discount/forecast by the same curve, leg2 different curves
    basis_swap = Swap.swap(val_date, '5Y', '3M', '3M', True, 0.01, 1000000,
                             leg1_discount_curve, leg1_discount_curve, leg2_discount_curve, leg2_forward_curve)
    print('5Y basis swap mtm is:', str(basis_swap.compute_mtm()))
    print('5Y implied basis swap margin is:', str(basis_swap.compute_target_rate()))
    # test stub period, 9M swap
    vanilla_swap2 = Swap.swap(val_date, '9M', '12M', '3M', False, 0.04, 1000000,
                             leg1_discount_curve, leg1_forward_curve, leg2_discount_curve, leg2_forward_curve)
    print('9M fixed float vanilla swap mtm is:', str(vanilla_swap2.compute_mtm()))
    print('9M implied fixed rate is:', str(vanilla_swap2.compute_target_rate()))
    vanilla_swap3 = Swap.swap(val_date, '18M', '12M', '3M', False, 0.04, 1000000,
                             leg1_discount_curve, leg1_forward_curve, leg2_discount_curve, leg2_forward_curve)
    print('18M fixed float vanilla swap mtm is:', str(vanilla_swap3.compute_mtm()))
    print('18M implied fixed rate is:', str(vanilla_swap3.compute_target_rate()))

def test_future(val_date):
    x = np.arange(1, 11)
    y = 0.02 * np.ones(10)
    discount_curve = Curve.curve("dis_curve1", val_date, x, y)
    y = 0.03 * np.ones(10)
    forward_curve = Curve.curve("fwd_curve1", val_date, x, y)
    future = Future.future(val_date, '6M', '3M', False, 98., 1000000, discount_curve, forward_curve)
    print('6m implied Eurodollar future price is:', str(100 * (1. - future.compute_target_rate())))
    fedfund_future = Future.future(val_date, '9M', '1M', True, 98., 1000000, discount_curve, forward_curve)
    print('6m implied fedfund future price is:', str(100 * (1. - fedfund_future.compute_target_rate())))

def test_fra(val_date):
    x = np.arange(1, 11)
    y = 0.02 * np.ones(10)
    discount_curve = Curve.curve("dis_curve1", val_date, x, y)
    y = 0.03 * np.ones(10)
    forward_curve = Curve.curve("fwd_curve1", val_date, x, y)
    fra = FRA.fra(val_date, '6M', '3M', 0.03, 1000000, discount_curve, forward_curve)
    print('6m-3m implied FRA rate', fra.compute_target_rate())

def test_fxforward(val_date):
    x = np.arange(1, 11)
    y = 0.01 * np.ones(10)
    dom_curve = Curve.curve("jpy_curve", val_date, x, y)
    y = 0.02 * np.ones(10)
    for_curve = Curve.curve("usd_curve", val_date, x, y)
    fxforward = FXForward.fxforward(val_date, '9m', 108, 107.1923, dom_curve, for_curve)
    print('9m USDJPY FX Forward target rate', fxforward.compute_target_rate())
    print('9m USDJPY FX Forward market quote to target', fxforward.convert_marketquote_to_target())

# def test_mtmxccyswap(val_date):
#     x = np.arange(1, 11)
#     y = 0.02 * np.ones(10)
#     jpy_discount_curve = Curve.curve("dis_curve1", val_date, x, y)
#     y = 0.03 * np.ones(10)
#     usd_discount_curve = Curve.curve("dis_curve2", val_date, x, y)
#     y = 0.01 * np.ones(10)
#     jpy_forward_curve = Curve.curve("fwd_curve1", val_date, x, y)
#     y = 0.03 * np.ones(10)
#     usd_forward_curve = Curve.curve("fwd_curve2", val_date, x, y)
#
#     # test mtmxccy basis swap
#     # leg1 discount/forecast by the same curve, leg2 different curves
#     basis_swap = MTMXccySwap.XccySwap(val_date, '5Y', '3M', '3M', True, -0.002, 108000000, 1000000,
#                                       jpy_discount_curve, jpy_forward_curve, usd_discount_curve, usd_forward_curve,
#                                       108., True, True)
#     print('5Y mtm xccy swap mtm is:', str(basis_swap.compute_mtm()))
#     print('5Y mtm xccy implied margin is:', str(basis_swap.compute_target_rate()))

if __name__ == '__main__':
    val_date = dt.datetime(2020, 1, 2)
    # test_curve(val_date)
    test_swap(val_date)
    # test_future(val_date)
    # test_fra(val_date)
    # test_fxforward(val_date)
    # test_mtmxccyswap(val_date)




# %%
