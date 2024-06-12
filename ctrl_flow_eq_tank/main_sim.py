import os
import time
import datetime
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler


def write_pv_tag(plc, tag, value):
    plc.write_single_tag(tag, value)


if __name__ == '__main__':
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager()
    print(clx.get_plc_info())

    # Relative path to the JSON file
    filepath = os.path.join(os.path.dirname(__file__), 'LIT_30_01_config.json')

    # Compute Process Variable to be simulated
    name, desc, unit, waveform = signal_handler.compute_pv(filepath)

    # Write Process Variable to PLC every 1 second
    while True:
        for t, v in waveform:
            # print(f'{datetime.datetime.now()}\t|\tsecond={t}\t|\tvalue={v:.2f}')
            write_pv_tag(clx, name, v)
            time.sleep(1)
