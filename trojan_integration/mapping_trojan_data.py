import json
import time
import csv
from handlers import comm_handler

def get_tag_list(clx):
    # Read tags from PLC
    data = clx.get_tag_list_json()

    # Writing tag list in JSON format
    with open(f"tag-list-{time.strftime('%Y-%m-%d')}.json", 'w') as file:
        json.dump(data, file, indent=4)

    return json.dumps(data, indent=4)

def main():
    # clx = comm_handler.CLX_Manager(ip_address='192.168.60.80')
    # get_tag_list(clx)

    with open('trojan.json', 'r') as file:
        data = json.load(file)

    print(len(data['Trojan_UV']['data_type']['internal_tags'].keys()))
    for k in data['Trojan_UV']['data_type']['internal_tags'].keys():
        if data['Trojan_UV']['data_type']['internal_tags'][k]['data_type'] == 'BOOL':
            print(f'Read_Boolean(Read_Boolean_1,0,PLX31_EIP_PND:I1.Data); Trojan_UV.{k} := Read_Boolean_1.Output_Bit_0;')
        elif data['Trojan_UV']['data_type']['internal_tags'][k]['data_type'] == 'INT':
            print(f'Read_Integer(Read_Integer_1,6,PLX31_EIP_PND:I1.Data); Trojan_UV.{k} := Read_Integer_1.Output;')
        elif data['Trojan_UV']['data_type']['internal_tags'][k]['data_type'] == 'DINT':
            print(f'Read_DInt(Read_DInt_1,2,PLX31_EIP_PND:I1.Data); Trojan_UV.{k} := Read_DInt_1.Output;')
        elif data['Trojan_UV']['data_type']['internal_tags'][k]['data_type'] == 'REAL':
            print(f'Read_Real(Read_Real_1,2,PLX31_EIP_PND:I1.Data); Trojan_UV.{k} := Read_Real_1.Output;')

    # csv_file_name = f"mapping-trojan-data.txt"
    # tags = 'Trojan_UV'
    # # print(field_names)
    #
    # # Initialize CSV file with headers
    # with open(csv_file_name, mode='w', newline='') as file:
    #     writer = csv.DictWriter(file, fieldnames=tags)
    #     writer.writeheader()
    #
    # while True:
    #     # Read data from PLC
    #     values = clx.read_single_tag(tags)
    #
    #     ts = time.strftime('%Y-%m-%d %H:%M:%S')
    #     data = dict(zip(tags, values))
    #
    #     # Write data to CSV
    #     print(data)
    #     # write_to_csv(csv_file_name, tags, data)
    #
    #     # Adjust the reading interval as needed
    #     time.sleep(1)


if __name__ == '__main__':
    main()
