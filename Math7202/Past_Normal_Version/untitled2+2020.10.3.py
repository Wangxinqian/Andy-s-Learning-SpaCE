import math
import random
from gurobipy import *

def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 100
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
    

# What trips can I reach if I start at depot d with trip k
CanReach = {(d,k):
    [k]+[t for t in Trips
        if all([
                k!=t, 
                Depot_TripFuel[d][k]+TripFuel[k]+Trip_TripFuel[k][t]+TripFuel[t]<=FuelCapacity,
                TripTime[t][0]-TripTime[k][1]>=Trip_TripTime[k][t]
            ]) or
            all([
                1<0,
                k!=t, 
                #不确定，最小的到加油站的距离未必就是 a+b 下午讨论的路线 的最优，但是min足够relax这个范围
                Depot_TripFuel[d][k]+TripFuel[k]+min(Trip_FuelStationFuel[k][j] for j in Fuels)<=FuelCapacity,
                TripTime[t][0]-TripTime[k][1]>=min(Trip_FuelStationTime[k][j]+FuelStation_TripTime[j][t] for j in Fuels)
            ])
        ]
    for d in Depots for k in Trips}
    
# If I started at depot d with trip k and I'm at trip t, what can I do next
Successors = {(d,k,t):
              [t2 for t2 in CanReach[d,k] 
               if all([
                t!=t2,
                TripFuel[t]+Trip_TripFuel[t][t2]+TripFuel[t2]<=FuelCapacity,
                TripTime[t2][0]-TripTime[t][1]>=Trip_TripTime[t][t2]
            ]) or
            all([
                1<0,
                t!=t2, 
                TripFuel[t]+min(Trip_FuelStationFuel[t][j] for j in Fuels)<=FuelCapacity,
                TripTime[t2][0]-TripTime[t][1]>=min(Trip_FuelStationTime[t][j]+FuelStation_TripTime[j][t2] for j in Fuels)
            ])
        ]
    for (d,k) in CanReach for t in CanReach[d,k]}
    
AllTours = {}

def Generate(d, Tour):
    cost = random.choice(range(0,20))
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
