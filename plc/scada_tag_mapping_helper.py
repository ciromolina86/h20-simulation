from utils.main_helper import get_instances


def scada_read_mapping(instances):
    with open('read_mapping_template.txt', 'r') as file:
        data = file.read()

    new_data = ''
    for instance in instances:
        temp = data.replace('VFD_15_11', instance)
        temp = data.replace('PMP_15_11', instance)
        temp = temp.replace('OSRI35', f'One_Shot_1_{instance}')
        temp = temp.replace('OSFI35', f'One_Shot_2_{instance}')
        temp = temp.replace('OSRI38', f'One_Shot_3_{instance}')
        temp = temp.replace('OSRI37', f'One_Shot_4_{instance}')
        temp = temp.replace('OSRI36', f'One_Shot_5_{instance}')
        temp = temp.replace('OSFI36', f'One_Shot_6_{instance}')

        new_data = new_data + temp + '\n\n'

    # print(new_data)

    with open('read_mapping_all.txt', 'w') as file:
        file.write(new_data)


def scada_write_mapping(instances):
    with open('write_mapping_template.txt', 'r') as file:
        data = file.read()

    new_data = ''
    for instance in instances:
        temp = data.replace('VFD_15_11', instance)
        temp = temp.replace('PMP_15_11', instance)
        new_data = new_data + temp + '\n\n'

    # print(new_data)

    with open('write_mapping_all.txt', 'w') as file:
        file.write(new_data)


if __name__ == '__main__':
    instances = get_instances(
        file_path='C:/Users/cmolina/PycharmProjects/h20-simulation/utils/tag-list-2024-09-18.json',
        data_type='P_VSD')
    print(f'{len(instances)}: {instances} \n')

    print(f'Generating PLC Code for SCADA Read Routine')
    scada_read_mapping(instances)

    print(f'Generating PLC Code for SCADA Write Routine')
    scada_write_mapping(instances)
