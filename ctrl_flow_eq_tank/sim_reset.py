import os
import time
import datetime
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler


def write_pv_tag(plc, tag, value):
    plc.write_single_tag(tag, value)


def main():
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager()
    print(clx.get_plc_info())

    # Relative path to the JSON file
    file_path_1 = os.path.join(os.path.dirname(__file__), '../config_files/Water_Off_Range_SCADA_Reset_config.json')

    # Compute Process Variable to be simulated
    name_1, desc_1, unit_1, waveform_1 = signal_handler.compute_pv(file_path_1)

    # Write Process Variable to PLC every 1 second
    while True:
        for t, v in waveform_1:
            # print(f'{datetime.datetime.now()}\t|\tsecond={t}\t|\tvalue={v:.2f}')
            write_pv_tag(clx, name_1, v)
            time.sleep(1)


if __name__ == '__main__':
    main()
