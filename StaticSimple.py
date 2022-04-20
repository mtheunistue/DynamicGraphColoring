#Imports
from types import DynamicClassAttribute
import networkx as nx
import misc
import math
import random
import time
import RandomWarmUp1

class StaticSimpleAlgo:
    def __init__(self, G: nx.Graph = nx.Graph(), l=5):
        self.l = l          # Number of updates per segment, segment length
        self.G = G.copy()   # Graph to be used
        self.staticColoring = {}
        self.activeLevel = 0

        nx.set_node_attributes(self.G, 0, 'recentDegree')       # Reset all recent degrees to 0

        Gp = nx.Graph()                     # Sparse version of graph G
        Gp.add_nodes_from(self.G.nodes())   # Initialize with only nodes and no edges

        self.elemCounter = 0                        # Counter for elementary operations

        self.fullReset()


    # Runs the static black-box algorithm on subgraph G with color palette of 'level'
    # Automatically updates the staticColoring variable
    def staticBlackBox(self, g, level):
        newStaticColoring = misc.useUniquePalette(nx.coloring.greedy_color(g), level)
        self.staticColoring.update(newStaticColoring)

        for node in g.nodes(): 
            self.G.nodes[node]['recentDegree'] = 0         # Reset all recent degees of nodes in g to 0
        
        self.levels[level] =  (set({}), self.levels[level][1])       # Remove all nodes from the current level node set


    # Resets all variables, only called during initialization and when the end of the segment at level 0 is reached
    def fullReset(self):
        #print("full reset")
        self.c = 0

        self.maxLevel = int(math.log(self.G.number_of_nodes(), 2))  # Calculate number of levels required, assumes number of vertices is static

        self.levels = []
        for level in range(0, self.maxLevel+1):                
            rLevel = set({})                                 # Initialize vertex sets per level for vertices with highest recent degrees
            self.levels.append((rLevel, True))               # Initialize all levels as active

        self.staticBlackBox(self.G, 0)                            # Color full graph using static black box with level 0 color palette

    
    # General update step called in every update
    # Keeps track of the vertices with max recent degree and counter c
    def updateStep(self, addedEdge=None):
        self.c = (self.c+1) % self.l
        activeNodes = set({})
        activeEdges = set({})
        if addedEdge != None:
            activeEdges.add(addedEdge)
        if self.c == 0:

            self.activeLevel = 0
            for i in reversed(range(0, self.maxLevel+1)):    # Get active level
                if self.levels[i][1]:
                    self.activeLevel = i
                    break
        
            if self.activeLevel == 0:
                self.fullReset()                                                                             # Run static black box on everything and reset
            else:
                activeNodes = self.levels[self.activeLevel][0]
                self.staticBlackBox(self.G.subgraph(activeNodes), self.activeLevel)     # Run static black box on selected subgraph
                self.levels[self.activeLevel] = (self.levels[self.activeLevel][0], False)                    # Deactivate this level
                for i in range(self.activeLevel + 1, self.maxLevel + 1):                                     # Reactivate all levels higher than current level
                    self.levels[i] = (self.levels[i][0], True)

        # Resolve remaining conflicts
        for node in activeNodes:
            for edge in self.G.edges(node):
                activeEdges.add(edge)

    
        for edge in activeEdges:
            timer = time.perf_counter()
            if self.staticColoring.get(edge[0]) == self.staticColoring.get(edge[1]):
                self.elemCounter += (time.perf_counter() - timer)
                if bool(random.getrandbits(1)):
                    # Recolor first node
                    self.recolor(edge[0])
                else:
                    # Recolor second node
                    self.recolor(edge[1])
            else:
                self.elemCounter += (time.perf_counter() - timer)

    def recolor(self, node):
        # Create set of all colors occupied by neighbours
        timer = time.perf_counter()
        neighbors = list(self.G.neighbors(node))
        occupiedColors: set = set({})
        for neighbor in neighbors:
            occupiedColors.add(self.staticColoring.get(neighbor))

        # Create set of all available colors to this node
        colors: set = set({})
        for i in range(0, self.G.degree[node]+1):
            if i not in occupiedColors:
                colors.add(i)

        self.elemCounter += (time.perf_counter() - timer)
        # Select random color from available colors
        self.staticColoring[node] = random.choice(tuple(colors))


    # Returns a coloring dictionary by combining the two available colorings
    def getColoring(self) -> dict:
        return self.staticColoring.copy()


    # Print the current situation of the leveled segment data structure
    def printLevels(self):
        print("l: " + str(self.l))
        print("c: " + str(self.c))
        print("Last Updated Level: " + str(self.activeLevel))
        print("Max Level: " + str(self.maxLevel))

    
    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.elemCounter = 0
        self.G.remove_edge(s, t)
        #self.updateStep()                 # Does not count as an update
        return self.elemCounter

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return
        self.elemCounter = 0
        self.G.remove_node(v)
        #self.updateStep()                 # Does not count as an update
        return self.elemCounter

    def addEdge(self, s, t):

        if self.G.has_edge(s, t):    # Potentially redundant, but could be extended to also check if the vertices are present yet
            print("Edge already in the graph")
            return
        if (not self.G.has_node(s) or not self.G.has_node(t)):
            print("Not all nodes present in graph yet")
            return

        self.elemCounter = 0
        self.G.add_edge(s, t)

        # Increase recent degree of endpoints
        self.G.nodes[s]['recentDegree'] += 1
        self.G.nodes[t]['recentDegree'] += 1

        # Add node with highest recent degree to active level node sets
        if self.G.number_of_nodes() > 0:
            rd = -1
            n = None
            for node in self.G.nodes():
                if self.G.nodes[node]['recentDegree'] > rd:
                    rd = self.G.nodes[node]['recentDegree']
                    n = node
            for level in self.levels:
                if level[1]:
                    level[0].add(n)

        self.updateStep(addedEdge=(s, t))                # Run update step in which the static algorithm is potentially ran

        return self.elemCounter 

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.elemCounter = 0
        self.G.add_node(v)
        self.staticColoring[v] = 'L0C0'
        self.G.nodes[v]['recentDegree'] = 0
        self.DBB.addVertex(v)
        #self.updateStep()                 # Does not count as an update
        return self.elemCounter