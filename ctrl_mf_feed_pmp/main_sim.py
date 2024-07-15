import os
import subprocess
import multiprocessing
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler


def write_pv_tags(plc, tags, values):
    plc.write_multiple_tags(tags, values)


def main():
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    print(clx.get_plc_info())

    config_files = ['Feed_Tank_Level_config.json',
                    'Inlet_Pressure_config.json']

    # init data with first tag values
    file_path = os.path.join('config_files', config_files[0])
    data = signal_handler.compute_pv_dict(file_path)
    merged_df = pd.DataFrame({'idx': data['idx'], data['name']: data['waveform']})

    # attach rest of tag values to dataset
    for file in config_files[1:]:
        file_path = os.path.join('config_files', file)
        data = signal_handler.compute_pv_dict(file_path)
        df = pd.DataFrame({'idx': data['idx'], data['name']: data['waveform']})
        merged_df = pd.merge(merged_df, df, on='idx')

    # Relative path to the JSON file
    # file_path_1 = os.path.join('config_files', 'FIT_30_04_config.json')
    # file_path_2 = os.path.join('config_files', 'LIT_30_01_config.json')
    # file_path_3 = os.path.join('config_files', 'PSH_30_04_config.json')
    # file_path_4 = os.path.join('config_files', 'TSH_30_04_config.json')
    # file_path_5 = os.path.join('config_files', 'Power_Fault_config.json')
    # file_path_6 = os.path.join('config_files', 'Common_Fault_config.json')
    # file_path_7 = os.path.join('config_files', 'VFD_Fault_config.json')
    #
    # # Compute Process Variable to be simulated
    # data_1 = signal_handler.compute_pv_dict(file_path_1)
    # data_2 = signal_handler.compute_pv_dict(file_path_2)
    # data_3 = signal_handler.compute_pv_dict(file_path_3)
    # data_4 = signal_handler.compute_pv_dict(file_path_4)
    # data_5 = signal_handler.compute_pv_dict(file_path_5)
    # data_6 = signal_handler.compute_pv_dict(file_path_6)
    # data_7 = signal_handler.compute_pv_dict(file_path_7)
    #
    # # Merge all data to single dataset
    # df1 = pd.DataFrame({'idx': data_1['idx'], data_1['name']: data_1['waveform']})
    # df2 = pd.DataFrame({'idx': data_2['idx'], data_2['name']: data_2['waveform']})
    # df3 = pd.DataFrame({'idx': data_3['idx'], data_3['name']: data_3['waveform']})
    # df4 = pd.DataFrame({'idx': data_4['idx'], data_4['name']: data_4['waveform']})
    # df5 = pd.DataFrame({'idx': data_5['idx'], data_5['name']: data_5['waveform']})
    # df6 = pd.DataFrame({'idx': data_6['idx'], data_6['name']: data_6['waveform']})
    # df7 = pd.DataFrame({'idx': data_7['idx'], data_7['name']: data_7['waveform']})
    # merged_df = df1
    # merged_df = pd.merge(merged_df, df2, on='idx')
    # merged_df = pd.merge(merged_df, df3, on='idx')
    # merged_df = pd.merge(merged_df, df4, on='idx')
    # merged_df = pd.merge(merged_df, df5, on='idx')
    # merged_df = pd.merge(merged_df, df6, on='idx')
    # merged_df = pd.merge(merged_df, df7, on='idx')
    # print dataset info
    print(merged_df.shape)
    # merged_df.plot()
    # plt.show()

    # Write Process Variable to PLC every 1 second
    rows, cols = merged_df.shape
    print(merged_df.columns)

    while True:
        for i in range(rows):
            print(f"{list(merged_df.columns[:])}")
            print(f"{list(merged_df.iloc[i, :])}")
            write_pv_tags(clx, list(merged_df.columns[1:]), list(merged_df.iloc[i, 1:]))
            time.sleep(1)


if __name__ == '__main__':
    main()
