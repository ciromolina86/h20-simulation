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
    # print(clx.get_plc_info())

    config_files = ['Level_config.json',
                    'Discharge_Flow_config.json']

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

    # print dataset info
    print(merged_df.shape)
    # merged_df[[
    #     "Program:Ctrl_Sanitary_Lift_Station.PI_Lift_Station_Level",
    #     "Program:Ctrl_Sanitary_Lift_Station.PI_Discharge_Flow"
    #     ]].plot()
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
