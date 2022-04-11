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


class DcSimpleAlgo:
    def __init__(self, G: nx.Graph = nx.Graph(), p: int = 0.5):
        self.G = G.copy()                                         # Undirected graph G
        self.Gstar = nx.DiGraph()                                 # Directed graph Gstar, used for everything within the algorithm
        self.changeCounter = 0                                    # Initialize changeCounter to 0
        self.p = p                                                # Probability of taking a random step

        self.elemCounter = 0                        # Counter for elementary operations

        self.Gstar.add_nodes_from(self.G.nodes())
        nx.set_node_attributes(self.Gstar, 0, 'color')                      # Reset all colors to 0
        nx.set_node_attributes(self.Gstar, 0, 'changed')               # Reset all change counters to 0
        for node in self.Gstar.nodes():
            self.Gstar.nodes[node]['DINC'] = DincIndex()               # Initialize all DINC indices

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
            self.dincColorIncrease(v, c=Cnew)
        self.Gstar.nodes[u]['color'] = Cnew
        self.Gstar.nodes[u]['DINC'].cu.clear()
        self.changeCounter += 1      # update change counter
        self.Gstar.nodes[u]['changed'] = self.changeCounter


    def notifyColor(self, u, Cold: int, q: PriorityQueue):
        for edge in self.Gstar.out_edges(u):
            v = edge[1]
            if (not (self.nodePriority(v), v) in q.queue) and (self.Gstar.nodes[u]['color'] == self.Gstar.nodes[v]['color'] or Cold < self.Gstar.nodes[v]['color']):
                q.put((self.nodePriority(v), v))


    def CAN(self, q: PriorityQueue):
        while not q.empty():
            u = q.get()[1]
            Cnew = self.collectColor(u)
            if Cnew != None:
                Cold = self.Gstar.nodes[u]['color']
                self.assignColor(u, Cnew)
                self.notifyColor(u, Cold, q)


    def dincColorIncrease(self, u, v=None, c=None):
        self.elemCounter += 1
        I = self.Gstar.nodes[u]['DINC']
        if v != None:
            c = self.Gstar.nodes[v]['color']
        elif c == None:
            return
        # if c <= self.Gstar.in_degree(u):          # REMOVED TO FIX BUG
        if I.cnt.get(c, 0) != 0:
            I.cnt[c] += 1
        else:
            I.cnt[c] = 1
        if c in I.cu:
            I.cu.remove(c)


    def dincColorDecrease(self, u, v):
        self.elemCounter += 1
        I = self.Gstar.nodes[u]['DINC']
        c = self.Gstar.nodes[v]['color']
       
        # if c <= self.Gstar.in_degree(u):          # REMOVED TO FIX BUG
        if I.cnt.get(c, 0) > 0:
            I.cnt[c] = I.cnt[c]-1
        if I.cnt.get(c, 0) == 0:
            if c in I.cnt:
                I.cnt.pop(c)
       
        if I.cnt.get(c, 0) == 0 and c < self.Gstar.nodes[u]['color']:
            I.cu.add(c)


    def ocgInsert(self, u, v):
        S = set({})
        S.add(u)
        S.add(v)

        uEdges = list(self.Gstar.in_edges(u)).copy()
        vEdges = list(self.Gstar.in_edges(v)).copy()

        self.Gstar.add_edge(u, v)

        for edge in uEdges:
            nbr = edge[0]
            if self.isBefore(u, nbr):
                self.Gstar.remove_edge(nbr, u)
                self.Gstar.add_edge(u, nbr)
                self.dincColorIncrease(nbr, u)
                self.dincColorDecrease(u, nbr)
                S.add(nbr)
        
        for edge in vEdges:
            nbr = edge[0]
            if self.isBefore(v, nbr):
                self.Gstar.remove_edge(nbr, v)
                self.Gstar.add_edge(v, nbr)
                self.dincColorIncrease(nbr, v)
                self.dincColorDecrease(v, nbr)
                S.add(nbr)
        self.dincColorIncrease(v, u)
        # for edge in self.Gstar.in_edges(v):                                               # REMOVED TO FIX BUG
        #     nbr = edge[0]
        #     if nbr != u and self.Gstar.nodes[nbr]['color'] == self.Gstar.in_degree(v):
        #         self.dincColorIncrease(v, nbr)
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
        # if self.Gstar.in_degree(v) + 1 in self.Gstar.nodes[v]['DINC'].cnt:                        # REMOVED TO FIX BUG
        #     self.Gstar.nodes[v]['DINC'].cnt.pop(self.Gstar.in_degree(v) + 1)
        return S


    def dcOrientInsert(self, u, v):
        b = random.uniform(0, 1) <= self.p
        if b:
            if self.isBefore(u, v):
                S = self.ocgInsert(u, v)
            else:
                S = self.ocgInsert(v, u)
            # Check if colors of endpoints are the same, if so, choose a new color for one of the neighbours
            # Recolor the neighbor that has most recently been recolored. If this value is the same (only possible on 'new' nodes) pick one at random
            if self.Gstar.nodes[u]['color'] == self.Gstar.nodes[v]['color']:
                if self.Gstar.nodes[u]['changed'] > self.Gstar.nodes[v]['changed']:
                    self.recolor(u)
                elif self.Gstar.nodes[v]['changed'] > self.Gstar.nodes[u]['changed']:
                    self.recolor(v)
                elif bool(random.getrandbits(1)):
                    self.recolor(u)
                else:
                    self.recolor(v)
        else:
            q = PriorityQueue()
            if self.isBefore(u, v):
                S = self.ocgInsert(u, v)
            else:
                S = self.ocgInsert(v, u)
            for w in S:
                q.put((self.nodePriority(w), w))
            self.CAN(q)


    def dcOrientDelete(self, u, v):
        q = PriorityQueue()
        S = self.ocgDelete(u, v)
        for w in S:
            q.put((self.nodePriority(w), w))
        self.CAN(q)

    def recolor(self, node):
        self.changeCounter += 1      # update change counter
        self.Gstar.nodes[node]['changed'] = self.changeCounter

        # Create set of all colors occupied by neighbours
        neighbors = list(self.G.neighbors(node))
        occupiedColors: set = set({})
        for neighbor in neighbors:
            occupiedColors.add(self.Gstar.nodes[neighbor]['color'])

        # Create set of all available colors to this node
        colors: set = set({})
        for i in range(0, self.Gstar.degree[node]+1):
            if i not in occupiedColors:
                colors.add(i)

        # Select random color from available colors
        Cnew = random.choice(tuple(colors))

        # Update DINC-Index
        for edge in self.Gstar.out_edges(node):
            nbr = edge[1]
            self.dincColorDecrease(nbr, node)
            self.dincColorIncrease(nbr, c=Cnew)
        self.Gstar.nodes[node]['color'] = Cnew

    # Returns a coloring dictionary from the nodes 'color' attributes
    def getColoring(self) -> dict:
        coloring: dict = {}
        for node in self.Gstar.nodes():
            coloring[node] = self.Gstar.nodes[node]['color']
        return coloring


    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            return
        self.elemCounter = 0
        self.G.remove_edge(s, t)
        self.dcOrientDelete(s, t)
        return self.elemCounter

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            return
        self.elemCounter = 0
        self.G.remove_node(v)
        self.Gstar.remove_node(v)
        return self.elemCounter

    def addEdge(self, s, t):

        if self.G.has_edge(s, t):    # Potentially redundant, but could be extended to also check if the vertices are present yet
            return
        if (not self.G.has_node(s) or not self.G.has_node(t)):

            return
        self.elemCounter = 0
        self.G.add_edge(s, t)
        self.dcOrientInsert(s,t)
        return self.elemCounter

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            return
        self.elemCounter = 0
        self.G.add_node(v)
        self.Gstar.add_node(v)
        self.Gstar.nodes[v]['color'] = 0
        self.Gstar.nodes[v]['DINC'] = DincIndex()
        return self.elemCounter


    