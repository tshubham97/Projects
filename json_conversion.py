# -*- coding: utf-8 -*-

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from tkinter import *
import concurrent.futures

import pandas as pd
import pytz


def find_list_cols(df):
    """ Find all columns in a dataframe that contain list data. Columns
    must have at least one list object. Includes handling for partially
    null columns."""
    some_lists = (df.map(type) == list).any() # At least one list obj
    some_lists = some_lists[some_lists].index.to_list()
    df = df.filter(some_lists)
    list_cols = (df.isnull() | (df.map(type) == list)).all()
    return list_cols[list_cols].index.tolist()
    
def find_dict_cols(df):
    """ Find all columns in a dataframe that contain list data. Columns
    must have at least one list object. Includes handling for partially
    null columns."""
    some_dicts = (df.map(type) == dict).any() # At least one dict obj
    some_dicts = some_dicts[some_dicts].index.to_list()
    df = df.filter(some_dicts)
    dict_cols = (df.isnull() | (df.map(type) == dict)).all()
    return dict_cols[dict_cols].index.tolist()

def find_date_cols(df):
    """ Find all columns with 'Date' in the name
    """
    return list(df.filter(like="Date").columns)

def unix_to_dt(t):
    """Convert unix integer times to datetimes or dates
    """
    try:
        t = int(t)
        mdt = pytz.timezone('America/Denver')
        t = datetime.fromtimestamp(t, mdt)
        #t = t.tz_localize(tz=None) #Will this cause issues in xlsx?
        if t.hour == 0 and t.minute == 0 and t.second == 0:
            t = t.strftime('%Y-%m-%d')
    except:
        pass
    return t

def remove_tz(df: pd.DataFrame) -> pd.DataFrame:
    """ Find columns that have timezone data and convert to timezone
    naive data. This prevents issues with writing datetimes to Excel.
    """
    data_types = dict(zip(list(df.columns), list(df.dtypes)))
    tz_cols = [col for col, dtype in data_types.items() 
               if str(dtype) == 'datetime64[ns, UTC]'
               or str(dtype) == 'datetime64[ns, America/Denver]']
    if tz_cols:
        for col in tz_cols:
            df[col] = (
                pd.to_datetime(df[col], unit='s').dt.tz_localize(tz=None)
            )

    return df

def dict_to_list(col: dict):
    """Reformat a set of dictionaries into a list. This will force vertical
    data unpacking in a JSON."""
    pay_type_patt = r'(?P<payType>[a-z]*)PayAmount$'
    pay_types = []
    for k, v in col.items():
        pay_types.append(dict(re.match(pay_type_patt, k).groupdict(), **v))
    return pay_types

def flatten_col(col: pd.DataFrame):
    """Flatten one column of a dataframe. Flatten horizontally before any
    vertical expansion to prevent mismatched keys and levels between rows.
    """
    if find_dict_cols(col):
        # explode dictionaries horizontally, adding new columns
        nested_dict = find_dict_cols(col)[0]
        flattened_col = pd.json_normalize(
            col[nested_dict],
            sep="_"
            ).add_prefix(f'{nested_dict}_')
        return flattened_col
    elif find_list_cols(col):
        # explode lists vertically, adding new rows
        nested_list = find_list_cols(col)[0]
        ex_rows = col[nested_list].explode(ignore_index=True).to_frame()
        new_rows = [ex_rows.loc[row, :].to_frame().T for row in ex_rows.index]
        #Use recursion to process each row separately and then join together
        flattened_rows = list(map(flatten_nested_json_df, new_rows))
        final_rows = pd.concat(flattened_rows, axis='rows', ignore_index=True)
        return final_rows
    else:
        return col

def flatten_nested_json_df(json_df: pd.DataFrame):
    """Unpack any nested columns in a JSON dataframe. Preserves root and
    nested column ordering by transforming through mapping."""
    if not find_list_cols(json_df) and not find_dict_cols(json_df):
        return json_df
    while find_list_cols(json_df) or find_dict_cols(json_df):
        cols = [json_df.loc[:, col].to_frame() for col in json_df.columns]
        flattened_cols = list(map(flatten_col, cols))
        json_df = pd.concat(flattened_cols, axis='columns')
    return json_df


def folder_convert(file_path):

    merged_files = os.path.join(file_path, "OUT_XLSX")
    try:
        os.mkdir(merged_files)
    except FileExistsError:
        pass

    for file in os.listdir(file_path):
        if file.endswith('.json'):
            jsons = {}
            path = file_path + '/' + file
            with open(file_path + '/' + file) as fp:
                json_data = json.load(fp)
                #repack payamounts
                json_df = pd.DataFrame([json_data]) # needs list of dict input
                json_df = flatten_nested_json_df(json_df)
                for col in find_date_cols(json_df):
                    json_df[col] = json_df[col].apply(unix_to_dt)
                json_df = remove_tz(json_df)
                name = Path(path).resolve().stem # strip file extension
                jsons[name] = json_df
                for name, data in jsons.items():
                    data.to_excel(f'{file_path}/OUT_XLSX/{name}.xlsx', index=False)



def main():
    print("Running for Payroll Provider Reports")
    print("Current Time:",datetime.now().strftime("%H:%M:%S"))
    ppr_time = time.time()
    start_time = time.time()
    folder_convert(*----add the folder path----*)
    elapsed_time_voie  = time.time() - start_time
    print('Execution time for Payroll Provider Reports:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time_voie)))
