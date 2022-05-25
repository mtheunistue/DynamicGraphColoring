#Imports
from types import DynamicClassAttribute
import networkx as nx
import misc
import math
import random
import time
import RandomWarmUp1

class StaticGreedyAlgo:
    def __init__(self, G: nx.Graph = nx.Graph(), l=5):
        self.G = G.copy()   # Graph to be used
        self.staticColoring = {}

        self.fullReset()


    def fullReset(self):
        self.staticColoring = nx.coloring.greedy_color(self.G)


    # Returns a coloring dictionary by combining the two available colorings
    def getColoring(self) -> dict:
        return self.staticColoring.copy()


    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.elemCounter = 0
        self.G.remove_edge(s, t)
        self.fullReset()
        return self.elemCounter

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return
        self.elemCounter = 0
        self.G.remove_node(v)
        self.fullReset()
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
        self.fullReset()
        return self.elemCounter 

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.elemCounter = 0
        self.G.add_node(v)
        self.fullReset()
        return self.elemCounter