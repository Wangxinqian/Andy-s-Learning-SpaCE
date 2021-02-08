'''
This is a early version
Finally we found that it is too slow, 60 seconds slower for the up_to_date version
We used a lot of ways in here but finally found that the code taught on the class is such efficient
So, we decide abandom this file
'''

import math
import random
from gurobipy import *
random.seed (3)
def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 100
nLocs = 100
nDepots = 6
nFuels = 6
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)
Fuels = range(nFuels)

Square = 150
BusCost = 15000
ReFuelCharge = 500
FuelCapacity = 1000
DepotCapacity = 20

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

TripTime = [GenerateTimes_Fuel(i)[:-1] for i in Trips]

#AverageWorkingTime = sum(i[1]-i[0] for i in TripTime)/len(TripTime)
#BreakInterval = int(AverageWorkingTime*0.3)
BreakInterval=10

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

#Calculating the execute time
import time
start = time.clock()

#Check if ned fuel
#We set
#trip: i
#fuel station I need to visit if I need to fuel: s
#fuel condition after doing trip i： f
#If not, output the list [i,f]
#Otherwise, out put [i,s,f]
def CanFuel(k,t,f):
    if k!=t and TripTime[t][0]-TripTime[k][1]-BreakInterval>=Trip_TripTime[k][t]:
        if TripFuel[t] + Trip_TripFuel[k][t] + min(Trip_FuelStationFuel[t][station] for station in Fuels) <= f:
            f=f-TripFuel[t]-Trip_TripFuel[k][t]
            return (t,f)
        else:
            Station_list = []
            for station in Fuels:
                if TripTime[t][0] - Trip_FuelStationTime[k][station] - FuelStation_TripTime[station][t] -BreakInterval>= 0:
                    if f >= Trip_FuelStationFuel[k][station]:
                        if FuelStation_TripFuel[station][t] <= FuelCapacity - TripFuel[t] - min(Trip_FuelStationFuel[t][s] for s in Fuels):
                            f=FuelCapacity - FuelStation_TripFuel[station][t] - TripFuel[t]
                            Station_list.append((FuelStation_TripFuel[station][t],t,station,f))
            if len(Station_list)>0:
                return min(Station_list)
            return False
    return False

#An algorithm for decode the Canfuel Function abrove
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
    #MaxTour
    if len(Tour)>5:
        return False
    #Can not go back to depot
    if Tour[-1][-1]< Trip_DepotFuel[Tour[-1][0]][d] and len(Tour)>3:
        return False
    #Working to hard
    if TripTime[Tour[-1][0]][1]+max(Trip_DepotTime[Tour[-1][0]][j] for j in Depots)>1550:
        return False
    k = ()
    #Calculating the cost
    cost = BusCost
    for x in Tour:
        k = k + (x[0],)
        if len(x)==2:
            cost = cost + FuelCapacity - x[-1]
        else:
            cost = cost + FuelCapacity - x[-1] + ReFuelCharge
    #Do gneration
    AllTours[d,k] = cost
    #Pre-Check, which can accelerate the algorithm
    #Check whether we have over the Canreach
    if (d,k[-1]) in CanReach and len(CanReach[d,k[-1]]) > 1:
        TTTTT = [i[0] for i in CanReach[d,k[-1]][1:]]
        for r in CanFuel_Decomposition(TTTTT,Tour[-1][0],Tour[-1][-1]):
            Generate(Tour+(r,),d)

for d,k in CanReach:
    for j in CanReach[d,k]:
        if j[0]==k:
            Tour = (j,)
        else:
            Tour = (CanReach[d,k][0],j)
        Generate(Tour,d)
    print(d,k,len(AllTours))

m = Model('ColGen')

Z = {k: m.addVar(vtype=GRB.BINARY) for k in AllTours}

m.setObjective(quicksum(AllTours[k]*Z[k] for k in Z))

Cover = {t:
    m.addConstr(quicksum(Z[k] for k in Z if t in k[1])==1)
    for t in Trips}
    
m.setParam('MIPGap', 0)
m.optimize()


for k in Z:
    if Z[k].x>0.01:
        print(k,Z[k].x)
        
end = time.clock()
print(end-start,'Executing Time')