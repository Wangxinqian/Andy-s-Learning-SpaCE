#!usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@project:  Infs7450
@author:   Xinqian Wang(Andy) 
@contact:  xinqian.wang@uq.net.au
@website:  https://github.com/Wangxinqian/Andy-s-Learning-SpaCE
@file:     graph_me.py 
@platform: Windows 10, IDLE Python 3.7
@time:     2020/04/19 13:33
"""

#Import package
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from networkx.algorithms import tree
import time
import numpy as np
from numpy import mat
import heapq

class Stack:
    def __init__(self): 
        self.items = [] 

    def isEmpty(self): 
        return self.items == [] 

    def push(self, item): 
        self.items.append(item) 

    def pop(self): 
        return self.items.pop()
    
    def peek(self): 
        return self.items[len(self.items)-1] 

    def size(self): 
        return len(self.items) 
    
class Queue: 
    def __init__(self): 
        self.items = [] 

    def isEmpty(self): 
        return self.items == [] 

    def enqueue(self, item): 
        self.items.insert(0, item) 

    def dequeue(self): 
        return self.items.pop() 

    def size(self): 
        return len(self.items) 




if __name__ == "__main__":
    # Create Directed Graph
    G = nx.Graph() #G = nx.DiGraph()
    Node_List = []
    FileName = "3.data.txt"
    with open(FileName) as file:
        for line in file:
            Node_L, Node_R = [str(x) for x in line.split()]
            Node_List.append(Node_L)
            Node_List.append(Node_R)
            G.add_edge(Node_L,Node_R)
    Node_List = list(set(Node_List))




    #----------------------------------------------
    #Task 1: caluculate the betweenness_centrality
    #----------------------------------------------
    #DATA
    Q = Queue()
    S = Stack()
    N = range(4039)
 
    #It should take around 500 seconds to run the code.
    start = time.time()
    C_b = [0 for _ in N]
    for ss in G.nodes():
        s = int(ss)
        #Single-source shortest path problem
        #Initialization
        pred = [[] for _ in G.nodes()]
        dist =[float("inf") for _ in G.nodes()]
        sigma = [0 for _ in N]
        
        dist[s] = 0
        sigma[s]=1
        Q.enqueue(s)
        
        while Q.isEmpty() == False:
            v = Q.dequeue()
            S.push(v)
            for ww in G[str(v)]:
                w = int(ww)
                if dist[w] == float("inf"):
                    dist[w] = dist[v] + 1
                    Q.enqueue(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] = sigma[w] + sigma[v]
                    pred[w].append(v)
                    
        delta = [0 for _ in G.nodes()]      
        while S.isEmpty() == False:
            w = S.pop()
            for v in pred[w]:
                delta[v] = delta[v] + ((sigma[v]/sigma[w])*(1+delta[w]))
            if w!=s:
                C_b[w] = C_b[w]+ delta[w]
                    
    end = time.time()
    print ("Running Time(seconds): ", end-start)    

    #import heapq
    print("Top-10 the betweenness_centrality: ",list(map(C_b.index, heapq.nlargest(10, C_b))))



    
    #----------------------------------------------
    #Task 2: PageRank Centrality
    #----------------------------------------------

    Degree_List = [G.degree[str(i)] for i in range(0,4039)]
    D = np.diag(Degree_List)
    inv_D = np.linalg.inv(D)
    inv_D = mat(inv_D)
    #print(np.shape(D),np.shape(inv_D))
    #print(type(inv_D))

    A = []
    for i in range(0,4039):
        L = []
        for j in range(0,4039):
            if str(j) in G[str(i)]:
                L.append(1)
            else:
                L.append(0)
        A.append(L)
    A = np.mat(A)

    Th = True
    c_old=np.matrix([[1] for i in range(4039)])
    II =np.matrix([1 for i in range(4039)])
    k=1
    alpha = 0.85
    beta = 0.15
    I = np.identity(4039)

    start = time.time()
    k = 0
    while Th:
        c_new = alpha*A.T*inv_D*c_old + beta
        V = np.linalg.norm((c_new - c_old), ord=1)
        if V < 0.001:
            Th = False
        else:
            k = k + 1
            #print(k,V)
            c_old = c_new
    end = time.time()
    print ('Running Time(seconds): ',end-start)

    CN = c_new.tolist()
    #import heapq
    max_num_index_list = list( map(CN.index, heapq.nlargest(10, CN)) )
    print("Top-10 the PageRank Centrality: ", max_num_index_list)
    

