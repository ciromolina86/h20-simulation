import csv
import os
import time
import datetime
import numpy as np
import pandas as pd
from handlers import comm_handler, signal_handler
import json


def get_instances(file_path='tag-list-2024-08-09.json', data_type='P_AIn'):
    instances = []
    # open JSON file and load instances into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    for tag in data:
        if data[tag]['data_type_name'] == data_type:
            instances.append(tag)

    return instances


def get_attributes(file_path='attributes_setpoints.json', data_type='P_AIn', group='all_attributes'):
    # open JSON file and load attributes into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    # filter attributes by data type
    return data[data_type][group]


def get_common_values(file_path='attributes_setpoints_common_values.json', data_type='P_AIn'):
    # open JSON file and load attributes into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    attributes = list(data[data_type]['attributes'].keys())
    values = [data[data_type]['attributes'][attribute] for attribute in attributes]

    return attributes, values


def read_setpoints(plc, instances, attributes):
    data = {}

    for instance in instances:
        print(instance)
        # Create a dictionary for the current instance
        instance_dict = {}
        values = plc.read_multiple_tags([f'{instance}.{attribute}' for attribute in attributes])

        for attribute, value in zip(attributes, values):
            # Get the attribute value from the instance and add it to the instance_dict
            instance_dict[attribute] = getattr(instance, attribute, value)

        # Add the instance_dict to the result dictionary using the instance as the key
        data[instance] = instance_dict

        # Writing instance attributes in JSON format
        with open(f"setpoints-1-{time.strftime('%Y-%m-%d')}.json", 'w') as file:
            json.dump(data, file, indent=4)

        time.sleep(1)

    return data


def write_setpoints(plc, instances, attributes, values):
    for instance in instances:
        print(instance)
        plc.write_multiple_tags([f'{instance}.{attribute}' for attribute in attributes], values)
        time.sleep(1)


def export_setpoints(file_path):
    # open JSON file and load into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert JSON dictionary to a DataFrame
    df = pd.json_normalize(data).T

    # Export the DataFrame to an Excel file
    df.to_excel(f"setpoints-{time.strftime('%Y-%m-%d')}.xlsx", index=True, engine='openpyxl')


def filter_setpoints(file_path, filter):
    with open(file_path, 'r') as file:
        data = json.load(file)

    result = {}
    for key, value in data.items():
        # Create a filtered dictionary for each key
        filtered_value = {k: v for k, v in value.items() if k in filter}
        result[key] = filtered_value

    # Writing instance attributes in JSON format
    with open(f"{file_path}_filtered.json", 'w') as file:
        json.dump(result, file, indent=4)


def p_ain_helper(clx):
    # get a list of all the P_AIn instances
    instances = get_instances('tag-list-2024-08-09.json', data_type='P_AIn')

    if False:  # if you want writing functions to run manually change to True, if not change to False
        # get a list of all the attributes and values for the common values that do not change between instances
        attributes, values = get_common_values('attributes_setpoints_common_values.json', 'P_AIn')
        attributes_alarm, values_alarm = get_common_values('attributes_setpoints_common_values.json', 'P_Alarm')

        # adding the P_Alarm setpoint attributes
        attributes_alarm = [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                            for attribute in attributes_alarm]
        attributes = attributes + attributes_alarm
        values = values + values_alarm * 5

        # write all the common setpoint attributes to all the P_AIn instances
        write_setpoints(clx, instances, attributes, values)
        # if it fails before finishing, use the instance where it failed as a starting point to continue
        # write_setpoints(clx, instances[instances.index('FIT_40_14'):], attributes, values)

    if False:  # if you want reading functions to run manually change to True, if not change to False
        # get a list of all the setpoint attributes for P_Ain instances
        attributes = get_attributes('attributes_setpoints.json', data_type='P_AIn')

        # adding the P_Alarm setpoint attributes
        attributes_alarm = [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                            for attribute in get_attributes('attributes_setpoints.json', data_type='P_Alarm')]
        attributes = attributes + attributes_alarm

        # read all the setpoint attributes to all the P_AIn instances
        read_setpoints(clx, instances[:], attributes)
        # if it fails before finishing, use the instance where it failed as a starting point to continue
        # read_setpoints(clx, instances[instances.index('AIT_70_31H'):], attributes)

        # if you want to export json as an excel file uncomment this line
        # export_setpoints('setpoints-2024-08-07.json')

    if True:  # if you want attributes filtering functions to run manually change to True, if not change to False
        custom_attributes = get_attributes('attributes_setpoints.json', data_type='P_AIn', group='custom_attributes')
        custom_attributes = custom_attributes + \
                            [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                             for attribute in get_attributes('attributes_setpoints.json', data_type='P_Alarm',
                                                             group='custom_attributes')]
        filter_setpoints('setpoints-3-2024-08-09.json', custom_attributes)


def main():
    # Create PLC object
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    p_ain_helper(clx)


if __name__ == '__main__':
    main()
