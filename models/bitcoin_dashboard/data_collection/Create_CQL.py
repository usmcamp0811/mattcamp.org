from functools import reduce
# from tqdm import tqdm
import pandas as pd
import sys, traceback, logging


def row_to_insert(row):
    new_row = []
    for i in row:
        if type(i) is str:
            i = i.replace("'","''")
            i = "'" + i + "'"
            new_row.append(i)
        else:
            new_row.append(i)
    return reduce(lambda x, y : x + ', ' + y, map(str, new_row))

def create_table_cql(df, PK, CASSANDRA_DB, CASSANDRA_TABLE):
    ''' 
    Creates CQL create table code for any dataframe.
    :param df: dataframe that resembles the table to be created
    :param PK: list of primary keys
    :param CASSANDRA_DB: the keyspace to be used
    :param CASSANDRA_TABLE: the talbe to be used
    '''
    # TODO: Add more dtypes
    dtype_convert = {'int64':'int', 'float64':'float', 'object':'text', 'datetime64[ns]':'text'}
    
    cols = list(df.columns)

    colstring = []

    for c in cols:
        colstring.append(str(c) + ' ' + str(dtype_convert[str(df[c].dtype)]))
    colstring = ', '.join(colstring)
    PK = ', '.join(PK)

    create = "CREATE TABLE IF NOT EXISTS {}.{}({}, PRIMARY KEY ({}));".format(CASSANDRA_DB, CASSANDRA_TABLE, colstring, PK)
    return create


def insert_row_into_cql(df, row_num, CASSANDRA_DB, CASSANDRA_TABLE):
    c = list(df.columns)
    cols = []
    row = []
    for i in range(df.shape[1]):
        jj = df.iloc[row_num, i]
        if pd.isnull(jj):
            pass
        else:
            row.append(jj)
            cols.append(c[i])

    cols = ', '.join(cols)
    insert = "INSERT INTO {}.{}({}) VALUES({});".format(CASSANDRA_DB, CASSANDRA_TABLE, cols, row_to_insert(row))
    return insert

def df2cassandra(df, CASSANDRA_DB, CASSANDRA_TABLE, PK=None, session=None, create_table=False):
    if session == None:
        print('Please provide a Cassandra session...')
    if create_table == True:
        session.execute(create_table_cql(df, PK, CASSANDRA_DB, CASSANDRA_TABLE))
    try:
        for i in range(df.shape[0]):
            session.execute(insert_row_into_cql(df, i, CASSANDRA_DB, CASSANDRA_TABLE))
    except Exception as e:
        print("Error at record {}".format(i))
        print("The CQL statement that caused the error:")
        print(insert_row_into_cql(df, i, CASSANDRA_DB, CASSANDRA_TABLE))
        print(e)



