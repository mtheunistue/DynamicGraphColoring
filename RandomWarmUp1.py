#Imports
import networkx as nx
import misc
import math
import random


class WarmUp1Algo:
    def __init__(self, G: nx.Graph = nx.Graph()):
        self.G = nx.Graph()        

        self.changeCounter = 0                      # Initialize changeCounter to 0
        nx.set_node_attributes(G, 0, 'color')       # Reset all colors to 0
        nx.set_node_attributes(G, 0, 'changed')     # Reset all change integers to 0

        # Initialize graph by adding nodes and edges one by one
        for node in G.nodes():
            self.addVertex(node)
        for edge in G.edges():
            self.addEdge(edge[0], edge[1])
            

    # Randomly recolors a node with a color none of its neighbours have
    def recolor(self, node):
        self.changeCounter += 1      # update change counter
        self.G.nodes[node]['changed'] = self.changeCounter

        # Create set of all colors occupied by neighbours
        neighbors = list(self.G.neighbors(node))
        occupiedColors: set = set({})
        for neighbor in neighbors:
            occupiedColors.add(self.G.nodes[neighbor]['color'])

        # Create set of all available colors to this node
        colors: set = set({})
        for i in range(0, self.G.degree[node]+1):
            if i not in occupiedColors:
                colors.add(i)
        
        # Select random color from available colors
        self.G.nodes[node]['color'] = random.choice(tuple(colors))


    # Methods for possible updates
    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.G.remove_edge(s, t)

    def removeVertex(self, v):
        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return
        self.G.remove_node(v)

    def addEdge(self, s, t):
        if self.G.has_edge(s, t):    # Potentially redundant, but could be extended to also check if the vertices are present yet
            print("Edge already in the graph")
            return
        if (not self.G.has_node(s) or not self.G.has_node(t)):
            print("Not all nodes present in graph yet")
            return

        self.G.add_edge(s, t)

        # Check if colors of endpoints are the same, if so, choose a new color for one of the neighbours
        # Recolor the neighbor that has most recently been recolored. If this value is the same (only possible on 'new' nodes) pick one at random
        if self.G.nodes[s]['color'] == self.G.nodes[t]['color']:
            if self.G.nodes[s]['changed'] > self.G.nodes[t]['changed']:
                self.recolor(s)
            elif self.G.nodes[t]['changed'] > self.G.nodes[s]['changed']:
                self.recolor(t)
            elif bool(random.getrandbits(1)):
                self.recolor(s)
            else:
                self.recolor(t)


    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.G.add_node(v)
        self.G.nodes[v]['color'] = 0
        self.G.nodes[v]['changed'] = 0


    # Returns a coloring dictionary from the nodes 'color' attributes
    def getColoring(self) -> dict:
        coloring: dict = {}
        for node in self.G.nodes():
            coloring[node] = self.G.nodes[node]['color']
        return coloring