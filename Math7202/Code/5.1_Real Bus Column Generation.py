# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 12:21:11 2020

@author: Yupeng Wu
"""

import os, json
import pandas as pd
import math
import random
from gurobipy import *

BusCost = 100000
# Set Maxtour to a smaller number in order to show a simple solution
# If we set MaxtTour=400000, then it will be super time consuming
MaxTour = 10000
FuelCapacity = 200000
# In order to make the model feasible, set nBus=60
nBus = 60
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

# Where should I go to refuel when I finished t1 and will go for t2 with fuel f
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
    
# If we need to go to a fuel station between trip t1 and t2 with fuel f 
# while we started from depot d on k
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

# What trips can I reach if I start at depot d with trip k with fuel f
CanReach = {(d,k):
    [k]+[t for t in Trips
        if all([
                EndDep[t][d]-StartDep[k][d]<=MaxTour,
                k!=t,
                CanFuel(d,k%nTrip,k,t,FuelCapacity-Depot_Trip[d][k%nTrip][0])[1]>0
            ])
        ]
    for d in Depots for k in Trips}
    
# If I started at depot d with trip k and I'm at trip t with fuel f, what can I do next
Successors = {(d,k,t):
              [t2 for t2 in CanReach[d,k] 
               if TripTime[t2][0]-TripTime[t][1]>=Trip_Trip[t%nTrip][t2%nTrip][1]]
    for (d,k) in CanReach for t in CanReach[d,k]}

ILLEGAL = 9999999999
def Cost(d,tList):
    k = tList[0]
    f = FuelCapacity - Depot_Trip[d][k%nTrip][0]
    cost = BusCost + Depot_Trip[d][k%nTrip][1]
    for (t1,t2) in zip(tList,tList[1:]):
        nex = CanFuel(d,k,t1,t2,f)
        cost += nex[0]
        f = nex[1]
        if f<=0:
        # If we get here with no fuel
            return ILLEGAL
    # Find out which depot should the bus return
    BKDepots = [d for d in DepotLoc if f>=Trip_Depot[tList[-1]%nTrip][DepotLoc.index(d)][0]]
    if len(BKDepots) > 0:
        ReturnCost = min(Trip_Depot[tList[-1]%nTrip][DepotLoc.index(d)][1] for d in BKDepots)
        return cost + ReturnCost
    else:
        return ILLEGAL

AllTours = {}

def Generate(d, Tour):
    cost = Cost(d,Tour)
    if cost==ILLEGAL:
        return
    AllTours[d,Tour] = cost
    for t in Successors[d,Tour[0],Tour[-1]]:
        Generate(d, Tour+(t,))

for d,k in CanReach:
    Generate(d, (k,))
    print(d,k,len(AllTours))

m = Model('ColGen')

Z = {k: m.addVar(vtype=GRB.BINARY) for k in AllTours}

m.setObjective(quicksum(AllTours[k]*Z[k] for k in Z))

Cover = {t:
    m.addConstr(quicksum(Z[k] for k in Z if t in k[1])==1)
    for t in Trips}
    
BusLimit = {d:
            m.addConstr(quicksum(Z[k] for k in Z if d == k[0])<=nBus)
            for d in Depots}

m.setParam('MIPGap', 0)
m.optimize()

Schedule = []
for k in Z:
    if Z[k].x>0.9:
        Schedule.append(k)

# Construct output into a human-friendly form and print
Output = {}
DepotBus = {}
for d,Tour in Schedule:
    k = Tour[0]
    if d in DepotBus:
        DepotBus[d] += 1
    else:
        DepotBus[d] = 0
    retBus = (d,DepotBus[d])
    retTour = [k]
    cost = BusCost + Depot_Trip[d][k%nTrip][1]
    f = FuelCapacity - Depot_Trip[d][k%nTrip][0]
    for (t1,t2) in zip(Tour,Tour[1:]):
        nex = CanFuel(d,k,t1,t2,f)
        cost += nex[0]
        f = nex[1]
        if nex[-1] == 'T':
            retTour += [t2]
        elif nex[-1][0] == 'F':
            retTour += [nex[-1],t2]
        else:
            print('Infeasible solution')
            xxxxxx
    retInfo = min((Trip_Depot[retTour[-1]%nTrip][d][1],d,
                   Trip_Depot[retTour[-1]%nTrip][d][0]) 
                  for d in Depots)
    cost += retInfo[0]
    retTour += ['D'+str(retInfo[1])]
    f -= retInfo[2]
    if f < 0:
        print('Infeasible solution: can\'t return')
        xxxxxx
    Output[retBus] = (retTour,cost,f)
    print(retBus, (retTour,cost,f))