from utils.main_helper import get_instances


def scada_read_mapping(instances):

    with open('read_mapping.txt', 'r') as file:
        data = file.read()

    new_data = '\n\n'
    for instance in instances:
        temp = data.replace('VFD_15_11', instance)
        new_data = new_data + temp

    print(new_data)


if __name__ == '__main__':
    instances = get_instances(file_path='C:/Users/cmolina/PycharmProjects/h20-simulation/utils/tag-list-2024-09-18.json', data_type='P_VSD')
    print(f'{len(instances)}: {instances} \n')

    print(f'Generating PLC Code for SCADA Read Routine')
    scada_read_mapping(instances)
