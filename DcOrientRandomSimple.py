#Imports
import networkx as nx
import misc
import math
import random
from queue import PriorityQueue


class DcOrientRandomSimpleAlgo:
    def __init__(self, G: nx.Graph = nx.Graph(), p = 0.5):                         # Initial graph
        self.changeCounter = 0                      # Initialize changeCounter to 0
        self.p = p                                  # Probability of randomizing color instead of using priority ordering
        
        self.Gstar = nx.DiGraph()

        self.Gstar.add_nodes_from(G.nodes())
        nx.set_node_attributes(self.Gstar, 0, 'color')                 # Reset all colors to 0
        nx.set_node_attributes(self.Gstar, 0, 'changed')               # Reset all change counters to 0
        self.G = nx.Graph()
        self.G.add_nodes_from(G.nodes())
        self.G.add_edges_from(G.edges())

        for edge in self.G.edges():
            if self.isBefore(edge[0], edge[1]):
                self.Gstar.add_edge(edge[0], edge[1])
            else:
                self.Gstar.add_edge(edge[1], edge[0])

        # Initialize graph nodes by setting their colors correctly
        initColoring = nx.coloring.greedy_color(self.Gstar)
        for node in self.Gstar.nodes():
            self.Gstar.nodes[node]['color'] = initColoring[node]


    def nodePriority(self, node):
        return (-1*self.Gstar.degree(node), list(self.Gstar.nodes()).index(node))


    # Returns wheter a comes before b in the ordering of nodes
    def isBefore(self, a, b):
        if self.nodePriority(a) < self.nodePriority(b):
            return True
        else:
            return False

    def collectColor(self, u):
        C = set({})
        for edge in self.Gstar.in_edges(u):
            v = edge[0]
            C.add(self.Gstar.nodes[v]['color'])
        return C


    def assignColor(self, u, C):
        colorNew = None
        for i in range(0, self.Gstar.degree(u) + 1):
            if i not in C:
                colorNew = i
                break
        if self.Gstar.nodes[u]['color'] != colorNew:
            self.Gstar.nodes[u]['color'] = colorNew
            return True
        else:
            return False

    def notifyColor(self, u, b: bool, q: PriorityQueue):
        if b:
            for edge in self.Gstar.out_edges(u):
                v = edge[1]
                if not self.nodePriority(v) in q.queue:
                    q.put((self.nodePriority(v), v))

    def CAN(self, q: PriorityQueue):
        while not q.empty():
            u = q.get()[1]
            C = self.collectColor(u)
            b = self.assignColor(u, C)
            self.notifyColor(u, b, q)

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
                S.add(nbr)
        
        for edge in list(self.Gstar.in_edges(v)).copy():
            nbr = edge[0]
            if self.isBefore(v, nbr):
                self.Gstar.remove_edge(nbr, v)
                self.Gstar.add_edge(v, nbr)
                S.add(nbr)
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
                S.add(nbr)
        
        for edge in list(self.Gstar.out_edges(v)).copy():
            nbr = edge[1]
            if self.isBefore(nbr, v):
                self.Gstar.remove_edge(v, nbr)
                self.Gstar.add_edge(nbr, v)
                S.add(nbr)
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
        self.Gstar.nodes[v]['changed'] = 0