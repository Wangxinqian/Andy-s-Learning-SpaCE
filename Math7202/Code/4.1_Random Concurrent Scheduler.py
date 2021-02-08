# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 22:21:04 2020

@author: simon
"""

import math
import random
from gurobipy import *
import time
start = time.clock()

def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 100
nLocs = 200
nDepots = 5
nFuels = 5
nBus = 5
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)
Fuels = range(nFuels)
Buses = range(nBus)

Square = 150
BusCost = 1000
MaxTour = 1000
FuelCapacity = 400
random.seed(3)

# Set up random locations but set some of the positions to be corners
# of the grid.  The depots are the first nDepots positions
Pos = [(random.randint(0,Square), random.randint(0,Square)) for i in Locs]
Pos[0] = (0,0)
Pos[1] = (Square,Square)
Pos[2] = (0, Square)
Pos[3] = (Square, 0)
Pos[4] = (Square/2, Square/2)
D = [[Distance(Pos[i], Pos[j]) for j in Locs] for i in Locs]

TripLoc = [(random.choice(Locs), random.choice(Locs)) for i in Trips]
DepotLoc = [(random.choice(Locs)) for i in Depots]
FuelLoc = [(random.choice(Locs)) for i in Fuels]

def GenerateTimes_Fuel(i):
  # Generate a start and end time for a trip
  start = random.randint(240,1440 - D[TripLoc[i][0]][TripLoc[i][1]] - 60)
  end = start + D[TripLoc[i][0]][TripLoc[i][1]] + random.randint(0,30)
  return (start, end, 2*(D[TripLoc[i][0]][TripLoc[i][1]]))

#Trip i
TripTime = [GenerateTimes_Fuel(i)[:-1] for i in Trips]
TripFuel = [GenerateTimes_Fuel(i)[-1] for i in Trips]
TripData = sorted((tt,tl,tf) for (tt,tl,tf) in zip(TripTime,TripLoc,TripFuel))
TripTime = [tt for (tt,_,_) in TripData]
TripLoc = [tl for (_,tl,_) in TripData]
TripFuel = [tf for (_,_,tf) in TripData]

#Trip i 到 Trip j
Trip_TripFuel = [[2*D[TripLoc[i][1]][TripLoc[j][0]] for j in Trips] for i in Trips]
Trip_TripTime = [[D[TripLoc[i][1]][TripLoc[j][0]] for j in Trips] for i in Trips]

#Trip i 到 Depot
Trip_DepotFuel = [[2*D[TripLoc[i][1]][DepotLoc[j]] for j in Depots] for i in Trips]
Trip_DepotTime = [[D[TripLoc[i][1]][DepotLoc[j]] for j in Depots] for i in Trips]

#Trip i 到 FuelStation
Trip_FuelStationFuel = [[2*D[TripLoc[i][1]][FuelLoc[j]] for j in Fuels] for i in Trips]
Trip_FuelStationTime = [[D[TripLoc[i][1]][FuelLoc[j]] for j in Fuels] for i in Trips]

#Fuel Station to Trip i 
FuelStation_TripFuel = [[2*D[FuelLoc[i]][TripLoc[j][0]] for j in Trips] for i in Fuels]
FuelStation_TripTime = [[D[FuelLoc[i]][TripLoc[j][0]] for j in Trips] for i in Fuels]

#Fuel Station to Depot
FuelStation_DepotFuel = [[2*D[FuelLoc[i]][DepotLoc[j]] for j in Depots] for i in Fuels]
FuelStation_DepotTime = [[D[FuelLoc[i]][DepotLoc[j]] for j in Depots] for i in Fuels]

#Depot to Trip i 
Depot_TripFuel = [[2*D[DepotLoc[i]][TripLoc[j][0]] for j in Trips] for i in Depots]
Depot_TripTime = [[D[DepotLoc[i]][TripLoc[j][0]] for j in Trips] for i in Depots]

# Check if need to refuel
#def checknext(d,k,):

# Start time from depot d
StartDep = [[TripTime[t][0]-D[DepotLoc[d]][TripLoc[t][0]] for d in Depots] for t in Trips]
# End time at depot d
EndDep = [[TripTime[t][1]+D[TripLoc[t][1]][DepotLoc[d]] for d in Depots] for t in Trips]

# Where should I go to refuel
def goFuel(t1,t2,f):
    FuelPlan = []
    # find a station to fuel
    for station in Fuels:
        if TripTime[t1][1] + Trip_FuelStationTime[t1][station] + FuelStation_TripTime[station][t2] < TripTime[t2][0] \
                and Trip_FuelStationFuel[t1][station] < f:
            # FuelPlan = [tuple(TimeCost,RemainedFuel,TargetTrip,FuelFlag)]
            FuelPlan.append((Trip_FuelStationTime[t1][station]+FuelStation_TripTime[station][t2],
                             FuelCapacity-FuelStation_TripFuel[station][t2],t2,'F '+str(station)))
    # find a depot to fuel
    for station in Depots:
        if TripTime[t1][1] + Trip_DepotTime[t1][station] + Depot_TripTime[station][t2] < TripTime[t2][0] \
                and Trip_DepotFuel[t1][station] < f:
            # FuelPlan = [tuple(TimeCost,RemainedFuel,TargetTrip,FuelFlag)]
            FuelPlan.append((Trip_DepotTime[t1][station]+Depot_TripTime[station][t2],
                             FuelCapacity-Depot_TripFuel[station][t2],t2,'FD '+str(station)))
    # if don't have any fuel plan
    if len(FuelPlan) == 0:
        return (-1,-1,None,False)
    # return the refuel plan with a minimum cost
    return min(FuelPlan)
    
# Can we go to a fuel station between trip t1 and t2 with fuel f and we started from depot d on k
def CanFuel(d,k,t1,t2,f):
    # Does the first trip end too late or does the second trip start too early?
    if  Trip_TripTime[t1][t2] > TripTime[t2][0] - TripTime[t1][1]:
        return (-1,-1,None,False)
    # Is there enough fuel?
    if TripFuel[t2] + Trip_TripFuel[t1][t2] + min(Trip_DepotFuel[t2][d] for d in Depots)> f:
        return goFuel(t1,t2,f)
    return (Trip_TripTime[t1][t2],f-Trip_TripFuel[t1][t2],t2,'T')

def CanSchedule(Tour,t2):
    trip = Tour[0]
    cost = Tour[1]
    f = Tour[2]
    if cost == 0:
        return [t2],BusCost+Depot_TripTime[d][t2],FuelCapacity-Depot_TripFuel[d][t2]
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
    t = Tours[d,b][0][-1]
    f = Tours[d,b][2]
    # find out which depot should the bus return
    BKDepots = [d for d in DepotLoc if f>=Trip_DepotFuel[t][DepotLoc.index(d)]]
    if len(BKDepots) > 0:
        ReturnCost,ReturnDepot,ReturnFuel = min((Trip_DepotTime[t][DepotLoc.index(d)],
                                      ['D'+str(DepotLoc.index(d))],
                                      Trip_DepotFuel[t][DepotLoc.index(d)]) 
                                     for d in BKDepots)
    elif f > min(Trip_FuelStationFuel[t][fs] for fs in Fuels):
        for fs in Fuels:
            if Trip_FuelStationFuel[t][fs] < f:
                # find a return plan with minimum cost
                ReturnCost,ReturnDepot,ReturnFuel = min((Trip_FuelStationTime[t][fs]+FuelStation_DepotTime[fs][DepotLoc.index(d)],
                      ['F'+str(fs),'D'+str(DepotLoc.index(d))],
                      FuelCapacity-FuelStation_DepotFuel[fs][DepotLoc.index(d)]) 
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