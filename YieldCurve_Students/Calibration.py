"""
Name:   Curve Calibration
Description:
Author:      YANG YIFAN
Created:     2020
"""
# %%
import pandas as pd
import numpy as np
import datetime as dt
import Future
import Swap
import FRA
import FXForward
import Curve
from scipy.optimize import leastsq
import time
import pdb

class curveconstructor(object):
    '''
    curve calibration class
    Attributes
    ==========
    curve_instruments_dict: dict<curve_name: list<instruments> >
    targets : rt (-ln(discount_factor)), numpy array
    curve_dict : all curves need in curve instrumetns pricing dict<curve_name, curve>
                    e.g., to calibrate USD.LIBOR6M, we need USD.OIS, USD.LIBOR.3M curves
    curve_calibration_dict : curves for calibration, dict<curve_name, curve>

    Methods
    =======
    update_curves(y_update) :
        update curves with new iterated curve yiled values, follow order of curve_calibration_dict
    compute_errors():
        return error in array, computed targets - targets
    __init__(curves_info_dict, curves_to_calibrate)
    '''

    def __init__(self, val_date, curves_info_dict, curves_to_calibrate, input_curves_dict={}):
        # step1 initiate curve instruments self.curve_instruments_dict
        # step2 initiate curves to calibrate, curves_to_calibrate, curve initial value is from market quote
        # step3 initiate targets for all curves to be calibrated
        self.version = 0
        self.curve_instruments_dict = {}
        self.curves_to_calibrate = curves_to_calibrate
        self.input_curves_dict = input_curves_dict
        self.curves_info_dict = curves_info_dict
        self.targets = []
        for key in curves_to_calibrate:
            try:
                curve_df = curves_info_dict[key]
            except:
                raise AttributeError(key, 'is not defined in curves_info_dict')
            instruments = []
            x = np.zeros(curve_df.shape[0])
            y = np.zeros(curve_df.shape[0])
            for index, row in curve_df.iterrows():
                target = 0.
                if row['Type'].lower() == 'fedfund future':
                    instruments.append(Future.future(val_date, row['Start Tenor'], row['Tenor'],
                                                     True, row['Market Quote']))
                    target = (100 - row['Market Quote'])/100
                elif row['Type'].lower() == 'future':
                    instruments.append(Future.future(val_date, row['Start Tenor'], row['Tenor'],
                                                     False, row['Market Quote']))
                    target = (100 - row['Market Quote']) / 100
                elif row['Type'].lower() == 'swap':
                    instruments.append(Swap.swap(val_date, row['Tenor'], row['Leg1 Freq'], row['Leg2 Freq'],
                                                 False, row['Market Quote']))
                    target = row['Market Quote']
                elif row['Type'].lower() == 'basis swap':
                    instruments.append(Swap.swap(val_date, row['Tenor'], row['Leg1 Freq'], row['Leg2 Freq'],
                                                 True, row['Market Quote']))
                    target = row['Market Quote']
                elif row['Type'].lower() == 'fra':
                    instruments.append(FRA.fra(val_date, row['Start Tenor'], row['Tenor'], row['Market Quote']))
                    target = row['Market Quote']
                elif row['Type'].lower() == 'fx forward':
                    instruments.append(FXForward.fxforward(val_date, row['Tenor'], 108., row['Market Quote']))
                    target = instruments[-1].convert_marketquote_to_target()
                else:
                    raise AttributeError('only 7 type instruments are implemented: '
                                         'fedfund fture, future, swap, basis swap,'
                                         'fra, fx forward, mtmxccy basis swap')
                x[index] = instruments[-1].get_maturity()
                y[index] = 0.
                self.targets.append(target)
            self.curves_to_calibrate[key] = Curve.curve(key, val_date, x, y)
            self.curve_instruments_dict[key] = instruments
        # step4 sanity check, sum of curve y vector size must be equal to targets size
        self.targets = np.array(self.targets)
        yvec_count = 0.
        for key, value in self.curves_to_calibrate.items():
            yvec_count += value.y.shape[0]
        if yvec_count != self.targets.shape[0]:
            raise ValueError("number of targets is not equal to the total number of curve size")
        # step5 assign curves to curve instruments
        self.__assign_curves()

    def __assign_curves(self):
        '''
        Assign curves to each instrument, e.g., fedfund/libor basis swap, we assign 3 curves for this instrument
        curves are passed by reference, e.g., only 1 instance of ois curve, shared by all instruments
        in this way as long as we update the curve, all instruments will be refreshed as well
        :return:
        '''
        for key, value in self.curve_instruments_dict.items():
            for instrument in value:
                if isinstance(instrument, Future.future):
                    array = ['future', 'fedfund future']
                    curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['ForwardCurve'].iloc[0]
                    if curve_name in self.curves_to_calibrate:
                        instrument.forward_curve = self.curves_to_calibrate[curve_name]
                    elif curve_name in self.input_curves_dict:
                        instrument.forward_curve = self.input_curves_dict[curve_name]
                    else:
                        raise AttributeError(curve_name, 'is not found in initial curves')
                elif isinstance(instrument, Swap.swap):
                    array = ['swap', 'basis swap']
                    discount_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['DiscountCurve'].iloc[0]
                    forward_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['Leg2 ForwardCurve'].iloc[0]
                    if discount_curve_name in self.curves_to_calibrate:
                        instrument.leg1_discount_curve = self.curves_to_calibrate[discount_curve_name]
                        instrument.leg2_discount_curve = self.curves_to_calibrate[discount_curve_name]
                    elif discount_curve_name in self.input_curves_dict:
                        instrument.leg1_discount_curve = self.input_curves_dict[discount_curve_name]
                        instrument.leg2_discount_curve = self.input_curves_dict[discount_curve_name]
                    else:
                        raise AttributeError(discount_curve_name, 'is not found in initial curves')
                    if forward_curve_name in self.curves_to_calibrate:
                        instrument.leg2_forward_curve = self.curves_to_calibrate[forward_curve_name]
                    elif forward_curve_name in self.input_curves_dict:
                        instrument.leg2_forward_curve = self.input_curves_dict[forward_curve_name]
                    else:
                        raise AttributeError(forward_curve_name, 'is not found in initial curves')
                    if instrument.is_basis_swap:
                        forward_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                            ['ForwardCurve'].iloc[0]
                        if forward_curve_name in self.curves_to_calibrate:
                            instrument.leg1_forward_curve = self.curves_to_calibrate[forward_curve_name]
                        elif forward_curve_name in self.input_curves_dict:
                            instrument.leg1_forward_curve = self.input_curves_dict[forward_curve_name]
                        else:
                            raise AttributeError(forward_curve_name, 'is not found in initial curves')
                    instrument.update_cashflow_curves()
                elif isinstance(instrument, FRA.fra):
                    array = ['FRA']
                    forward_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['ForwardCurve'].iloc[0]
                    if forward_curve_name in self.curves_to_calibrate:
                        instrument.forward_curve = self.curves_to_calibrate[forward_curve_name]
                    elif forward_curve_name in self.input_curves_dict:
                        instrument.forward_curve = self.input_curves_dict[forward_curve_name]
                    else:
                        raise AttributeError(forward_curve_name, 'is not found in initial curves')
                elif isinstance(instrument, FXForward.fxforward):
                    array = ['fx forward']
                    dom_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['DiscountCurve'].iloc[0]
                    for_curve_name = self.curves_info_dict[key].loc[self.curves_info_dict[key]['Type'].isin(array)]\
                        ['Leg2 DiscountCurve'].iloc[0]
                    if dom_curve_name in self.curves_to_calibrate:
                        instrument.dom_curve = self.curves_to_calibrate[dom_curve_name]
                    elif dom_curve_name in self.input_curves_dict:
                        instrument.dom_curve = self.input_curves_dict[dom_curve_name]
                    else:
                        raise AttributeError(dom_curve_name, 'is not found in initial curves')
                    if for_curve_name in self.curves_to_calibrate:
                        instrument.for_curve = self.curves_to_calibrate[for_curve_name]
                    elif for_curve_name in self.input_curves_dict:
                        instrument.for_curve = self.input_curves_dict[for_curve_name]
                    else:
                        raise AttributeError(for_curve_name, 'is not found in initial curves')
                else:
                    raise AttributeError(type(instrument), 'is not supported instrument type in curve calibration')

    def update_curve_yvectors(self, ynews):
        pos = 0
        for key, value in self.curves_to_calibrate.items():
            if not isinstance(value, Curve.curve):
                raise AttributeError('curves_to_calibrate value is not with type curve')
            value.update(ynews[pos:pos+value.y.shape[0]])
            pos += value.y.shape[0]

    def compute_target(self):
        computed_targets = []
        for key, value in self.curve_instruments_dict.items():
            for instrument in value:
                computed_targets.append(instrument.compute_target_rate())
        computed_targets = np.array(computed_targets)
        if computed_targets.shape[0] != self.targets.shape[0]:
            raise ValueError("computed targets and targets are not the same size")
        return computed_targets

