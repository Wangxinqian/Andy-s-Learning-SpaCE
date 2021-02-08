import math
import random
from gurobipy import *

def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 100
nLocs = 300
nDepots = 10
nFuels = 10
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)
Fuels = range(nFuels)

Square = 150
BusCost = 100
FuelCapacity = 500

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
FuelLoc = [(random.choice(Locs)) for i in Fuels]
DepotLoc = [(random.choice(Locs)) for i in Depots]

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
#StartDep = [[TripTime[t][0]-D[d][TripLoc[t][0]] for d in Depots] for t in Trips]
# End time at depot d
#EndDep = [[TripTime[t][1]+D[TripLoc[t][1]][d] for d in Depots] for t in Trips]


# What trips can I reach if I start at depot d with trip k
#First Filter
import time
start = time.clock()

def CanFuel(d,k,t,f):
    if k!=t and TripTime[t][0]-TripTime[k][1]>=Trip_TripTime[k][t]:
        #油刚好够，不去加油，就去trip t,返回(t,结束t后的油量)
        if TripFuel[t] + Trip_TripFuel[k][t] + min(Trip_FuelStationFuel[t][station] for station in Fuels) <= f:
            f=f-TripFuel[t]-Trip_TripFuel[k][t]
            return (t,f)
        else:
            Station_list = []
            for station in Fuels:
                if TripTime[t][0] - Trip_FuelStationTime[k][station] - FuelStation_TripTime[station][t] >= 0:
                    if f >= Trip_FuelStationFuel[k][station]:
                        if FuelStation_TripFuel[station][t] <= FuelCapacity - TripFuel[t] - min(Trip_FuelStationFuel[t][s] for s in Fuels):
                            f=FuelCapacity - FuelStation_TripFuel[station][t] - TripFuel[t]
                            Station_list.append((FuelStation_TripFuel[station][t],t,station,f,'F'))
            if len(Station_list)>0:
                return min(Station_list)
            return False
    return False
            
def CanFuel_Decomposition(Trips,d,k,f):
    kd = []
    for t in Trips:
        Judge = CanFuel(d,k,t,f)
        if Judge != False:
            if len(Judge)==2:
                kd.append([Judge[0],Judge[1]]) #返回 trip t  和  开完后剩下的油量
            elif len(Judge)==5:
                kd.append([Judge[1],Judge[2],Judge[3]])
            else:
                xxxxxxxxxx
    return kd

# What trips can I reach if I start at depot d with trip k,with fuel f
#每天出发的车  都是满油 ， can reach  算的是第一段，所以f等于FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]
CanReach = {(d,k):
    [[k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]]]+[r for r in CanFuel_Decomposition(Trips,d,k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k])]
    for d in Depots for k in Trips if TripFuel[k] <= FuelCapacity-Depot_TripFuel[d][k]}


    
    


end = time.clock()
print(end-start,'运行时间')