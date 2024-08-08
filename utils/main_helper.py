import csv
import os
import time
import datetime
import numpy as np
import pandas as pd
from handlers import comm_handler, signal_handler
import json


def get_instances(file_path, data_type='P_AIn'):
    instances = []
    # open JSON file and load instances into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    for tag in data:
        if data[tag]['data_type_name'] == data_type:
            instances.append(tag)

    return instances


def get_attributes(file_path, data_type='P_AIn'):
    # open JSON file and load attributes into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    # filter attributes by data type
    return data[data_type]['attributes'][0] + data[data_type]['attributes'][1]


def get_std_cfg_values(file_path, data_type='P_AIn'):
    # open JSON file and load attributes into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    attributes = list(data[data_type]['attributes'].keys())
    values = [data[data_type]['attributes'][attribute] for attribute in attributes]

    return attributes, values


def read_setpoints(plc, instances, attributes):
    data = {}

    for instance in instances:
        # Create a dictionary for the current instance
        instance_dict = {}
        values = plc.read_multiple_tags([f'{instance}.{attribute}' for attribute in attributes])

        for attribute, value in zip(attributes, values):
            # Get the attribute value from the instance and add it to the instance_dict
            instance_dict[attribute] = getattr(instance, attribute, value)

        # Add the instance_dict to the result dictionary using the instance as the key
        data[instance] = instance_dict

        # Writing instance attributes in JSON format
        with open(f"setpoints-{time.strftime('%Y-%m-%d')}.json", 'w') as file:
            json.dump(data, file, indent=4)

        time.sleep(3)

    return data


def write_setpoints(plc, instances, attributes, values):
    for instance in instances:
        plc.write_multiple_tags([f'{instance}.{attribute}' for attribute in attributes], values)

        time.sleep(3)


def export_setpoints(file_path):
    # open JSON file and load into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert JSON dictionary to a DataFrame
    df = pd.json_normalize(data).T

    # Export the DataFrame to an Excel file
    df.to_excel(f"setpoints-{time.strftime('%Y-%m-%d')}.xlsx", index=True, engine='openpyxl')


def main():
    # Create PLC object
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')

    instances = get_instances('tag-list-2024-08-08.json', data_type='P_AIn')
    # attributes = get_attributes('attributes_config.json', data_type='P_AIn')
    # read_setpoints(clx, instances[:3], attributes)
    # print(instances)
    # print(len(instances))
    # print(instances.index('PIT_40_11B'))

    # export_setpoints('setpoints-2024-08-07.json')

    attributes, values = get_std_cfg_values('p_ain_std_cfg.json')
    write_setpoints(clx, instances, attributes, values)


if __name__ == '__main__':
    main()