def read_curves_info(file_path_name, curves_info_dict):
    '''
    :param file_path_name: input file, which has curve instrumetns information
    :param curves_info_dict: pass by reference, dict, key: curve name, value: dataframe
    :return:
    '''
    curve_names = []
    curve_row_pos = []
    count = 1
    with open(file_path_name) as fp:
        for line in fp:
            line_components = line.split(':')
            if line_components[0].upper() == 'CURVE':
                curve_names.append(line_components[1].rstrip(',\n'))
                curve_row_pos.append(count + 1)
            count += 1
    fp.close()
    for i in range(len(curve_names)):
        if i != len(curve_names) - 1:
            row_pos_bottom = (count - 1) - (curve_row_pos[i+1]-1) + 1
            curves_info_dict[curve_names[i]] = pd.read_csv(file_path_name, skiprows=curve_row_pos[i]-1,
                                                      skipfooter=row_pos_bottom, engine='python')
        else:
            curves_info_dict[curve_names[i]] = pd.read_csv(file_path_name, skiprows=curve_row_pos[i] - 1)

def read_input_curves(val_date, file_path_name, input_curve_names, input_curves_dict):
    if not input_curve_names:
        return
    curves_info_dict = {}
    read_curves_info(file_path_name, curves_info_dict)
    for name in input_curve_names:
        if name in curves_info_dict:
            x = np.array(curves_info_dict[name]['maturity year frac'])
            y = np.array(curves_info_dict[name]['zero rate'])
            input_curves_dict[name] = Curve.curve(name, val_date, x, y)
        else:
            raise ValueError(name, "is not found in input curve result file")

