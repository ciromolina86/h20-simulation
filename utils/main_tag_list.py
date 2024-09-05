import csv
import os
import time
import datetime
import numpy as np
import pandas as pd
from handlers import comm_handler, signal_handler
import json


def get_attributes(s):
    return s.data_type['attributes']


def get_tag_type(file_path, tag_type='struct'):
    # Open tag list JSON file and load its contents into a dictionary
    with open(file_path, 'r') as file:
        _tags = json.load(file)

    _tags_df = pd.DataFrame(_tags)
    _tags_df2 = _tags_df.transpose()

    if tag_type == 'atomic':
        tags_df = _tags_df2.where(_tags_df2['tag_type'] == 'atomic')
        return tags_df.dropna(how='all')  # .to_excel('tags_atomic.xlsx')
    if tag_type == 'struct':
        tags_df = _tags_df2.where(_tags_df2['tag_type'] == 'struct')
        return tags_df.dropna(how='all')  # .to_excel('tags_struct.xlsx')


def get_data_type(tags_df, data_type='P_AIn'):
    if data_type == 'P_AIn':
        tags_df_filtered = tags_df.where(tags_df['data_type_name'] == 'P_AIn')
        return tags_df_filtered.dropna(how='all')  # ['tag_name', 'data_type_name', 'data_type']
    if data_type == 'P_VSD':
        tags_df_filtered = tags_df.where(tags_df['data_type_name'] == 'P_VSD')
        return tags_df_filtered.dropna(how='all')  # ['tag_name', 'data_type_name', 'data_type']


def insert_attributes(tags_df_filtered):
    new_df = pd.DataFrame(tags_df_filtered['tag_name'])

    for index, row in tags_df_filtered.iterrows():
        temp_dict = {}
        temp_dict.update({'attributes': get_attributes(row)})
        temp_df = pd.DataFrame(temp_dict)
        new_df = new_df.merge(temp_df, how='cross')
        break

    tags_df_filtered = tags_df_filtered[['tag_name', 'data_type_name']]
    print(tags_df_filtered.shape)
    tags_df_filtered = tags_df_filtered.merge(new_df, on='tag_name', how='left')
    print(tags_df_filtered.shape)

    return tags_df_filtered


def get_tag_list(clx):
    # Read tags from PLC
    data = clx.get_tag_list_json()

    # Writing tag list in JSON format
    with open(f"tag-list-{time.strftime('%Y-%m-%d')}.json", 'w') as file:
        json.dump(data, file, indent=4)

    return json.dumps(data, indent=4)


def get_plc_info(clx):
    # Read PLC info
    data = clx.get_plc_info()
    data['status'] = data['status'].decode('utf-8')

    # Writing PLC info in JSON format
    with open(f"plc-info-{time.strftime('%Y-%m-%d')}.json", 'w') as file:
        json.dump(data, file, indent=4)

    return json.dumps(data, indent=4)


def testing_writing_setpoint(plc):
    plc.write_multiple_tags(['LIT_15_11.Cfg_EU', 'LIT_15_11.Cfg_Tag', 'LIT_15_11.Cfg_Label', 'LIT_15_11.Cfg_Desc'],
                            ['feet', 'LIT_15_11', 'LIT-15-11', 'Sanitary Lift Station Level'])


def testing_reading_setpoints(plc):
    return plc.read_multiple_tags(['LIT_15_11.Cfg_EU', 'LIT_15_11.Cfg_Tag', 'LIT_15_11.Cfg_Label', 'LIT_15_11.Cfg_Desc'])


def main():
    # Create PLC object
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    # print(testing_reading_setpoints(clx))
    # testing_writing_setpoint(clx)
    # print(testing_reading_setpoints(clx))
    # return None

    # Read data from PLC and write to json files
    # get_plc_info(clx)
    # get_tag_list(clx)

    # Parse tag list read from PLC and filter data type of interest
    # tag_list_atomic = get_tag_type(file_path='tag-list-2024-08-07.json', tag_type='atomic')

    # Parse tag list read from PLC and filter data type of interest
    # tag_list_struct = get_tag_type(file_path='tag-list-2024-08-07.json', tag_type='struct')
    # print(tag_list_struct['data_type_name'].unique())
    # tag_list_p_ain = get_data_type(tags_df=tag_list_struct, data_type='P_AIn')
    # tag_list_p_ain_with_attributes = insert_attributes(tag_list_p_ain)
    # tag_list_p_ain_with_attributes.to_excel('tag_list_p_ain_with_attributes.xlsx')


if __name__ == '__main__':
    main()
