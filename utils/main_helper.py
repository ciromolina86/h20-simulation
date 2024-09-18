import csv
import os
import time
import datetime
import numpy as np
import pandas as pd
from handlers import comm_handler, signal_handler
import json


def get_data_types(file_path='tag-list-2024-09-18.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)

    data_types = []
    # for dt in [dt for dt in data
    #            if not any(char in data[dt]['data_type_name']
    #                       for char in ['BOOL', 'REAL', 'WORD', 'INT', 'FBD_', ':', 'TIMER', 'udtDateTime'])]:
    for dt in [dt for dt in data
               if any(char in data[dt]['data_type_name'] for char in ['P_']) and
                  not any(char in data[dt]['data_type_name']
                          for char in ['BOOL', 'REAL', 'WORD', 'INT', 'FBD_', ':', 'TIMER', 'udtDateTime'])]:
        data_types.append(data[dt]['data_type_name'])
    data_types = list(set(data_types))

    print(data_types)
    print(f"No of data types: {len(data_types)}")
    for data_type in data_types:
        print(f"No of {data_type} instances: "
              f"{len(get_instances(file_path='tag-list-2024-08-09.json', data_type=data_type))}")

    return data_types


def get_instances(file_path='tag-list-2024-09-18.json', data_type='P_AIn'):
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


def get_values(file_path, instance, attributes):
    with open(file_path, 'r') as file:
        data = json.load(file)

    result = []
    for key, value in data[instance].items():
        if key in attributes:
            result.append(value)

    return result


# do not use this method
def get_attributes_values(instances, attributes_file_path='attributes_setpoints.json',
                          values_file_path='attributes_setpoints_custom_values.json', data_type='P_AIn',
                          group='custom_attributes'):
    # open JSON file and load attributes into a dictionary
    with open(values_file_path, 'r') as file:
        data = json.load(file)
    attributes = get_attributes(attributes_file_path, data_type, group)
    print(attributes)
    values = [data[data_type][group][attribute] for attribute in attributes]
    print(values)

    return attributes, values


def export_setpoints(file_path):
    # open JSON file and load into a dictionary
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert JSON dictionary to a DataFrame
    df = pd.json_normalize(data).T

    # Export the DataFrame to an Excel file
    df.to_excel(f"setpoints-{time.strftime('%Y-%m-%d')}.xlsx", index=True, engine='openpyxl')
# do not use this method


def filter_setpoints(file_path, filter):
    with open(file_path, 'r') as file:
        data = json.load(file)

    result = {}
    for key, value in data.items():
        # Create a filtered dictionary for each key
        filtered_value = {k: v for k, v in value.items() if k in filter}
        result[key] = filtered_value

    return result

    # # Writing instance attributes in JSON format
    # with open(f"{file_path}_filtered.json", 'w') as file:
    #     json.dump(result, file, indent=4)


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


def write_setpoints(plc, instance, attributes, values):
    print(instance)
    plc.write_multiple_tags([f'{instance}.{attribute}' for attribute in attributes], values)
    time.sleep(0.3)


def p_ain_helper(clx):
    # get a list of all the P_AIn instances
    instances = get_instances('tag-list-2024-09-18.json', data_type='P_AIn')
    # print(instances)

    attributes = get_attributes(file_path='attributes_setpoints.json', data_type='P_AIn', group='custom_attributes')
    attributes = attributes + [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                               for attribute in get_attributes('attributes_setpoints.json',
                                                               data_type='P_Alarm',
                                                               group='custom_attributes')]
    # print(attributes)

    for instance in instances:
        values = get_values('setpoints-3-2024-08-09.json', instance, attributes)
        # print(values)
        write_setpoints(clx, instance, attributes, values)

    if False:  # if you want writing functions to run manually change to True, if not change to False
        # get a list of all the attributes and values for the common values that do not change between instances
        attributes, values = get_attributes_values(instances=instances,
                                                   attributes_file_path='attributes_setpoints.json',
                                                   values_file_path='attributes_setpoints_custom_values.json',
                                                   data_type='P_AIn',
                                                   group='custom_attributes')
        # attributes_alarm, values_alarm = get_attributes_values('attributes_setpoints_custom_values.json', 'P_Alarm')
        #
        # # adding the P_Alarm setpoint attributes
        # attributes_alarm = [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
        #                     for attribute in attributes_alarm]
        # attributes = attributes + attributes_alarm
        # values = values + values_alarm * 5

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

    if False:  # if you want attributes filtering functions to run manually change to True, if not change to False
        custom_attributes = get_attributes('attributes_setpoints.json', data_type='P_AIn', group='custom_attributes')
        custom_attributes = custom_attributes + \
                            [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                             for attribute in get_attributes('attributes_setpoints.json', data_type='P_Alarm',
                                                             group='custom_attributes')]
        filter_setpoints('setpoints-3-2024-08-09.json', custom_attributes)


def main():
    print('Creating PLC object!!!')
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    print('Running analog objects helper!!!')
    p_ain_helper(clx)

    # with open('tag-list-2024-08-09.json', 'r') as file:
    #     data = json.load(file)

    # df = pd.DataFrame({"attributes": data['LIT_15_11']['data_type']['attributes'],
    #                    "Faceplate": ['' for x in data['LIT_15_11']['data_type']['attributes']],
    #                    "Alarm": ['' for x in data['LIT_15_11']['data_type']['attributes']],
    #                    "Trend": ['' for x in data['LIT_15_11']['data_type']['attributes']]})
    # print(df.head(5))
    # df.to_excel('P_AIn attributes.xlsx')

    # df = pd.DataFrame({"attributes": data['PMP_15_11']['data_type']['attributes'],
    #                    "Faceplate": ['' for x in data['PMP_15_11']['data_type']['attributes']],
    #                    "Alarm": ['' for x in data['PMP_15_11']['data_type']['attributes']],
    #                    "Trend": ['' for x in data['PMP_15_11']['data_type']['attributes']]})
    # print(df.head(5))
    # df.to_excel('P_VSD attributes.xlsx')

    # df = pd.DataFrame({"attributes": data['CMP_30_61']['data_type']['attributes'],
    #                    "Faceplate": ['' for x in data['CMP_30_61']['data_type']['attributes']],
    #                    "Alarm": ['' for x in data['CMP_30_61']['data_type']['attributes']],
    #                    "Trend": ['' for x in data['CMP_30_61']['data_type']['attributes']]})
    # print(df.head(5))
    # df.to_excel('P_Motor attributes.xlsx')

    # df = pd.DataFrame({"attributes": data['VBF_70_27']['data_type']['attributes'],
    #                    "Faceplate": ['' for x in data['VBF_70_27']['data_type']['attributes']],
    #                    "Alarm": ['' for x in data['VBF_70_27']['data_type']['attributes']],
    #                    "Trend": ['' for x in data['VBF_70_27']['data_type']['attributes']]})
    # print(df.head(5))
    # df.to_excel('P_ValveC attributes.xlsx')

    # df = pd.DataFrame({"attributes": data['FC_70_51']['data_type']['attributes'],
    #                    "Faceplate": ['' for x in data['FC_70_51']['data_type']['attributes']],
    #                    "Alarm": ['' for x in data['FC_70_51']['data_type']['attributes']],
    #                    "Trend": ['' for x in data['FC_70_51']['data_type']['attributes']]})
    # print(df.head(5))
    # df.to_excel('P_AOut attributes.xlsx')


if __name__ == '__main__':
    main()
