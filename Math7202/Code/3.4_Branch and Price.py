import math
import random
from gurobipy import *
random.seed (3)
def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 20
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

#input trip chain, depot d
#output the current fuel after finishing the whole chain 
#We are not considered the fuel cost of a particular trip, because no matter what, it would always be paid.
def SuccessCost(d,Tour,f=0,expense=0):
    #Initialize the trip, if the output length is one
    if expense == 0 and f == 0:
        k = Tour[0]
        f = FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]
        expense = BusCost+Depot_TripFuel[d][k]
        if len(Tour) == 1:
            return f,expense + Trip_DepotFuel[Tour[-1]][d]
    if len(Tour)>=2:
        LastTrip = Tour[0]
        NextTrip = Tour[1]
        #If Noe Fuel
        if f>=Trip_TripFuel[LastTrip][NextTrip]+TripFuel[NextTrip]:
            expense = expense + Trip_Trip_Cost[LastTrip][NextTrip][0]
            f = f - Trip_Trip_Cost[LastTrip][NextTrip][0] - TripFuel[NextTrip]
            Tour = Tour[1:]
            return SuccessCost(d,Tour,f,expense)
        #If Fuel
        elif FuelTimeConstrain(LastTrip,NextTrip):
            expense = expense + ReFuelCharge  + Trip_Trip_Cost[LastTrip][NextTrip][1]
            f = FuelCapacity - FuelStation_TripFuel[Trip_Fuel_Trip[LastTrip][NextTrip]][NextTrip] - TripFuel[NextTrip]
            Tour = Tour[1:]
            return SuccessCost(d,Tour,f,expense)
        #Fail both, return NoComplible
        else:
            return NoComplible,NoComplible
    return f,expense+ Trip_DepotFuel[Tour[-1]][d]


AllTours = {}

def Generate(d, Tour):
    f,expense = SuccessCost(d, Tour)
    if expense>=NoComplible or f<Trip_DepotFuel[Tour[-1]][d] or f == NoComplible:
        return
    AllTours[d,Tour] = expense
    if len(Tour)>=2:
        return
    for t in Successors[d,k,Tour[-1]]:
        Generate(d, Tour+(t,))
        
for d,k in CanReach:
    Generate(d, (k,))
    print(d,k,len(AllTours))
    
m = Model('ColGen')

Z = {k: m.addVar() for k in AllTours}

m.setObjective(quicksum(AllTours[k]*Z[k] for k in Z))

VarsForT = {t:[] for t in Trips}
for k in Z:
    for t in k[1]:
        VarsForT[t].append(Z[k])

Cover = {t:
    m.addConstr(quicksum(VarsForT[t])==1)
    for t in Trips}

m.setParam('MIPGap', 0)


def GenColumns():
    Added = 0
    #Initialization
    for d,i in CanReach:
        Short = [(GRB.INFINITY,None) for _ in Trips]
        Short[i] = (BusCost + Depot_TripFuel[d][i]-Cover[i].pi,(i,))
        
        for j in CanReach[d,i]:
            #Checking code for debug
            if Short[j][1] is None :
                continue
            #Checking code for debug
            if Short[j][1][-1]!=j :
                xxxxxxxxxx
            if Short[j][0]+Trip_DepotFuel[j][d]<-0.00000001:
                tCol = Short[j][1]
                #Checking code for debug
                if tCol[-1]!=j:
                    xxxxxxxx
                #Checking code for debug
                #This is a very important code by detecting whether it is executing correct.
                if (d,tCol) in Z:
                    print(d,tCol)
                    xxxxxxxxxxxxxxxxxxx
                f,co = SuccessCost(d,tCol)
                if co>=NoComplible or f<Trip_DepotFuel[tCol[-1]][d] or f == NoComplible:
                    print(d,tCol,co,tCol[-1],Trip_DepotFuel[tCol[-1]][d],f)
                    xxxxxxxxxxxxxxxxxxx
                Z[(d,tCol)] = tVar = m.addVar(obj=co)
                for tt in tCol:
                    m.chgCoeff(Cover[tt],tVar,1)
                Added += 1
            # We comment the code below because it is not fit the code here
            # if Short[j][0]==GRB.INFINITY:
            #     continue
            #     print('Failed at',d,i,j)
            #     xxxxxxxxxxxxxxxxxxx
            for t in Successors[d,i,j]:
                #Checking code for debug
                if t == None and t==j:
                    continue
                Tour = Short[j][1]
                #Calculating the fuel after visiting the Short[j]'s tour.
                f,expense = SuccessCost(d,Tour)
                #Check if it is feasible
                if f<Trip_DepotFuel[Tour[-1]][d] or f == NoComplible:
                    continue
                else:
                    #If I add the trip t into the least would it be feaible
                    #Because we have only fixing the time constrain
                    #The only thing we need to care about is the fuel
                    ff,expense = SuccessCost(d,Tour+(t,))
                    #Check if the new solution is feasible
                    if expense>=NoComplible or ff<Trip_DepotFuel[t][d] or ff >= NoComplible:
                        continue
                    #If the fuel is no need to fuel
                    if f>=Trip_TripFuel[j][t]+TripFuel[t]:
                        tCost = Short[j][0]+Trip_Trip_Cost[j][t][0]-Cover[t].pi
                        if tCost< Short[t][0]:
                            Short[t] = (tCost,Short[j][1]+(t,))
                    #If need refuelig
                    elif FuelTimeConstrain(j,t):
                        #and FuelCapacity-FuelStation_TripFuel[Trip_Fuel_Trip[j][t]][t]-TripFuel[t]-Trip_DepotFuel[t][d]>=0:
                        tCost = Short[j][0]+ ReFuelCharge +Trip_Trip_Cost[j][t][1]-Cover[t].pi
                        if tCost < Short[t][0]:
                            Short[t] = (tCost,Short[j][1]+(t,))
                    #Otherwise
                    else:
                        continue
    return Added

m.setParam("OutputFlag",0)
LowerBound = GRB.INFINITY
while True:
    m.optimize()
    print('Obj val:', m.objVal)
    Added = GenColumns()
    print(Added)
    if Added == 0:
        if LowerBound==GRB.INFINITY:
            LowerBound = m.objVal
            break
for v in m.getVars():
    v.vtype = GRB.BINARY
for v in m.getVars():
    v.lb = 0
m.optimize()
print('Obj val:', m.objVal,LowerBound)
for k in Z:
    if Z[k].x>0.01:
        print(k)
        
end = time.clock()
print(end-start,'Execution Time')