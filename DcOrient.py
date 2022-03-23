#Imports
import networkx as nx
import misc
import math
import random
from queue import PriorityQueue


class DincIndex:
    def __init__(self):
        self.cnt = {}
        self.cu = set({})


class DcOrientAlgo:
    def __init__(self, G: nx.Graph = nx.Graph()):
        self.G = G.copy()                                         # Undirected graph G
        self.Gstar = nx.DiGraph()                                 # Directed graph Gstar, used for everything within the algorithm

        self.Gstar.add_nodes_from(self.G.nodes())
        nx.set_node_attributes(self.Gstar, 0, 'color')                      # Reset all colors to 0
        for node in self.Gstar.nodes():
            self.Gstar.nodes[node]['DINC'] = DincIndex()               # Initialize all DINC indices

        for edge in self.G.edges():
            self.dcOrientInsert(edge[0], edge[1])


    def nodePriority(self, node):
        return (-1*self.Gstar.degree(node), list(self.Gstar.nodes()).index(node))


    # Returns wheter a comes before b in the ordering of nodes
    def isBefore(self, a, b):
        if self.nodePriority(a) < self.nodePriority(b):
            return True
        else:
            return False


    def collectColor(self, u):
        I = self.Gstar.nodes[u]['DINC']
        if len(I.cu) > 0:
            return min(I.cu)
        if I.cnt.get(self.Gstar.nodes[u]['color'], 0) != 0:
            for i in range(0, self.Gstar.in_degree(u) +1):
                if I.cnt.get(i, 0) == 0:
                    return i
        return None


    def assignColor(self, u, Cnew):
        for edge in self.Gstar.out_edges(u):
            v = edge[1]
            self.dincColorDecrease(v, u)
            self.dincColorIncrease(v, Cnew)
        self.Gstar.nodes[u]['color'] = Cnew
        self.Gstar.nodes[u]['DINC'].cu = set({})


    def notifyColor(self, u, Cold: int, q: PriorityQueue):
        for edge in self.Gstar.out_edges(u):
            v = edge[1]
            if not self.nodePriority(v) in q.queue and (self.Gstar.nodes[u]['color'] == self.Gstar.nodes[v]['color'] or Cold < self.Gstar.nodes[v]['color']):
                q.put((self.nodePriority(v), v))


    def CAN(self, q: PriorityQueue):
        while not q.empty():
            u = q.get()[1]
            Cnew = self.collectColor(u)
            if Cnew != None:
                Cold = self.Gstar.nodes[u]['color']
                self.assignColor(u, Cnew)
                self.notifyColor(u, Cold, q)


    def dincColorIncrease(self, u, v):
        I = self.Gstar.nodes[u]['DINC']
        c = self.Gstar.nodes[v]['color']
        if c <= self.Gstar.in_degree(u):
            if I.cnt.get(c, 0) != 0:
                I.cnt[c] += 1
            else:
                I.cnt[c] = 1
        if c in I.cu:
            I.cu.remove(c)


    def dincColorDecrease(self, u, v):
        I = self.Gstar.nodes[u]['DINC']
        c = self.Gstar.nodes[v]['color']
        if c <= self.Gstar.in_degree(u):
            if I.cnt.get(c, 1) != 1:
                I.cnt[c] += -1
            else:
                if c in I.cnt:
                    I.cnt.pop(c)
        if I.cnt.get(c, 0) == 0 and c < self.Gstar.nodes[u]['color']:
            I.cu.add(c)


    def ocgInsert(self, u, v):
        S = set({})
        S.add(u)
        S.add(v)

        self.Gstar.add_edge(u, v)

        for edge in list(self.Gstar.in_edges(u)).copy():
            nbr = edge[0]
            if self.isBefore(u, nbr):
                self.Gstar.remove_edge(nbr, u)
                self.Gstar.add_edge(u, nbr)
                self.dincColorIncrease(nbr, u)
                self.dincColorDecrease(u, nbr)
                S.add(nbr)
        
        for edge in list(self.Gstar.in_edges(v)).copy():
            nbr = edge[0]
            if self.isBefore(v, nbr):
                self.Gstar.remove_edge(nbr, v)
                self.Gstar.add_edge(v, nbr)
                self.dincColorIncrease(nbr, v)
                self.dincColorDecrease(v, nbr)
                S.add(nbr)
        self.dincColorIncrease(v, u)
        for edge in self.Gstar.in_edges(v):
            nbr = edge[0]
            if self.Gstar.nodes[nbr]['color'] == self.Gstar.in_degree(v):
                self.dincColorIncrease(v, nbr)
        return S


    def ocgDelete(self, u, v):
        S = set({})
        S.add(u)
        S.add(v)

        if not self.Gstar.has_edge(u, v):
            # If this edge is not in Gstar it must be present in the opposite direction
            x = u
            u = v
            v = x
        self.Gstar.remove_edge(u, v)

        for edge in list(self.Gstar.out_edges(u)).copy():
            nbr = edge[1]
            if self.isBefore(nbr, u):
                self.Gstar.remove_edge(u, nbr)
                self.Gstar.add_edge(nbr, u)
                self.dincColorIncrease(u, nbr)
                self.dincColorDecrease(nbr, u)
                S.add(nbr)
        
        for edge in list(self.Gstar.out_edges(v)).copy():
            nbr = edge[1]
            if self.isBefore(nbr, v):
                self.Gstar.remove_edge(v, nbr)
                self.Gstar.add_edge(nbr, v)
                self.dincColorIncrease(v, nbr)
                self.dincColorDecrease(nbr, v)
                S.add(nbr)
        self.dincColorDecrease(v, u)
        if self.Gstar.in_degree(v) + 1 in self.Gstar.nodes[v]['DINC'].cnt:
            self.Gstar.nodes[v]['DINC'].cnt.pop(self.Gstar.in_degree(v) + 1)
        return S


    def dcOrientInsert(self, u, v):
        q = PriorityQueue()
        S = self.ocgInsert(u, v)
        for w in S:
            q.put((self.nodePriority(w), w))
        self.CAN(q)


    def dcOrientDelete(self, u, v):
        q = PriorityQueue()
        S = self.ocgDelete(u, v)
        for w in S:
            q.put((self.nodePriority(w), w))
        self.CAN(q)

    
    # Returns a coloring dictionary from the nodes 'color' attributes
    def getColoring(self) -> dict:
        coloring: dict = {}
        for node in self.Gstar.nodes():
            coloring[node] = self.Gstar.nodes[node]['color']
        return coloring


    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.G.remove_edge(s, t)
        self.dcOrientDelete(s, t)

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return
        self.G.remove_node(v)
        self.Gstar.remove_node(v)

    def addEdge(self, s, t):

        if self.G.has_edge(s, t):    # Potentially redundant, but could be extended to also check if the vertices are present yet
            print("Edge already in the graph")
            return
        if (not self.G.has_node(s) or not self.G.has_node(t)):
            print("Not all nodes present in graph yet")
            return
        self.G.add_edge(s, t)
        self.dcOrientInsert(s,t)

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.G.add_node(v)
        self.Gstar.add_node(v)
        self.Gstar.nodes[v]['color'] = 0
        self.Gstar.nodes[v]['DINC'] = DincIndex()


    