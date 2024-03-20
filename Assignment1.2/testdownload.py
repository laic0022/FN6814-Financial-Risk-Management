'''
Name:   download
Description:
Author:      YANG YIFAN
Created:     2019
'''
import xml.etree.ElementTree as ET
import numpy as np
import datetime as dt
import pandas as pd

namespace = {'default': 'http://www.w3.org/2005/Atom',
             'properties': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata',
             'data': 'http://schemas.microsoft.com/ado/2007/08/dataservices'}
tenors = ['NEW_DATE', 'BC_6MONTH', 'BC_1YEAR', 'BC_2YEAR', 'BC_3YEAR',
          'BC_5YEAR', 'BC_7YEAR', 'BC_10YEAR', 'BC_20YEAR', 'BC_30YEAR']

def ParseTreasuryYields(start_date, end_date, xml_filename):
    '''
    :param start_date:
    :param end_date:
    :param xml_filename:
    :return:
    '''
    dict = {}  # save data in dictionary
    tree = ET.parse(xml_filename)
    root = tree.getroot()
    for tenor in tenors:
        if tenor == 'NEW_DATE':
            dict[tenor] = np.array([], 'datetime64')
        else:
            dict[tenor] = np.array([], float)

    count = 1
    for entry in root.findall('default:entry', namespace):
        ++count
        content = entry.find('default:content', namespace)
        properties = content.find('properties:properties', namespace)
        for tenor in tenors:
            data = properties.find('data:' + tenor, namespace)
            if tenor == 'NEW_DATE':
                dict[tenor] = np.append(dict[tenor], dt.datetime.strptime(data.text, '%Y-%m-%dT%H:%M:%S').date())
            else:
                dict[tenor] = np.append(dict[tenor], float(data.text)) if type(data.text) == str \
                    else np.append(dict[tenor], 0.)
    print(count)
    df = pd.DataFrame.from_dict(dict)
    df = df.sort_values(by=['NEW_DATE'])
    df = df.loc[df['NEW_DATE'] >= dt.datetime.strptime(start_date, '%Y-%m-%d').date()]
    df = df.loc[df['NEW_DATE'] <= dt.datetime.strptime(end_date, '%Y-%m-%d').date()]
    df.set_index('NEW_DATE', inplace=True)
    return df