def calibration_object_function(yvalues, curve_constructor):
    '''
    object function for levmar solver
    :param yvalues:
    :param curve_constructor:
    :return:
        calibration error, computed targets minus true targets
    '''
    if not isinstance(curve_constructor, curveconstructor):
        raise AttributeError("class object curveconstructor is not passed to calibration function properly")
    curve_constructor.update_curve_yvectors(yvalues)
    return curve_constructor.compute_target() - curve_constructor.targets

def calibrate_curves(val_date, input_file_pathname, output_file_pathname,
                     curves_to_calibrate, input_curve_names, input_curve_result_pathname = ''):

    # curve instruments detail, input
    curves_info_dict = {}
    read_curves_info(input_file_pathname, curves_info_dict)

    # parent curves as input, e.g., to calibrate 6m curve, ois and 3m curve are input
    input_curves_dict = {}
    read_input_curves(val_date, input_curve_result_pathname, input_curve_names, input_curves_dict)

    # curveconstructor class, hold instruments and its curves
    curve_constructor = curveconstructor(val_date, curves_info_dict, curves_to_calibrate, input_curves_dict)
    y_initial = np.zeros(len(curve_constructor.targets))
    start = time.time()
    y_calibration, success = leastsq(calibration_object_function, y_initial, args=(curve_constructor,))
    end = time.time()
    print('solver computation time', end - start)

    # # save result back to csv file
    curve_constructor.update_curve_yvectors(y_calibration)
    # save_calibration_results(curve_constructor, output_file_pathname)

if __name__ == '__main__':
    val_date = dt.datetime(year=2020, month=1, day=2)

    ## calib set 1, USD OIS, USD LIBOR.3M
    # step 1, input
    # input_file_pathname = r'C:\Yifan\Teaching\Project\YieldCurve_Students\USD_calibration.csv'
    # output_file_pathname = r'C:\Yifan\Teaching\Project\YieldCurve_Students\USDOISLIBOR3M_result.csv'
    input_file_pathname = 'USD_calibration.csv'
    output_file_pathname = 'USDOISLIBOR3M_result.csv'
    # step 2 this is to tell which curves we want to calibrate, could be multiple curves
    curves_to_calibrate = {'USD.OIS': pd.DataFrame(),
                           'USD.LIBOR.3M': pd.DataFrame()}

    # step 3 this is to tell parent curve information, e.g., USD.LIBOR.6M is dependent on USD.OIS and USD.LIBOR.3M
    input_curve_names = []
    input_curve_result_pathname =''

    ## calib set 2, USD.LIBOR.6M
    # input_file_pathname = r'C:\Yifan\Teaching\Project\YieldCurve_Students\USD_calibration.csv'
    # output_file_pathname = r'C:\Yifan\Teaching\Project\YieldCurve_Students\USDLIBOR6M_result.csv'
    # curves_to_calibrate = {'USD.LIBOR.6M': pd.DataFrame()}
    # input_curve_names = ['USD.OIS', 'USD.LIBOR.3M']
    # input_curve_result_pathname = r'C:\Yifan\Teaching\Project\YieldCurve\USDOISLIBOR3M_result.csv'

    calibrate_curves(val_date, input_file_pathname, output_file_pathname,
                     curves_to_calibrate, input_curve_names, input_curve_result_pathname)

# %%
