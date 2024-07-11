import pandas as pd
import numpy as np
import os


def main():
    # read excel with instance data
    df = pd.read_excel('C:\\Users\\cmolina\\Downloads\\book1.xlsx')

    # read data to create udt
    symbolic_address = df.iloc[:, 0]
    data_type = df.iloc[:, 2]
    description = df.iloc[:, 4]

    # open the text file in write mode
    with open('output.udt', 'w') as file:
        # write header of file
        file.write(f'TYPE "SCADA_Read_Train"\nVERSION : 0.1\n\tSTRUCT\n')

        # Iterate over the rows and write the data to the text file
        for symbolic_address, data_type, description in zip(symbolic_address, data_type, description):
            file.write(f"\t\t{str(symbolic_address).split('.')[1]} : {data_type};  // {description}\n")
            pass

        # write footer of file
        file.write(f'\tEND_STRUCT;\n\nEND_TYPE')


if __name__ == '__main__':
    main()
