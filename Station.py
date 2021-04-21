# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:33:31 2019

@author: vianney
"""

import random
import pandas as pd
import os
import numpy as np
import datetime as dt

file_path = r"/Users/chengyuwang/Documents/IMPE/projet_python/v5/RATP_GTFS_METRO_10"

class Station(object):
    """
    an object modelizing a station according to gtfs standards, node of djikstra algo.
    """
    def __init__(self, stop_id=0, stop_name='', stop_desc='', stop_lat=0, stop_lon=0):
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.stop_desc = stop_desc
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.neighbourg = set()
        self.transfers = {}
#        self.trips=pd.DataFrame(columns=['trip_id','set_of_date','time','next_stop','duration'])
        self.trips=pd.DataFrame(columns=['stop_id', 'trip_id', 'set_of_date', 'time', 'next_stop', 'duration', 'line'])

    def add_trip(self,trip_id,set_of_date,time,next_stop,duration):
        newrow = pd.DataFrame([[0,trip_id, set_of_date,time, next_stop,duration,0]],
                                columns=['stop_id', 'trip_id', 'set_of_date', 'time', 'next_stop', 'duration', 'line'])
        self.trips=self.trips.append(newrow, ignore_index=True)

    def add_all_trips_from_df(self, trui):
        self.trips = trui.loc[trui.stop_id==self.stop_id,:]
        
    def add_all_transfers(self, transfers):
        subdf = transfers.loc[transfers.from_stop_id==self.stop_id,:]#.drop(['from_stop_id'],axis=1)
        for  index, row in subdf.iterrows():
            self.transfers[row.to_stop_id]=('transfer',row.duration)
        #add return transfer if any
        subdf = transfers.loc[transfers.to_stop_id==self.stop_id,:]#.drop(['to_stop_id'],axis=1
        for  index, row in subdf.iterrows():
            self.transfers[row.from_stop_id]=('transfer',row.duration)
            
    def add_transfers_opposite_quay(self, stops):
        mdf = stops[(stops.stop_name==self.stop_name) & (stops.stop_id!=self.stop_id)]
        for index, row in mdf.iterrows():
            self.transfers[row.stop_id]=('transfer',0)
    
    def add_neigh(self):
        self.neighbourg = set(self.trips.next_stop)
        self.neighbourg = self.neighbourg.union(set(self.transfers.keys()))
        
    
    def compute_duration_to_every_neighbour(self, date, time, inc_transfers = False, inc_line_name = False):
        self.neighbourg = set(self.trips.next_stop)
        usefull_trips = self.trips
        if inc_transfers:
            #self.neighbourg = self.neighbourg.union(set(self.transfers.keys()))
            l=self.transfers
        else:
            l={}
        
        for neig in self.neighbourg:
            subset_trips0 = usefull_trips[(usefull_trips.next_stop==neig) ]
            mask = [(date in subset_trips0.set_of_date[i]) for i in subset_trips0.index]          
            subset_trips = subset_trips0[mask]
            subset_trips = subset_trips[subset_trips.time >= time]    
            d_incr = 0

            while len(subset_trips)==0 and d_incr < 10:
                d_incr = d_incr + 1
                mask = [((date + dt.timedelta(d_incr)) in subset_trips0.set_of_date[i]) for i in subset_trips0.index]
                subset_trips = subset_trips0[mask]
                
            if len(subset_trips)!=0:
                min_time = min(subset_trips.time)
                next_trip_to_neig = subset_trips[subset_trips.time==min_time].iloc[0,:]
                next_trip_time = min_time
                next_trip_duration = pd.to_timedelta(next_trip_to_neig.duration)
                total_duration = (dt.datetime.combine(date + dt.timedelta(d_incr),next_trip_time)+ next_trip_duration -
                                   dt.datetime.combine(date ,time))
                if inc_line_name:
                    l[neig] = (str(next_trip_to_neig.line), total_duration.total_seconds()//60)
                else:
                    l[neig] = total_duration.total_seconds()//60
        if l != {} :
            return l
        else :
            return None
