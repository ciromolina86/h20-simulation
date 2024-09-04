from utils.main_helper import get_instances
import pandas as pd


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


if __name__ == '__main__':
    scada_tags()
