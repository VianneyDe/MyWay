#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 00:40:28 2019

@author: chengyuwang
"""

import folium
import os
import webbrowser
import Network

def create_map(list_coord, parcours, main):
    dic = {'ligne1':'yellow','ligne2':'blue','ligne3':'5f932f','ligne3b':'8cd6f0',
       'ligne4':'bf4190','ligne5':'f06816','ligne6':'f06816',
       'ligne7':'f06816','ligne7b':'8bc691','ligne8':'9a74ab','ligne9':'5e8e10',
       'ligned10':'dca43a','ligne11':'4d1e1d','ligne12':'1f4728','ligne13':'7ce2e9',
       'ligne14':'4f265c'}
    
    Paris = folium.Map(location = [48.856578, 2.351828], zoom_start = 12)
    for color_i, locations_i in list_coord:
        lst = folium.PolyLine(locations_i, dic[color_i])
        lst.add_to(Paris)
        # 保存地图
        
    for nom, coords in main.items()
    folium.Marker(, popup='Horche').add_to(Paris)
    folium.Marker([48.84686470206919,2.307268847578926], popup='Ségur').add_to(Paris)
    Paris.save('testMap.html')
    
    # MacOS
    #chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    
    # Windows
    #chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    #chrome_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s"
    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'
    #webbrowser.get(chrome_path).open(url)
    #webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("http://google.com")
    
    webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(os.path.join(os.getcwd(),"testMap.html"))







def segment_parcours(parcours,r):
    print("merde")
    list_coord = defaultdict(list)
    main = {}
    for i in range(1,len(parcours)):
        step_prec = parcours[i-1]
        step = parcours[i]
        station_im1 = r.dict_stations[step_prec[0]]
        station_i = r.dict_stations[step[0]]
        list_coord[step[1]].append([[station_i.stop_lon, station_i.stop_lat],[station_im1.stop_lon, station_im1.stop_lat]])
    
    print("list_coord",list_coord)
    
    a = list_coord.pop('transfer')
    i=1
    for x in a:
        main['transfer '+str(i)] = x
    
    station_i = r.dict_stations[parcours[0][0]]
    main.update({'depart':[station_i.stop_lon, station_i.stop_lat]})
    station_i = r.dict_stations[parcours[-1][0]]
    main.update({'arrivee':[station_i.stop_lon, station_i.stop_lat]})
    return list_coord, main