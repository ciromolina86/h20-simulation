import os
import subprocess
import multiprocessing
import time
import datetime
import matplotlib.pyplot as plt
from handlers import *
from ctrl_flow_eq_tank import *


def sim_pv():
    subprocess.run(["python", "sim_pv.py"])


def sim_auto():
    subprocess.run(["python", "sim_auto.py"])


def sim_oor():
    subprocess.run(["python", "sim_oor.py"])


def sim_reset():
    subprocess.run(["python", "sim_reset.py"])


def sim_util_power():
    subprocess.run(["python", "sim_util_power.py"])


def main():
    # TODO : scripts execute sequencially. I need them to execute simultaneously.

    # Crear procesos
    process1 = multiprocessing.Process(target=sim_pv)
    process2 = multiprocessing.Process(target=sim_auto)
    process3 = multiprocessing.Process(target=sim_oor)
    process4 = multiprocessing.Process(target=sim_reset)
    process5 = multiprocessing.Process(target=sim_util_power)

    # Iniciar procesos
    process1.start()
    process2.start()
    process3.start()
    process4.start()
    process5.start()

    # Esperar a que los procesos terminen
    process1.join()
    process2.join()
    process3.join()
    process4.join()
    process5.join()


if __name__ == '__main__':
    main()
