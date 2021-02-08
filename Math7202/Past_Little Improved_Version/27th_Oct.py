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
ReFuelCharge = 0
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

#Trip i
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

#From trip i to trip j which fuel station is used
Trip_Fuel_Trip = [[[Trip_FuelStationFuel[i][s]+FuelStation_TripFuel[s][j] for s in Fuels].index(min([Trip_FuelStationFuel[i][s]+FuelStation_TripFuel[s][j] for s in Fuels]))for j in Trips]for i in Trips]
#From trip i to trip j the cost
# [0]:No need fuel
# [1]: Need fuel
Trip_Trip_Cost = [[[Trip_TripFuel[i][j], Trip_FuelStationFuel[i][Trip_Fuel_Trip[i][j]]+FuelStation_TripFuel[Trip_Fuel_Trip[i][j]][j]]for j in Trips]for i in Trips]

#Calculating the execute time
import time
start = time.clock()

#dictionary CanReach,Successors are two dictionaries filt the possible trips with feasible tima
#fuel are not considered in below two dictionaries
# What trips can I reach if I start at depot d with trip k
CanReach = {(d,k):
    [k]+[t for t in Trips if all([k!=t,TripTime[t][0]-TripTime[k][1]>=Trip_TripTime[k][t]])]
    for d in Depots for k in Trips}

# If I started at depot d with trip k and I'm at trip t, what can I do next
Successors = {(d,k,t):
    [t2 for t2 in CanReach[d,k] 
     if TripTime[t2][0]-TripTime[t][1]>=Trip_TripTime[t][t2]]
    for (d,k) in CanReach for t in CanReach[d,k]}

#Check if have time to fuel when I finish LastTrip and I m about to go to the NextTrip.
def FuelTimeConstrain(LastTrip,NextTrip):
    FeasibleStation = Trip_Fuel_Trip[LastTrip][NextTrip]
    if TripTime[NextTrip][0]>=TripTime[LastTrip][1]+Trip_FuelStationTime[LastTrip][FeasibleStation]+FuelStation_TripTime[FeasibleStation][NextTrip]:
        return True
    return False
    
NoComplible = 13928372893
#Important the curredt condition
#(start depot d, tour list tList, current fuel, start-up expense)
#We only calculating the last trip in the trip list according to the last trip's last trip.
def Cost(d,tList,f,expense):
    if len(tList)>=2:
        LastTrip = tList[-2]
        NextTrip = tList[-1]
        if f>=Trip_TripFuel[LastTrip][NextTrip]+TripFuel[NextTrip]:
            expense = expense + TripFuel[NextTrip] + Trip_Trip_Cost[LastTrip][NextTrip][0]
            f = f - Trip_TripFuel[LastTrip][NextTrip] - TripFuel[NextTrip]
            return f,expense
        elif FuelTimeConstrain(LastTrip,NextTrip):
            expense = expense + ReFuelCharge + TripFuel[NextTrip] + Trip_Trip_Cost[LastTrip][NextTrip][1]
            f = FuelCapacity - FuelStation_TripFuel[Trip_Fuel_Trip[LastTrip][NextTrip]][NextTrip] - TripFuel[NextTrip]
            if f<0:
                xxxxxxx
            return f,expense
        else:
            return 0,NoComplible
    else:
        NextTrip = tList[-1]
        expense = expense + TripFuel[NextTrip]
        f = f - TripFuel[NextTrip]
        return f,expense
            
AllTours = {}
#Generating the columns
#Using the Cost function every step
def Generate(d, Tour,f,expense):
    f,expense = Cost(d, Tour,f,expense)
    if expense==NoComplible or f<Trip_DepotFuel[Tour[-1]][d]:
        return
    AllTours[d,Tour] = expense + Trip_DepotFuel[Tour[-1]][d]
    for t in Successors[d,Tour[0],Tour[-1]]:
        Generate(d, Tour+(t,),f,expense)

for d,k in CanReach:
    Generate(d, (k,),FuelCapacity-Depot_TripFuel[d][k],BusCost+Depot_TripFuel[d][k])
    print(d,k,len(AllTours))
    
m = Model('ColGen')

Z = {k: m.addVar(vtype = GRB.BINARY) for k in AllTours}

m.setObjective(quicksum(AllTours[k]*Z[k] for k in Z))

VarsForT = {t:[] for t in Trips}
for k in Z:
    for t in k[1]:
        VarsForT[t].append(Z[k])

Cover = {t:
    m.addConstr(quicksum(VarsForT[t])==1)
    for t in Trips}
    
m.setParam('MIPGap', 0)
m.optimize()

for k in Z:
    if Z[k].x>0.01:
        print(k,Z[k].x,AllTours[k])
        
end = time.clock()
print(end-start,'Executing Time')



'''
Out comes for the current code
Optimal solution found (tolerance 0.00e+00)
Best objective 3.697320000000e+05, best bound 3.697320000000e+05, gap 0.0000%
(2, (0, 17, 32, 66, 95)) 1.0 16298
(2, (1, 13, 31, 48, 73, 87)) 1.0 16000
(2, (3, 22, 39, 70)) 1.0 15976
(2, (4, 20, 35, 65, 83, 99)) 1.0 16652
(2, (5, 47, 85)) 1.0 15854
(2, (7, 23, 34, 58, 68, 97)) 1.0 16718
(2, (8, 21, 60, 78, 91)) 1.0 16588
(2, (10, 33, 69, 90)) 1.0 16092
(2, (12, 50, 74, 81)) 1.0 15978
(2, (24, 38, 56, 75, 96)) 1.0 15740
(2, (25, 40, 79, 89)) 1.0 15910
(2, (42, 57, 77, 93)) 1.0 15900
(3, (14, 18, 29, 53, 71, 82, 98)) 1.0 16508
(4, (6, 26, 44, 67, 84)) 1.0 16414
(4, (9, 36, 59)) 1.0 15810
(4, (37, 63, 80, 88)) 1.0 15876
(4, (46, 62)) 1.0 15482
(5, (2, 28, 41, 54, 76, 86)) 1.0 16382
(5, (11, 19, 45)) 1.0 15978
(5, (15, 49, 61, 92)) 1.0 15906
(5, (16, 52)) 1.0 15864
(5, (27, 43, 55, 72, 94)) 1.0 15918
(5, (30, 51, 64)) 1.0 15888
83.8466318 Executing Time
'''