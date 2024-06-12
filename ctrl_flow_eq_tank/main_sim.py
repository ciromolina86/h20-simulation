import os
import time
import datetime
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler
import sim_pv
import sim_oor
import sim_reset


def write_pv_tag(plc, tag, value):
    plc.write_single_tag(tag, value)


def main():
    # TODO : scripts execute sequencially. I need them to execute simultaneously.
    sim_pv.main()
    sim_oor.main()
    sim_reset.main()


if __name__ == '__main__':
    main()
