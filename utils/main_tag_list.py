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


def get_structs():
    # Create PLC object and print PLC info
    clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    print(clx.get_plc_info())
    # _tags = json.loads(str(clx.get_tag_list_json()).replace("'", '"'))

    _tags = clx.get_tag_list_json()
    _tags_df = pd.DataFrame(_tags)
    _tags_df2 = _tags_df.transpose()

    _atomic_tags = _tags_df2.where(_tags_df2['tag_type'] == 'atomic')
    # _atomic_tags = _atomic_tags.dropna(how='all').to_excel('tags_atomic.xlsx')

    _struct_tags = _tags_df2.where(_tags_df2['tag_type'] == 'struct')
    # _struct_tags = _struct_tags.dropna(how='all').to_excel('tags_struct.xlsx')

    return _struct_tags


def get_p_ain(_struct_tags):
    _p_ain_tags = _struct_tags.where(_struct_tags['data_type_name'] == 'P_AIn')
    _p_ain_tags_short = _p_ain_tags[['tag_name', 'data_type_name', 'data_type']].dropna(how='all')

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
    structs = get_structs()
    p_ains = get_p_ain(structs)


if __name__ == '__main__':
    main()
