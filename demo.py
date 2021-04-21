# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 15:36:54 2019

@author: vianney
"""

import datetime
import Network
import webbrowser
from collections import defaultdict
import folium
import os

def segment_parcours(parcours):
    i=0
    k=0
    ind = []
    while i<len(parcours)-1:
        if (i<len(parcours)) and parcours[i][1] == 'transfer' and parcours[i+1][1] != 'transfer':
            ind.append(i)
        i=i+1
    ind.append(-1)
    lis = []
    for i in range(len(ind)-1):
        lis.append(parcours[ind[i]:ind[i+1]])
    return lis



def create_map(lis, parcours, time):
    
    dic = {'1':'yellow','2':'blue','3':'#5f932f','3b':'#8cd6f0',
       '4':'purple','5':'#f06816','6':'#f06816',
       '7':'pink','7b':'#8bc691','8':'#9a74ab','9':'#5e8e10',
       '10':'#dca43a','11':'#4d1e1d','12':'#1f4728','13':'#7ce2e9',
       '14':'#4f265c'}
    
    Paris = folium.Map(location = [48.856578, 2.351828], zoom_start = 12)
    
    for subparcours in lis:
        locations_i = []
        for x in subparcours:
            station_i = r.dict_stations[x[0]]
            locations_i.append([station_i.stop_lat, station_i.stop_lon])
            color = 'blue'
            line = x[1]

            if line !='transfer':
                color = dic[line]
        lst = folium.PolyLine(locations = locations_i,color = color)
        lst.add_to(Paris)
    
    st_from = r.dict_stations[parcours[0][0]]
    st_to =  r.dict_stations[parcours[-1][0]]
    folium.Marker([st_from.stop_lat,st_from.stop_lon], popup=("Départ "+ st_from.stop_name + ' ' + str(time.time()))).add_to(Paris)
    harrival = str((time + datetime.timedelta(minutes=duration)).time())
    folium.Marker([st_to.stop_lat,st_to.stop_lon], popup=("Arrivée "+ st_to.stop_name+ ' ' + harrival)).add_to(Paris)
    
    Paris.save('testMap.html')
    
    # MacOS
    #chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    #url = os.path.join(os.getcwd(),"testMap.html")
    #webbrowser.get(chrome_path).open(url)
    
    # Windows
    #chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    #chrome_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s"
    
    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'
    #webbrowser.get(chrome_path).open(url)
    #webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("http://google.com")
    
    webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open(os.path.join(os.getcwd(),"testMap.html"))


time = datetime.datetime.strptime('20190321 15:25', '%Y%m%d %H:%M')
r = Network.Network(*["Input/RATP_GTFS_METRO_4", "Input/RATP_GTFS_METRO_5", "Input/RATP_GTFS_METRO_10"])



parcours, duration = r.compute_shortest_path("Boulogne Pont de Saint-Cloud", "Hoche", time)
print(parcours, duration)
    
list_coord = segment_parcours(parcours)
try:
    os.remove('testMap.html')
except:
    pass
create_map(list_coord, parcours, time)


