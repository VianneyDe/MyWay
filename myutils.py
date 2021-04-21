# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:11:08 2019

@author: vianney
"""

import pandas as pd
import os
import numpy as np
import pdb
import Station as st
import datetime
import collections as col

def convert_24_to_datetime(df):
    a=df['departure_time'].str.extract(r'(?P<hour>\d{2}):(?P<minute>\d{2})')
    a['hour']=a['hour'].apply(int)%24
    a['hour']=a['hour'].apply(str)
    a['instr']=a['hour']+':'+a['minute']+":00"
    a['instr']=pd.to_datetime(a['instr'],format='%H:%M:%S')
    df['departure_time']=a['instr']

def build_all_stations(df_stops):
    # takes all items of the stopID dataset to build stations
    # df_trips à filtrer à 0;+5h ensuite pour ne pas alourdir.
    l = {}
    for index, row in df_stops.iterrows():
        newstation = st.Station(row['stop_id'], row['stop_name'], row['stop_desc'], row['stop_lat'], row['stop_lon'])
        l[row.stop_id] = newstation
    return l

def build_defaultdict_names(stops):
    d = col.defaultdict(list)
    stops_red=stops[['stop_id','stop_name']]
    for index, row in stops_red.iterrows():
        d[row.stop_name].append(row.stop_id)
    return d