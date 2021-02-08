import math
import random
from gurobipy import *

def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 500
nLocs = 150
nDepots = 5
nFuels = 5
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
StartDep = [[TripTime[t][0]-D[d][TripLoc[t][0]] for d in Depots] for t in Trips]
# End time at depot d
EndDep = [[TripTime[t][1]+D[TripLoc[t][1]][d] for d in Depots] for t in Trips]

# Where should I go to refuel
def goFuel(t1,t2,f):
    FuelPlan = []
    for station in Fuels:
        if TripTime[t1][1] + Trip_FuelStationTime[t1][station] + FuelStation_TripTime[station][t2] < TripTime[t2][0] and Trip_FuelStationFuel[t1][station] < f:
            FuelPlan.append((Trip_FuelStationFuel[t1][station]+FuelStation_TripFuel[station][t2],station,'F'))
    if len(FuelPlan) == 0:
        return False
    return min(FuelPlan)
    
# Can we go to a fuel station between trip t1 and t2 with fuel f and we started from depot d on k
def CanFuel(d,k,t1,t2,f):
    # Does the first trip end too late or does the second trip start too early?
    if  Trip_TripTime[t1][t2] > TripTime[t2][0] - TripTime[t1][1]:
        return False
    # Is there enough fuel?
    if TripFuel[t2] + Trip_TripFuel[t1][t2] > f:
        return goFuel(t1,t2,f)
    return (Trip_TripFuel[t1][t2],t2,'T')

# What trips can I reach if I start at depot d with trip k with fuel f
import time
start = time.clock()
CanReach = {(d,k):
    [k]+[t for t in Trips
        if all([
                k!=t,
                CanFuel(d,k,k,t,FuelCapacity-Depot_TripFuel[d][k])
            ])
        ]
    for d in Depots for k in Trips}
end = time.clock()
print(end-start,'运行时间')
'''    
# If I started at depot d with trip k and I'm at trip t with fuel f, what can I do next
Successors = {(d,k,t):
              [t2 for t2 in CanReach[d,k] 
               if all([
                t!=t2,
                TripFuel[t]+Trip_TripFuel[t][t2]+TripFuel[t2]<=FuelCapacity,
                TripTime[t2][0]-TripTime[t][1]>=Trip_TripTime[t][t2]
            ]) 
        ]
    for (d,k) in CanReach for t in CanReach[d,k]}

ILLEGAL = 9999999999
def Cost(d,tList):
    k = tList[0]
    f = FuelCapacity
    for (t1,t2) in zip(tList,tList[1:]):
        nex = CanFuel(d,k,t1,t2,f)
        if nex[-1] == 'F':
            f -= Trip_FuelStationFuel[t1][nex[1]] + FuelStation_TripFuel[nex[1]][t2]
            break
        elif nex[-1] == 'T':
            f -= Trip_TripFuel[t1][t2]
            break
    else:
        # If we get here a break is not possible
        return ILLEGAL
    return BusCost+D[d][TripLoc[tList[0]][0]]+D[TripLoc[tList[-1]][1]][d]+\
            sum(D[TripLoc[t1][1]][TripLoc[t2][0]] for (t1,t2) in zip(tList,tList[1:]))

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

m.setParam('MIPGap', 0)
m.optimize()
'''