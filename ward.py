# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 15:16:40 2018

@author: trying
"""

import shapefile
import matplotlib.pyplot as plt
import matplotlib.path as mplPath
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn import linear_model
#read the shapes of the wards in toronto
sf = shapefile.Reader("icitw_wgs84.shp")
wards = sf.shapeRecords() #list of shapes
#read the 311 data
restaurantData = pd.read_excel('dinesafedata.xlsx')
garbage16Data = pd.read_csv("SR2016.csv")
garbage17Data = pd.read_csv("SR2017.csv")
garbage18Data = pd.read_csv("SR2018.csv")
result = list()
severity = restaurantData[restaurantData.SEVERITY.isin(['M - Minor','S - Significant', 'C - Crucial', '4'])]
x=list()
y=list()    
ward_waste=dict()
for i in range(len(wards)):
    name = wards[i].record[2]
    if name.index(')')-name.index('(')==2:     #fix the naming issue for (6) and (06)
        name=name[0:name.index('(')]+'(0'+name[name.index('(')+1:]
    # define point in shape
    points = wards[i].shape.points
    bbPath = mplPath.Path(points)
    #collect severity info for this ward
    sev_ward = [a for a in severity.values if bbPath.contains_point((a[7],a[6]))]
    sev_ward = [a for a in sev_ward if ("sani" in a[10].lower() or "food" in a[10].lower() and "non" not in a[10].lower())]
    sev_m = [a for a in sev_ward if a[12]=="M - Minor"]
    sev_s = [a for a in sev_ward if a[12]=="S - Significant"]
    sev_c = [a for a in sev_ward if a[12]=="C - Crucial"]
    temp_waste=dict()
    for yr in range(0,3):
        #collect number of garbage request in this ward each year
        if yr ==0:
            all_ward = [rec for rec in garbage16Data.values if rec[5]==name and rec[1]!="Cancelled"]
            time='2016-'
        if yr ==1:
            all_ward = [rec for rec in garbage17Data.values if rec[5]==name and rec[1]!="Cancelled"]
            time='2017-'
        if yr ==2:
            time='2018-'
            all_ward = [rec for rec in garbage18Data.values if rec[5]==name and rec[1]!="Cancelled"]
        garbage = [a for a in all_ward if 'Garbage' in a[6]]
        res_garbage = [a for a in garbage if 'Residential' in a[6]]
        waste = [a for a in all_ward if 'Waste' in a[6]]
        res_waste = [a for a in waste if 'Residential' in a[6]]
        monthlist =['01','02','03','04','05','06','07','08','09','10','11','12']
        # the dine safe dataset ends at 2018-09
        if yr==2: monthlist = ['01','02','03','04','05','06','07','08','09']
        
        for m in monthlist:
            
            month = time+m
            g = [a for a in garbage if a[0][:7]==month]
            rg=[a for a in res_garbage if a[0][:7]==month]
            w=[a for a in waste if a[0][:7]==month]
            rw=[a for a in res_waste if a[0][:7]==month]
            war = [a for a in sev_ward if a[11][:7]==month]
            if len(war)==0:
                y.append(0)
            else:
                y.append(1)
            x_record = [len(g),len(g)-len(rg),len(w),len(w)-len(rw)]
            x.append(x_record)
            temp_waste[month]=[len(g)-len(rg)+len(w)-len(rw),len(rg)+len(rw)]
    ward_waste[name]=temp_waste
            

#predict the food related issue with garbage data
from sklearn.neighbors import KNeighborsClassifier
neigh = KNeighborsClassifier(n_neighbors=4)
#fit on the first 1000 data points, predict on the last 400 to validate
neigh.fit(x[:1000], y[:1000]) 
print(neigh.score(x[1000:],y[1000:]))            

#print out ward_waste value for excel generation
print(ward_waste)

