import os
import subprocess
import multiprocessing
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler


def write_pv_tags(plc, tags, values):
    plc.write_multiple_tags(tags, values)


def main():
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager()
    print(clx.get_plc_info())

    # Relative path to the JSON file
    file_path_1 = os.path.join('config_files', 'FIT_30_04_config.json')
    file_path_2 = os.path.join('config_files', 'LIT_30_01_config.json')
    # file_path_3 = os.path.join('config_files', 'Power_Failure_config.json')

    # Compute Process Variable to be simulated
    data_1 = signal_handler.compute_pv_dict(file_path_1)
    data_2 = signal_handler.compute_pv_dict(file_path_2)
    # data_3 = signal_handler.compute_pv_dict(file_path_3)

    # Merge all data to single dataset
    df1 = pd.DataFrame({'idx': data_1['idx'], data_1['name']: data_1['waveform']})
    df2 = pd.DataFrame({'idx': data_2['idx'], data_2['name']: data_2['waveform']})
    # df3 = pd.DataFrame({'idx': data_3['idx'], data_3['name']: data_3['waveform']})
    merged_df = df1
    merged_df = pd.merge(merged_df, df2, on='idx')
    # merged_df = pd.merge(merged_df, df3, on='idx')
    print(merged_df.shape)
    merged_df[['AOI_C_Loop_Cascade_Aerator_Recycle_Pump.FIT_30_04',
               'AOI_C_Loop_Cascade_Aerator_Recycle_Pump.LIT_30_01']].plot()
    plt.show()

    # Write Process Variable to PLC every 1 second
    rows, cols = merged_df.shape
    while True:

        for i in range(rows):
            print(f"{list(merged_df.columns[:])}")
            print(f"{list(merged_df.iloc[i, :])}")
            write_pv_tags(clx, list(merged_df.columns[1:]), list(merged_df.iloc[i, 1:]))
            time.sleep(1)


if __name__ == '__main__':
    main()
