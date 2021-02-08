# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:39:57 2020

@author: simon
"""

import os, json
import pandas as pd
import math
import random
from gurobipy import *
import time
start = time.clock()

BusCost = 100000
MaxTour = 400000
FuelCapacity = 200000
nBus = 10
Buses = range(nBus)
random.seed(3)

# find json files
path_to_json = 'data/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

# load data from json
data = {}
for f in json_files:
    path = path_to_json+f
    print('Loading',path)
    with open(path,'r') as load_f:
        data[f[:-5]] = json.load(load_f)
print('... End loading ...')

# Trips' distance and time
TripInfo = data['TripInfo']
# Trip locations (start, end), both start and end contain their lat & lon
TripLoc = data['TripLoc']
# Distance and time from trip to trip
Trip_Trip = data['Trip_Trip']
# Distance and time from trip to fuel
Trip_Fuel = data['Trip_Fuel']
# Distance and time from trip to depot
Trip_Depot = data['Trip_Depot']
# Distance and time from fuel to trip
Fuel_Trip = data['Fuel_Trip']
# Distance and time from fuel to depot
Fuel_Depot = data['Fuel_Depot']
# Distance and time from depot to trip
Depot_Trip = data['Depot_Trip']

Trips = dict(zip(range(len(TripLoc)),TripLoc))
nTrip = len(Trips)
# set the depot locations
DepotLoc = [(34.282772,109.055493),
           (34.192004,108.942106),
           (34.166441,108.825083),
           (34.279425,108.847389),
           (34.308879,109.001622)]
Depots = dict(zip(range(len(DepotLoc)),DepotLoc))
# set the fuel station locations
FuelLoc = [(34.273484,108.979029),
          (34.211426,108.876454),
          (34.293572,108.847827),
          (34.33886,108.927522),
          (34.297941,109.056661)]
Fuels = dict(zip(range(len(FuelLoc)),FuelLoc))

# timetable start from 0 to 12*60*60 (12 hours a day)
TripTime = [(i,i+j[1]) for i in range(0,12*60*60,60*60) for j in TripInfo]

# Start time from depot d
StartDep = [[TripTime[t][0]-Depot_Trip[d][t%len(Trips)][1] for d in Depots] for t in range(len(TripTime))]
# End time at depot d
EndDep = [[TripTime[t][1]+Trip_Depot[t%len(Trips)][d][1] for d in Depots] for t in range(len(TripTime))]

# and each route has 12 trips a day
Trips = dict(zip(range(len(TripLoc*12)),TripLoc*12))

# Where should I go to refuel
def goFuel(t1,t2,f):
    FuelPlan = []
    # find a station to fuel
    for station in Fuels:
        if TripTime[t1][1] + Trip_Fuel[t1%nTrip][station][1] + Fuel_Trip[station][t2%nTrip][1] < TripTime[t2][0] \
                and Trip_Fuel[t1%nTrip][station][0] < f:
            # FuelPlan = [tuple(TimeCost,RemainedFuel,TargetTrip,FuelFlag)]
            FuelPlan.append((Trip_Fuel[t1%nTrip][station][1]+Fuel_Trip[station][t2%nTrip][1],
                             FuelCapacity-Fuel_Trip[station][t2%nTrip][0],t2,'F '+str(station)))
    # find a depot to fuel
    for station in Depots:
        if TripTime[t1][1] + Trip_Depot[t1%nTrip][station][1] + Depot_Trip[station][t2%nTrip][1] < TripTime[t2][0] \
                and Trip_Depot[t1%nTrip][station][0] < f:
            # FuelPlan = [tuple(TimeCost,RemainedFuel,TargetTrip,FuelFlag)]
            FuelPlan.append((Trip_Depot[t1%nTrip][station][1]+Depot_Trip[station][t2%nTrip][1],
                             FuelCapacity-Depot_Trip[station][t2%nTrip][0],t2,'FD '+str(station)))
    if len(FuelPlan) == 0:
        return (-1,-1,None,False)
    return min(FuelPlan) # minimum time cost
    
# Can we go to a fuel station between trip t1 and t2 with fuel f and we started from depot d on k
def CanFuel(d,k,t1,t2,f):
    # Does the first trip end too late or does the second trip start too early?
    if  Trip_Trip[t1%nTrip][t2%nTrip][1] > TripTime[t2][0] - TripTime[t1][1]:
        return (-1,-1,None,False)
    # Is there enough fuel?
    if TripInfo[t2%nTrip][0] + Trip_Trip[t1%nTrip][t2%nTrip][0] > f:
        # find fuel plan
        return goFuel(t1,t2,f)
    # return trip cost, remained fuel, target trip, fuel flag
    return (Trip_Trip[t1%nTrip][t2%nTrip][1],f-Trip_Trip[t1%nTrip][t2%nTrip][0],t2,'T')

def CanSchedule(Tour,t2):
    trip = Tour[0]
    cost = Tour[1]
    f = Tour[2]
    if cost == 0:
        return [t2],BusCost+Depot_Trip[d][t2%nTrip][1],FuelCapacity-Depot_Trip[d][t2%nTrip][0]
    t1 = trip[-1]
    nex = CanFuel(d,trip[0],t1,t2,f)
    if not nex[-1]:
        return False
    elif nex[-1] == 'T':
        return trip+[t2],cost+nex[0],nex[1]
    elif nex[-1][0] == 'F':
        return trip+[nex[-1],t2],cost+nex[0],nex[1]
    else:
        print('CanSchedule Crashed',t2)
        xxxxxxxxxx
     
# Buses
Tours = {(d,b): ([],0,0) for d in Depots for b in Buses}

# Start allocate trips
for t in Trips:
    costs = []
    for (d,b) in Tours:
        s = CanSchedule(Tours[d,b],t)
        if s:
            costs.append((s[1],d,b))
    cost,d,b = min(costs)
    Tours[d,b] = CanSchedule(Tours[d,b],t)


# Add return cost from trip to depot
for (d,b) in Tours:
    if Tours[d,b][0] == []:
        continue
    t = Tours[d,b][0][-1]
    f = Tours[d,b][2]
    # find out which depot should the bus return
    BKDepots = [d for d in DepotLoc if f>=Trip_Depot[t%nTrip][DepotLoc.index(d)][0]]
    if len(BKDepots) > 0:
        ReturnCost,ReturnDepot,ReturnFuel = min((Trip_Depot[t%nTrip][DepotLoc.index(d)][1],
                                      ['D'+str(DepotLoc.index(d))],
                                      Trip_Depot[t%nTrip][DepotLoc.index(d)][0]) 
                                     for d in BKDepots)
    elif f > min(Trip_Fuel[t][fs][0] for fs in Fuels):
        for fs in Fuels:
            if Trip_Fuel[t][fs][0] < f:
                # find a return plan with minimum cost
                ReturnCost,ReturnDepot,ReturnFuel = min((Trip_Fuel[t][fs][1]+Fuel_Depot[fs][DepotLoc.index(d)][1],
                      ['F'+str(fs),'D'+str(DepotLoc.index(d))],
                      FuelCapacity-Fuel_Depot[fs][DepotLoc.index(d)][0]) 
                                                        for d in DepotLoc)
    else:
        print('Can\'t return', d,b,Tours[d,b])
        xxxxxxxxx
    trip,cost,fuel = Tours[d,b]
    Tours[d,b] = (trip+ReturnDepot,cost+ReturnCost,fuel-ReturnFuel)
    print((d,b),Tours[d,b])

Objval = 0
for (d,b) in Tours:
    Objval += Tours[d,b][1]
print('Objective value is: ', Objval)

# time cost
end = time.clock()
print('Time cost:',end-start)