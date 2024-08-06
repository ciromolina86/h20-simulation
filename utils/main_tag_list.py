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
        _atomic_tags = _tags_df2.where(_tags_df2['tag_type'] == 'atomic')
        return _atomic_tags.dropna(how='all')  # .to_excel('tags_atomic.xlsx')
    if tag_type == 'struct':
        _struct_tags = _tags_df2.where(_tags_df2['tag_type'] == 'struct')
        return _struct_tags.dropna(how='all')  # .to_excel('tags_struct.xlsx')


def get_data_type(tags_df, data_type='P_AIn'):
    if data_type == 'P_AIn':
        tags_df_filtered = tags_df.where(tags_df['data_type_name'] == 'P_AIn')

    _p_ain_tags_short = tags_df_filtered[['tag_name', 'data_type_name', 'data_type']].dropna(how='all')

    new_df = pd.DataFrame(_p_ain_tags_short['tag_name'])

    for index, row in _p_ain_tags_short.iterrows():
        temp_dict = {}
        temp_dict.update({'attributes': get_attributes(row)})
        temp_df = pd.DataFrame(temp_dict)
        new_df = new_df.merge(temp_df, how='cross')
        break

    _p_ain_tags_short = _p_ain_tags_short[['tag_name', 'data_type_name']]
    print(_p_ain_tags_short.shape)
    _p_ain_tags_short = _p_ain_tags_short.merge(new_df, on='tag_name', how='left')
    print(_p_ain_tags_short.shape)
    # _p_ain_tags_short.to_excel('tags_P_AIn.xlsx')

    return _p_ain_tags_short


def get_tag_list():
    pass
    # tag_list = f"tag_list-{time.strftime('%Y-%m-%d-%H-%M')}.txt"

    # with open(tag_list, mode='w', newline='') as file:
    #     file.write(str(clx.get_tag_list_json()))


def main():
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    print(clx.get_plc_info())

    # read tag list from PLC
    # tag_list_json = json.loads(str(clx.get_tag_list_json()).replace("'", '"'))
    tag_list_data = json.dumps(clx.get_tag_list_json())

    # Writing tag list in JSON format
    with open(f"tag-list-{time.strftime('%Y-%m-%d-%H-%M')}.json", 'w') as file:
        json.dump(tag_list_data, file)

    structs = get_structs()
    p_ains = get_p_ain(structs)


if __name__ == '__main__':
    main()
