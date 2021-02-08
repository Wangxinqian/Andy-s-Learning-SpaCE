import math
import random
from gurobipy import *
random.seed (3)
def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 100
nLocs = 100
nDepots = 5
nFuels = 5
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)
Fuels = range(nFuels)

Square = 150
BusCost = 150000
ReFuelCharge = 500
FuelCapacity = 600
DepotMaxCapacity = 10
DepotLeastCapacity = 1

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
  start = random.randint(240,1440 - D[TripLoc[i][0]][TripLoc[i][1]] - 60)
  end = start + D[TripLoc[i][0]][TripLoc[i][1]] + random.randint(0,30)
  return (start, end, 2*(D[TripLoc[i][0]][TripLoc[i][1]]))

TripTime = [GenerateTimes_Fuel(i)[:-1] for i in Trips]
#AverageWorkingTime = sum(i[1]-i[0] for i in TripTime)/len(TripTime)
#BreakInterval = int(AverageWorkingTime*0.3)
#BreakInterval=10
TripFuel = [GenerateTimes_Fuel(i)[-1] for i in Trips]
TripData = sorted((tt,tl,tf) for (tt,tl,tf) in zip(TripTime,TripLoc,TripFuel))
TripTime = [tt for (tt,_,_) in TripData]
TripLoc = [tl for (_,tl,_) in TripData]
TripFuel = [tf for (_,_,tf) in TripData]

Trip_TripFuel = [[2*D[TripLoc[i][1]][TripLoc[j][0]] for j in Trips] for i in Trips]
Trip_TripTime = [[D[TripLoc[i][1]][TripLoc[j][0]] for j in Trips] for i in Trips]

Trip_DepotFuel = [[2*D[TripLoc[i][1]][DepotLoc[j]] for j in Depots] for i in Trips]
Trip_DepotTime = [[D[TripLoc[i][1]][DepotLoc[j]] for j in Depots] for i in Trips]

Trip_FuelStationFuel = [[2*D[TripLoc[i][1]][FuelLoc[j]] for j in Fuels] for i in Trips]
Trip_FuelStationTime = [[D[TripLoc[i][1]][FuelLoc[j]] for j in Fuels] for i in Trips]

FuelStation_TripFuel = [[2*D[FuelLoc[i]][TripLoc[j][0]] for j in Trips] for i in Fuels]
FuelStation_TripTime = [[D[FuelLoc[i]][TripLoc[j][0]] for j in Trips] for i in Fuels]

FuelStation_DepotFuel = [[2*D[FuelLoc[i]][DepotLoc[j]] for j in Depots] for i in Fuels]
FuelStation_DepotTime = [[D[FuelLoc[i]][DepotLoc[j]] for j in Depots] for i in Fuels]

Depot_TripFuel = [[2*D[DepotLoc[i]][TripLoc[j][0]] for j in Trips] for i in Depots]
Depot_TripTime = [[D[DepotLoc[i]][TripLoc[j][0]] for j in Trips] for i in Depots]

import time
start = time.clock()

#If I m in trip k and ready for going to trip t with fuel f
def CanFuel(k,t,f):
    # if the current trip is not same as my last trip and I have time to get the start time, Then just go
    if k!=t and TripTime[t][0]-TripTime[k][1]>=Trip_TripTime[k][t]:
        #If the fuel is just enough, and I can get to the nearest fuel station to refuel, the schedule is feasible
        if TripFuel[t] + Trip_TripFuel[k][t] + min(Trip_FuelStationFuel[t][station] for station in Fuels) <= f:
            f=f-TripFuel[t]-Trip_TripFuel[k][t]
            return (t,f)
        else:
            #Go fuel
            Station_list = []
            for station in Fuels:
                # If time just enough even if we go after the fuel
                if TripTime[t][0] - Trip_FuelStationTime[k][station] - FuelStation_TripTime[station][t]>= 0:
                    # if fuel is enough after refuling
                    if f >= Trip_FuelStationFuel[k][station]:
                        #We can get to the next fuel station after we go to trip t
                        if FuelStation_TripFuel[station][t] <= FuelCapacity - TripFuel[t] - min(Trip_FuelStationFuel[t][s] for s in Fuels):
                            f=FuelCapacity - FuelStation_TripFuel[station][t] - TripFuel[t]
                            Station_list.append((FuelStation_TripFuel[station][t],t,station,f))
            if len(Station_list)>0:
                return min(Station_list)
            return False
    return False

def CanFuel_Decomposition(Trips,k,f):
    kd = []
    for t in Trips:
        Judge = CanFuel(k,t,f)
        if Judge != False:
            if len(Judge)==2:
                kd.append([Judge[0],Judge[-1]])
            elif len(Judge)==4:
                kd.append([Judge[1],Judge[2],Judge[-1]])
            else:
                xxxxxxxxxx
    return kd

CanReach = {(d,k):
    [[k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]]]
    +[r for r in CanFuel_Decomposition([i for i in Trips],k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k])]
    for d in Depots for k in Trips if TripFuel[k] <= FuelCapacity-Depot_TripFuel[d][k]
                                        and min(Trip_FuelStationFuel[k][station] for station in Fuels)<=FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]}
    
AllTours = {}
def Generate(Tour,d):
    k = ()
    cost = 0
    for x in Tour:
        k = k + (x[0],)
        if len(x)==2:
            cost = cost + 500 - x[-1]
        else:
            cost = cost + 500 - x[-1] + ReFuelCharge
    AllTours[d,k] = cost
    if (d,k[-1]) in CanReach and len(CanReach[d,k[-1]]) > 1:
        TTTTT = [i[0] for i in CanReach[d,k[-1]][1:]]
        for r in CanFuel_Decomposition(TTTTT,Tour[-1][0],Tour[-1][-1]):
            Generate(Tour+(r,),d)
        

for d,k in CanReach:
    Tour = (CanReach[d,k][0],)
    Generate(Tour,d)
    print(d,k,len(AllTours))

m = Model('ColGen')

Z = {k: m.addVar(vtype=GRB.BINARY) for k in AllTours}

m.setObjective(quicksum((AllTours[k]+BusCost)*Z[k] for k in Z))

Cover = {t:
    m.addConstr(quicksum(Z[k] for k in Z if t in k[1])==1)
    for t in Trips}

# DepotMaxCapacityConstrain = {d:
#     m.addConstr(quicksum(Z[k] for k in Z if d == k[0])<=DepotMaxCapacity)
#     for d in Depots}
    
# DepotLeastCapacityConstrain = {d:
#     m.addConstr(quicksum(Z[k] for k in Z if d == k[0])>=DepotLeastCapacity)
#     for d in Depots}
    
m.setParam('MIPGap', 0)
m.optimize()

end = time.clock()
print(end-start,'运行时间')


for k in Z:
    if Z[k].x>0.9:
        print(k)