import math
import random
from gurobipy import *
random.seed (5)
def Distance(p1, p2):
  return int(math.hypot(p1[0] - p2[0], p1[1] - p2[1]) + 0.5)

nTrips = 50
nLocs = 150
nDepots = 1
nFuels = 1
Trips = range(nTrips)
Locs = range(nLocs)
Depots = range(nDepots)
Fuels = range(nFuels)

Square = 150
BusCost = 100
MaxTour = 480
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
CanReach = {(d,k):
    [k]+[t for t in Trips
        if all([
                #EndDep[t][d]-StartDep[k][d]<=MaxTour,
                k!=t,
                CanFuel(d,k,k,t,FuelCapacity-Depot_TripFuel[d][k])
            ])
        ]
    for d in Depots for k in Trips}
    
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
        if f>0:
            if nex[-1] == 'F':
                f = FuelCapacity - FuelStation_TripFuel[nex[1]][t2]
                break
            elif nex[-1] == 'T':
                f -= Trip_TripFuel[t1][t2]
                break
        else:
        # If we get here with no fuel
            xxxxxxxxx
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
    #print(d,k,len(AllTours))
    
    
A = []
for x in AllTours.keys():
    A.append(x[1])
print(len(A))
    









#如果我在trip k 准备去 trip t
def CanFuel_1(k,t,f):
    # 我不能再回过去k 开一遍 且 我不能开 时间上不满足的
    if k!=t and TripTime[t][0]-TripTime[k][1]>=Trip_TripTime[k][t]:
        #油刚好够，不去加油，就去trip t,返回(t,结束t后的油量)
        if TripFuel[t] + Trip_TripFuel[k][t] + min(Trip_FuelStationFuel[t][station] for station in Fuels) <= f:
            f=f-TripFuel[t]-Trip_TripFuel[k][t]
            return (t,f)
        else:
            #去加油
            Station_list = []
            for station in Fuels:
                # trip t 开始时间 大于 trip k到加油站的时间 加上 从加油站开到 trip t的时间
                if TripTime[t][0] - Trip_FuelStationTime[k][station] - FuelStation_TripTime[station][t] >= 0:
                    #油量能到
                    if f >= Trip_FuelStationFuel[k][station]:
                        #且加完油跑完trip-t 之后可以去下一个加油站
                        if FuelStation_TripFuel[station][t] <= FuelCapacity - TripFuel[t] - min(Trip_FuelStationFuel[t][s] for s in Fuels):
                            f=FuelCapacity - FuelStation_TripFuel[station][t] - TripFuel[t]
                            Station_list.append((FuelStation_TripFuel[station][t],t,station,f))
            if len(Station_list)>0:
                return min(Station_list)
            return False
    return False

#Trips 这边可以优化，我们不用每次遍历 所有Trips
def CanFuel_Decomposition(Trips,k,f):
    kd = []
    for t in Trips:
        Judge = CanFuel_1(k,t,f)
        if Judge != False:
            if len(Judge)==2:
                kd.append([Judge[0],Judge[-1]]) #返回 trip t  和  开完后剩下的油量
            elif len(Judge)==4:
                kd.append([Judge[1],Judge[2],Judge[-1]])
            else:
                xxxxxxxxxx
    return kd

# What trips can I reach if I start at depot d with trip k,with fuel f
#每天出发的车  都是满油 ， can reach  算的是第一段，所以f等于FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]
CanReach_B = {(d,k):
    [[k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k]]]+[r for r in CanFuel_Decomposition(Trips,k,FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k])]
    for d in Depots for k in Trips if TripFuel[k] <= FuelCapacity-Depot_TripFuel[d][k]}
    
# Successors = {(d,k,x[0]):
#       [x]+[r for r in CanFuel_Decomposition([i[0] for i in CanReach[d,k]],x[0],x[-1])]
#       #[x]+[r for r in CanFuel_Decomposition(Trips,x[0],x[-1])]
#       for (d,k) in CanReach for x in CanReach[d,k]}

AllTours_B = {}
def Generate_B(Tour,d):
    k = ()
    for x in Tour:
        k = k + (x[0],)
    AllTours_B[k] = Tour
    for r in CanFuel_Decomposition(Trips,Tour[-1][0],Tour[-1][-1]):
        Generate_B(Tour+(r,),d)

for d,k in CanReach_B:
    Tour = (CanReach_B[d,k][0],)
    Generate_B(Tour,d)
    #print(d,k,len(AllTours))
    
B = []
for x in AllTours_B.keys():
    B.append(x)
print(len(B))

C=[]

for x in B:
    if x not in A:
        print('第二个算法和第一个有异议的地方',x)

for x in A:
    if x not in B:
        print('第一个算法和第二个有异议的地方',x)
        C.append(x)
print(C[0],'拿这一组来解，是0,4，车从depot0出发,开过0，再去4')
print('设置d，k，t 分别为0，0，4，如下')
d=0
k=0
t=4
print('车从d出来开到k的终点站之后所剩下的油',FuelCapacity-Depot_TripFuel[d][k]-TripFuel[k])
print('此时，车准备去加油，发现油量',Trip_FuelStationFuel[k][0],'油不够')
print('他准备回DEPOT发现',Trip_DepotFuel[0][0],'油不够')

