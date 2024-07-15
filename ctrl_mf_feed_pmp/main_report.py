import time
import datetime
import csv
import matplotlib.pyplot as plt
from handlers import comm_handler, signal_handler, plot_handler


def read_report_tags(plc, tags):
    plc.read_multiple_tags(tags)


def plot_report(**kwargs):
    # plot waveform for visual inspection
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f"{kwargs['pv_1']['desc']}")
    ax.set_xlabel(f"Time [s]")
    ax.set_ylabel(f"Process Variable [{kwargs['pv_1']['unit']}]")
    ax.grid(True)

    _time_array, _value_array = list(zip(*kwargs['pv_1']['waveform']))
    ax.plot(_time_array, _value_array, color='black', alpha=0.8, label=kwargs['pv_1']['name'])
    plt.legend()
    plt.show()

    # ax.axhline(y=high_limit,
    #            color='red',
    #            linestyle='--',
    #            label='High Threshold')
    # ax.fill_between(total_duration_array, high_limit, high_high_threshold,
    #                 color='red',
    #                 alpha=0.2,
    #                 label='High High Band')
    # ax.axhline(y=high_high_threshold,
    #            color='red',
    #            linestyle='--',
    #            label='High Threshold')
    # ax.fill_between(total_duration_array, high_high_threshold, high_threshold,
    #                 color='yellow',
    #                 alpha=0.2,
    #                 label='High Band')
    # ax.axhline(y=high_threshold,
    #            color='red',
    #            linestyle='--',
    #            label='High Threshold')
    # ax.fill_between(total_duration_array, high_threshold, low_threshold,
    #                 color='green',
    #                 alpha=0.2,
    #                 label='Control Band')
    # ax.plot(total_duration_array, total_wave_array,
    #         color='black',
    #         alpha=0.8)
    # ax.axhline(y=low_threshold,
    #            color='red',
    #            linestyle='--',
    #            label='Low Threshold')
    # ax.fill_between(total_duration_array, low_threshold, low_low_threshold,
    #                 color='yellow',
    #                 alpha=0.2,
    #                 label='Low Band')
    # ax.axhline(y=low_low_threshold,
    #            color='red',
    #            linestyle='--',
    #            label='Low Threshold')
    # ax.fill_between(total_duration_array, low_low_threshold, low_limit,
    #                 color='red',
    #                 alpha=0.2,
    #                 label='Low Low Band')
    # ax.axhline(y=low_limit,
    #            color='red',
    #            linestyle='--',
    #            label='Low Threshold')
    #
    # plt.legend(loc='lower center', ncol=2)
    # plt.show()


def write_to_csv(file_name, field_names, data):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writerow(data)


def main():
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    print(clx.get_plc_info())

    csv_file_name = f"report-mf-feed-pmp-{time.strftime('%Y-%m-%d-%H-%M')}.csv"
    tags = ['Ctrl_MF_Feed_Pumps.PI_Feed_Tank_Level',
            'Ctrl_MF_Feed_Pumps.PI_Hyd_LL_SP',
            'Ctrl_MF_Feed_Pumps.PI_Inlet_Pressure',
            'Ctrl_MF_Feed_Pumps.PI_Inlet_Pressure_SP',
            'Ctrl_MF_Feed_Pumps.PI_Max_Pmp_Speed_SP',
            'Ctrl_MF_Feed_Pumps.PI_Min_Pmp_Speed_SP',
            'Ctrl_MF_Feed_Pumps.PI_Op_Pressure_SP',
            'Ctrl_MF_Feed_Pumps.PI_Pump_1_Assignment',
            'Ctrl_MF_Feed_Pumps.PI_Pump_1_Speed_Fbk',
            'Ctrl_MF_Feed_Pumps.PI_Pump_1_Sts_Running',
            'Ctrl_MF_Feed_Pumps.PI_Pump_2_Assignment',
            'Ctrl_MF_Feed_Pumps.PI_Pump_2_Speed_Fbk',
            'Ctrl_MF_Feed_Pumps.PI_Pump_2_Sts_Running',
            'Ctrl_MF_Feed_Pumps.PI_Pump_3_Assignment',
            'Ctrl_MF_Feed_Pumps.PI_Pump_3_Speed_Fbk',
            'Ctrl_MF_Feed_Pumps.PI_Pump_3_Sts_Running',
            'Ctrl_MF_Feed_Pumps.PI_Start_Pmps_Delay_SP',
            'Ctrl_MF_Feed_Pumps.PI_Stop_Pmps_Delay_SP',
            'Ctrl_MF_Feed_Pumps.PI_Sts_Auto',
            'Ctrl_MF_Feed_Pumps.PO_Lead_Lag_Demand_Set',
            'Ctrl_MF_Feed_Pumps.PO_LLS_Prog_Cmd',
            'Ctrl_MF_Feed_Pumps.PO_LLS_Start_Cmd',
            'Ctrl_MF_Feed_Pumps.PO_Pump_1_Speed_Cmd',
            'Ctrl_MF_Feed_Pumps.PO_Pump_2_Speed_Cmd',
            'Ctrl_MF_Feed_Pumps.PO_Pump_3_Speed_Cmd',
            'Ctrl_MF_Feed_Pumps.PO_Stop_LLS_Cmd']
    field_names = ['ts'] + tags
    # print(field_names)

    # Initialize CSV file with headers
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()

    while True:
        # Read data from PLC
        values = clx.read_multiple_tags(tags)

        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        data = dict(zip(field_names, [ts] + values))

        # Write data to CSV
        print(data)
        write_to_csv(csv_file_name, field_names, data)

        # Adjust the reading interval as needed
        time.sleep(1)


if __name__ == '__main__':
    main()
