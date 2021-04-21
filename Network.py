# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 15:33:31 2019

@author: vianney
"""
import heapq
import random
import pandas as pd
import os
import numpy as np
import myutils as mu
import collections as col
from collections import defaultdict
from heapq import *
import datetime as dt
import Station as st

folder_path = os.getcwd()
#folder_path=r"/users/home/3876914/Bureau/projet_python/v4"

class Network(object):
    """
    an object modelizing a station according to gtfs standards, node of djikstra algo.
    """
    def __init__(self, *args):
        self.dict_stations = {}
        self.dd_names = col.defaultdict(list)
        
        for end_path in args:
            file_path = os.path.join(folder_path, end_path)

            # import all datasets
            #stops
            stops = pd.read_csv(os.path.join(file_path, "stops.txt"), sep=",")
            stops = stops.drop(['stop_code', 'location_type', 'parent_station'], axis=1)
            #self.default_dict_names
            self.dd_names.update(mu.build_defaultdict_names(stops))
            this_line_dict_stations = mu.build_all_stations(stops)

            #trips
            trips = pd.read_csv(os.path.join(file_path, "trips.txt"), sep=",")
            trips = trips.drop(['trip_headsign','trip_short_name','direction_id','shape_id'], axis=1)

            #stop_times
            times = pd.read_csv(os.path.join(file_path, "stop_times.txt"), sep=",")
            times = times.drop(['arrival_time','stop_headsign','shape_dist_traveled'], axis=1)
            mu.convert_24_to_datetime(times)
            times = pd.merge(trips, times, how='right', on = ['trip_id'])
            times['duration'] = np.float('nan')
            times2=times[['trip_id','stop_sequence','stop_id','departure_time']]
            times2.loc[:,'stop_sequence'] = times2.loc[:,'stop_sequence']-1
            trui = pd.merge(times,times2, how='left', on = ['trip_id','stop_sequence'], sort=False, validate="1:1", copy=False)
            trui.duration = trui.departure_time_y - trui.departure_time_x
            trui = trui.drop(['departure_time_y', 'stop_sequence'], axis = 1)
            trui = trui.rename(index=str, columns={"stop_id_x": "stop_id", "stop_id_y": "next_stop", "departure_time_y":"departure_time"})

            #calendar
            calendar = pd.read_csv(os.path.join(file_path, "calendar.txt"), sep=",")
            calendar['start_date'] = pd.to_datetime(calendar['start_date'], format = '%Y%m%d')
            calendar['end_date'] = pd.to_datetime(calendar['end_date'], format ='%Y%m%d')
            calendar = calendar.drop(['monday','tuesday','wednesday','thursday','friday','saturday','sunday'], axis=1)

            #calendar_dates
            calendar_expt = pd.read_csv(os.path.join(file_path, "calendar_dates.txt"), sep=",")
            calendar_expt = calendar_expt.drop(['exception_type'], axis=1)
            calendar_expt['date'] = pd.to_datetime(calendar_expt['date'], format ='%Y%m%d')

#            calendar['set_of_date'] = [set([(pd.to_datetime(i)).to_pydatetime().date()
#                for i in pd.date_range(start=row.start_date, end=row.end_date, closed=None)]) 
#                for index, row in calendar.iterrows()]
            calendar['set_of_date'] = [set() for index, row in calendar.iterrows()]

            g = col.defaultdict(set)
            for index, row in calendar_expt.iterrows():
                g[row.service_id].add(row.date.to_pydatetime().date())

            for index, row in calendar.iterrows():
#                row.set_of_date.difference_update(g.get(row.service_id))
#                row.set_of_date.intersection_update(g.get(row.service_id))
                row.set_of_date.update(g.get(row.service_id))
            calendar = calendar.drop(['start_date','end_date'],axis=1)
            trui = pd.merge(trui,calendar, how='left', 
                            on = ['service_id'], sort=False,
                            validate="m:1", copy=False)

            #routes
            routes = pd.read_csv(os.path.join(file_path, "routes.txt"), sep=",")
            routes = routes.drop(['agency_id', 'route_long_name', 'route_desc', 'route_type', 'route_url', 'route_color', 'route_text_color'], axis=1)

            trui = pd.merge(trui, routes, how='left', on=['route_id'], sort=False, validate="m:1", copy=False)
            trui = trui.drop(['route_id', 'service_id' ],axis=1)
            trui = trui.rename(index=str, columns={'departure_time_x':'time','route_short_name':'line'})
            trui = trui[['stop_id','trip_id','set_of_date', 'time', 'next_stop', 'duration','line']]
            trui = trui.dropna(axis=0, how='any', subset=['next_stop','duration'])

            #transfers
            transfers = pd.read_csv(os.path.join(file_path, "transfers.txt"), sep=",")
            transfers = transfers.drop(['transfer_type'], axis=1)
            transfers = transfers.drop(transfers[(transfers.from_stop_id>9999 ) | (transfers.to_stop_id>9999)].index )
            transfers = transfers.rename(index=str, columns={'min_transfer_time':'duration'})
            transfers.duration = transfers.duration//60 +1

            #complete all the stations of the line :
            for st in this_line_dict_stations.values():
                st.add_all_trips_from_df(trui)
                st.add_all_transfers(transfers)
                st.add_transfers_opposite_quay(stops)
                st.add_neigh() #just for verif
                st.trips.time = [i.to_pydatetime().time() for i in st.trips.time]
                
            self.dict_stations.update(this_line_dict_stations)
            del(stops, trips, routes, times, times2, trui, transfers, calendar, calendar_expt, this_line_dict_stations)

    def compute_shortest_path(self, from_stop_name, to_stop_name, date_and_time):
        date = date_and_time.date()
        time = date_and_time.time()
        f = self.dd_names[from_stop_name][0]
        t = self.dd_names[to_stop_name][0]
        victoire = self.dijkstra(f,t,date, time)
        return victoire[1], victoire[0]

    
    def dijkstra(self, f, t, date, time):
    
        q, seen, mins = [(0,f,[(f,'transfer',0)])], set(), {f: 0}
        iu=0
        while q:
            iu=iu+1
            (cost,v1, lisu) = heappop(q)
            if v1 not in seen:
                seen.add(v1)
                if lisu[-1][0]!=v1:
                    lisu.append((int(v1),int(cost)))

                if v1 == t: return (cost, lisu)
                try:
                    v1_station = self.dict_stations[v1]
                except:
                    continue
                newdatetime=dt.datetime.combine(date, time) + dt.timedelta(minutes=cost)
                v1_edges = v1_station.compute_duration_to_every_neighbour(newdatetime.date(), newdatetime.time(), 
                                                                          inc_transfers = True,
                                                                          inc_line_name = True).items()
                for v2,  line_and_c in v1_edges:  #ici compute duration to every neig

                    c = line_and_c[1]
                    line = line_and_c[0]
                    if v2 in seen:
                        continue
                    prev = mins.get(v2, None)

                    next = cost + c
                    if prev is None or next < prev:
                        mins[v2] = next
                        lisu2=lisu+[(int(v2), line, int(next))]
                        heappush(q, (int(next), int(v2), lisu2))
    
        return (float("inf"),(),[])