#Imports
import networkx as nx
import misc
import math
import random


class WarmUp2Algo:
    def __init__(self, G: nx.Graph = nx.Graph()):
        self.G = G                                  # Initial graph
        self.changeCounter = 0                      # Initialize changeCounter to 0
        
        nx.set_node_attributes(G, 0, 'color')       # Reset all colors to 0
        nx.set_node_attributes(G, 0, 'changed')     # Reset all change integers to 0

        # Initialize graph nodes by setting their colors correctly
        initColoring = nx.coloring.greedy_color(G)
        for node in G.nodes():
            G.nodes[node]['color'] = initColoring[node]
    

    # Randomly recolors a node with a color none of its neighbors have
    def recolor(self, node):
        self.changeCounter += 1      # update change counter
        self.G.nodes[node]['changed'] = self.changeCounter

        # Create set of all colors occupied by at least two neighbors and a set of all colors occupied by neighbors
        neighbors = list(self.G.neighbors(node))
        occupiedColors: set = set({})
        doubleOccupiedColors: set = set({})
        for neighbor in neighbors:
            color = self.G.nodes[neighbor]['color']
            if color in occupiedColors:
                doubleOccupiedColors.add(color)
            occupiedColors.add(color)

        uniqueColors = occupiedColors.difference(doubleOccupiedColors)  # Get the colors that are occupied by only a single neighbor

        # Create set of all available blank colors to this node
        blankColors: set = set({})
        for i in range(0, self.G.degree[node]+1):
            if i not in occupiedColors:
                blankColors.add(i)

        colors = blankColors.union(uniqueColors)    # Get all available colors

        # Select random color from available colors
        pickedColor = random.choice(tuple(colors))
        self.G.nodes[node]['color'] = pickedColor

        # If a color occupied by a neighbor was picked, recursively recolor this neighbor
        if pickedColor in uniqueColors:
            for neighbor in neighbors:
                if self.G.nodes[neighbor]['color'] == pickedColor:
                    self.recolor(neighbor)
                    break



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