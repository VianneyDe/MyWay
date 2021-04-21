#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:10:14 2019

@author: 3876914
"""
import pandas as pd



parcours.duration=r.compute_shortest_path()
Lon=[]
Lat=[]
For i in parcours:
    Lon.append(r.dict_station[i[0]].stop_lon)
    Lat.append(r.dict_station[i[0]].stop_lat)
return Lon,Lat

