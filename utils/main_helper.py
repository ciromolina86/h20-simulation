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

    if False:  # if you want attributes filtering functions to run manually change to True, if not change to False
        custom_attributes = get_attributes('attributes_setpoints.json', data_type='P_AIn', group='custom_attributes')
        custom_attributes = custom_attributes + \
                            [f"{alarm}.{attribute}" for alarm in ['HiHi', 'Hi', 'Lo', 'LoLo', 'Fail']
                             for attribute in get_attributes('attributes_setpoints.json', data_type='P_Alarm',
                                                             group='custom_attributes')]
        filter_setpoints('setpoints-3-2024-08-09.json', custom_attributes)

    return instances


def get_data_types(file_path='tag-list-2024-08-09.json'):
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


def scada_tags():
    instances = get_instances(data_type='P_ValveSO')
    # print(instances)
    df = pd.read_csv('database TagSourceHeader.csv')
    # print(df)

    '''#AssetHeader,Asset Name,Description,Asset Type Name,Parent Asset Name,Asset Type Template,'''
    for instance in instances:
        new_row = df.loc[5]
        new_row['Asset Name'] = instance
        df.loc[len(df)] = new_row
    df.to_csv('AssetHeader P_Motor.csv', index=False)

    '''#AssetSubstituteParameters,ParameterName,AssetName,AssetTemplate,AssetType,ParamterValue,'''
    for instance in instances:
        new_row = df.loc[2]
        new_row['AssetName'] = new_row['ParamterValue'] = instance
        df.loc[len(df)] = new_row
    df.to_csv('AssetSubstituteParameters P_ValveSO.csv', index=False)

    '''#TagSourceHeader,Parent Asset Name,Property Name,RealtimeServerAlias,RealtimeDataSourceName (iFix tag Id),HistoricalServerAlias,HistoricalDataSourceName,'''
    for instance in instances:
        rows_to_copy = df[df['Parent Asset Name'] == 'Test_P_ValveSO'].copy()
        rows_to_copy['Parent Asset Name'] = rows_to_copy['Parent Asset Name'].apply(
            lambda x: x.replace('Test_P_ValveSO', instance))
        rows_to_copy['RealtimeDataSourceName (iFix tag Id)'] = rows_to_copy[
            'RealtimeDataSourceName (iFix tag Id)'].apply(lambda x: x.replace('Test_P_ValveSO', instance))
        rows_to_copy['HistoricalDataSourceName'] = rows_to_copy['HistoricalDataSourceName'].apply(lambda x: str(x))
        rows_to_copy['HistoricalDataSourceName'] = rows_to_copy['HistoricalDataSourceName'].apply(
            lambda x: x.replace('Test_P_ValveSO', instance))
        df = pd.concat([df, rows_to_copy], ignore_index=True)

    df.to_csv('TagSourceHeader P_ValveSO.csv', index=False)

    # print(df.shape)


def scada_tag_groups():
    instances = get_instances(file_path='tag-list-2024-08-09.json', data_type='P_AOut')
    # print(instances)

    for instance in instances:
        with open(f'TGD_{instance}.csv', 'w') as file:
            file.write(f'"1"\n')
            file.write(f'"EquipmentName","{instance}",""')


def main():
    # Create PLC object
    # clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    # get_data_types(file_path='tag-list-2024-08-09.json')
    # p_ain_helper(clx)

    with open('tag-list-2024-08-09.json', 'r') as file:
        data = json.load(file)

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
    scada_tags()
    scada_tag_groups()
