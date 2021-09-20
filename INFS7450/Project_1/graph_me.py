#!usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@project:tutorial
@author:xiangguosun 
@contact:sunxiangguodut@qq.com
@website:http://blog.csdn.net/github_36326955
@file: graph_me.py 
@platform: macOS High Sierra 10.13.1 Pycharm pro 2017.1 
@time: 2020/03/11 
"""


# import networkx as nx
#
# g=nx.Graph()
#
# nx.closeness_centrality()
# nx.harmonic_centrality()




from collections import defaultdict

import numpy as np
import torch
import math



# import networkx as nx
# graph=nx.Graph()
# va=nx.closeness_centrality(graph)
# va=nx.in_degree_centrality()
# print(va)
# """
# {'s':0.99997,
# 't':lkkkl
# }
# """"



class Graph:
    def __init__(self, edges=None, weighted=True):
        # all nodes names
        node_set = set()
        for src, des, w in edges:
            node_set.add(src)
            node_set.add(des)

        """
        read node content, implemented by yourself.
        """
        self.node_names = list(node_set) # ['r','s',....]

        self.weighted = weighted
        self.edges = edges

        self.node_number = len(self.node_names)


        self.DiGraph = defaultdict(list)


        for node in self.node_names:
            self.DiGraph[node]

        for src, des, w in edges:
            self.DiGraph[src].append(des)


        self.name2index = defaultdict(int)
        self.index2name = defaultdict(str)

        for index, name in enumerate(self.DiGraph.keys()):
            self.name2index[name] = index
            self.index2name[index] = name

        self.DiAdj = torch.zeros((self.node_number, self.node_number))
        for src, des, w in edges:
            self.DiAdj[self.name2index[src], self.name2index[des]] = w

    def to_undirected(self):
        self.UnGraph = defaultdict(list)
        for node, neighbors in self.DiGraph.items():
            for nei in neighbors:
                self.UnGraph[node].append(nei)
                self.UnGraph[nei].append(node)

        """
        {'s':['t','t','a']}==>{'s':['t','a']}
        """
        # remove reduplicative nodes
        for node, neighbors in self.UnGraph.items():
            self.UnGraph[node] = list(np.unique(neighbors))

        # remove self-loop
        """
              {'s':['t','s','a']}
        """
        for node, neighbors in self.UnGraph.items():
            if node in neighbors:
                self.UnGraph[node] = neighbors.remove(node)

        self.DiGraph = self.UnGraph
        self.DiAdj = torch.zeros((self.node_number, self.node_number))
        for src, des, w in edges:
            self.DiAdj[self.name2index[src], self.name2index[des]] = w
            self.DiAdj[self.name2index[des], self.name2index[src]] = w

    def weight(self, u_name, v_name):
        return self.DiAdj[self.name2index[u_name], self.name2index[v_name]]

    def has_node(self, n):
        return n in self.node_names

    def has_edge(self, u, v):
        return v in self.DiGraph[u]

    def graph_transpose(self):
        graph = defaultdict(list)
        for node in self.node_names:
            graph[node]

        for src, des, w in edges:
            graph[des].append(src)
        """
        more work,update all related var, adj matrix.
        """
        return graph

    def degree(self, u=None,mode='out'):
        """

        :param u:
        :param mode: out,in,all
        :return:
        """
        nodes = []
        if u is None:
            nodes = self.node_names
        else:
            nodes.append(u)
        degree = defaultdict(int)
        if mode=='out':
            for node in nodes:
                degree[node] = len(self.DiGraph[node])
            return degree
        elif mode=='in':
            graph=self.graph_transpose()
            for node in nodes:
                degree[node] = len(graph[node])
            return degree
        else:
            graph=self
            graph.to_undirected()
            for node in nodes:
                degree[node] = len(graph[node])
            return degree

    def traverse(self, mode='bfs', src='s'):
        """
        :param mode: 'dfs','bfs'
        :return:
        if mode=='bfs', we return: BFS Tree, d, \pi and order list
        if mode=='dfs', we return: DFS Tree, finish time, start time, and order list
        """

        if mode == 'bfs':
            color = defaultdict(str)
            dis = defaultdict(float)
            pi = defaultdict(str)
            for name in self.node_names:
                color[name] = 'white'
                dis[name] = math.inf # math.inf
                pi[name] = '#'

            color[src] = 'gray'
            dis[src] = 0
            Q = [src]
            T = []
            order_list = [src]
            while len(Q) > 0:
                u = Q.pop(0)
                for v in self.DiGraph[u]:
                    if color[v] == 'white':
                        order_list.append(v)
                        color[v] = 'gray'
                        dis[v] = dis[u] + 1
                        pi[v] = u
                        Q.append(v)
                        T.append((u, v))
                    else:
                        continue
                color[u] = 'black'

            results = {"BFS_tree": T,
                       "dis": dis,
                       "pi": pi,
                       "order_list": order_list}
            return results
        elif mode == 'dfs':
            color = defaultdict(str)
            start_time = defaultdict(int)
            finish_time = defaultdict(int)
            pi = defaultdict(str)
            T = []
            order_list = []
            for name in self.node_names:
                color[name] = 'white'
                pi[name] = '#'

            time = 0
            S = []
            for s in self.node_names:
                if color[s] == 'white':
                    "one DFS starting from name"
                    color[s] = 'gray'
                    time = time + 1
                    start_time[s] = time
                    S.append(s)
                    order_list.append(s)

                    while len(S) > 0:
                        u = S[-1]
                        v = None
                        for nei in self.DiGraph[u]:
                            if color[nei] == 'white':
                                v = nei
                                break
                        if not v:  # if no such v
                            color[u] = 'black'

                            S.pop()
                            time = time + 1
                            finish_time[u] = time
                        else:
                            color[v] = 'gray'
                            time = time + 1
                            start_time[v] = time
                            pi[v] = u
                            T.append([u, v])
                            S.append(v)
                            order_list.append(v)

            results = {"DFS_tree": T,
                       "start_time": start_time,
                       "finish_time": finish_time,
                       "order_list": order_list
                       }

            return results

    def extract_min(self, Q, dis):
        temp_dis = defaultdict(float)
        for name in Q:
            temp_dis[name] = dis[name]
        u = min(temp_dis, key=temp_dis.get)
        Q.remove(u)
        return u, Q

    def prim(self, r):
        """
        r is start node name
        :param r:
        :return:
        """
        dis = defaultdict(float)
        pi = defaultdict(str)
        for name in self.node_names:
            dis[name] = math.inf
            pi[name] = '#'
        dis[r] = -1.0 * math.inf
        Q = self.node_names
        T = []
        while len(Q) > 0:
            u, Q = self.extract_min(Q, dis)

            T.append([pi[u], u])
            for v in self.DiGraph[u]:
                if (v in Q) and (self.weight(u, v) < dis[v]):
                    pi[v] = u
                    dis[v] = self.weight(u, v)
        results = {"MST": T}
        return results

    def Dijkstra(self, r):
        dis = defaultdict(float)
        pi = defaultdict(str)

        for name in self.node_names:
            dis[name] = math.inf
            pi[name] = '#'
        dis[r] = 0
        Q = self.node_names
        T = []
        while len(Q) > 0:
            u, Q = self.extract_min(Q, dis)
            T.append([pi[u], u])
            for v in self.DiGraph[u]:
                if (v in Q) and (self.weight(u, v) < dis[v]):
                    pi[v] = u
                    dis[v] = self.weight(u, v) + dis[u]
        results = {"shortest_path_tree": T,
                   "shortest_distance": dis}
        return results

    def out_degree_centrality(self):
        centrality = defaultdict(float)
        for node in self.node_names:
            centrality[node] = len(self.DiGraph[node])
        return centrality

    def closeness_centrality(self, u=None):
        if u is None:
            nodes = self.node_names
        else:
            nodes = [u]

        closeness_centrality = defaultdict(float)
        for n in nodes:
            sp = self.Dijkstra(n)['shortest_distance']
            totsp = sum(sp.values())
            closeness_centrality[n] = 1.0 / totsp
        return closeness_centrality


if __name__ == "__main__":
    edges = [('s', 't', 10),
             ('s', 'y', 5),
             ('t', 'y', 2),
             ('t', 'x', 1),
             ('y', 't', 3),
             ('y', 'x', 9),
             ('y', 'z', 2),
             ('x', 'z', 4),
             ('z', 'x', 6),
             ('z', 's', 7)
             ]
    # edges = [('A', 'B', 1),
    #          ('B', 'C', 1),
    #          ('C', 'D', 1),
    #          ('D', 'E', 1)
    #          ]
    graph = Graph(edges)
    # results=graph.traverse(mode='bfs')
    # """
    #  results = {"BFS_tree": T,
    #                    "dis": dis,
    #                    "pi": pi,
    #                    "order_list": order_list}
    # """
    # print(results['order_list'])
    results=graph.prim('s')
    # results = {"MST": T}
    print(results['MST'])



    #
    # print(graph.closeness_centrality())
