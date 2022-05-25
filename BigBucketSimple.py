#Imports
import networkx as nx
import misc
import math
import random

class Bucket:

  vertices: set = set({})
  coloring: dict = {}

  def __init__(self, s, size, level):
      self.s = s
      self.size = size
      self.level = level

  def addVertices(self, G, newVertices):
    self.vertices = self.vertices.union(newVertices)
    for vertex in newVertices:
        G.nodes[vertex]['bucket'] = self

  def removeVertices(self, G, removeVertices):
    self.vertices = self.vertices.difference(removeVertices)
    for vertex in removeVertices:
        G.nodes[vertex]['bucket'] = None
        self.coloring.pop(vertex, None)


class BigBucketSimpleAlgo:
    def __init__(self, d, p, G: nx.Graph = nx.Graph()):
        self.G = G.copy()
        self.d = d                          # Amount of levels
        self.nr = self.G.number_of_nodes    # Initialize nr to 0
        self.staticColoring = {}            # Coloring at any moment
        self.bucketLevels = []
        self.p = p

        self.elemCounter = 0                        # Counter for elementary operations

        self.resetBuckets(self.G)

    # Returns whether there is still a non-full bucket on the requested level
    def isEmptyBucketOnLevel(self, level: int) -> bool:
        for j in range(0, len(self.bucketLevels[level])):
            bucket = self.bucketLevels[level-1][j]
            if len(bucket.vertices) <= pow(bucket.s, level) - pow(bucket.s, level-1):
                    return True
        return False


    # Empties all buckets on a level and returns the union of all vertices
    # Also ensures the colorings and vertex lists in the emptied buckets are reset
    def emptyLevel(self, level: int):
        vertices: set = set({})
        for bucket in self.bucketLevels[level-1]:
            vertices = vertices.union(bucket.vertices)
            bucket.removeVertices(self.G, bucket.vertices)
        return vertices

    
    # Creates brand new buckets with the correct sizes
    def resetBuckets(self, G: nx.Graph):
        nx.set_node_attributes(G, None, 'bucket')   # Reset all bucket references in G to None
        self.nr = G.number_of_nodes()    # Number of vertices in G
        s = math.ceil(pow(self.nr, 1/self.d)) # Amount of buckets per level
        s = max(1, s)               # To allow the algorithm to work with empty graphs as well

        # Create d levels of s buckets each, with capacity s^i per bucket, where i the level of the bucket
        self.bucketLevels = []
        for level in range(1, self.d):
            bucketLevel = []
            bucketLevel.append(Bucket(s, pow(s, level), level))
            self.bucketLevels.append(bucketLevel)
        self.bucketLevels.append([Bucket(s, self.nr, self.d)])
        
        self.staticColoring = nx.coloring.greedy_color(G)
        

    # Update bucket contents and recolor subgraphs
    def updateBuckets(self, b: Bucket):
        b = b
        i = 1
        while i < self.d:
            # If there is still an empty bucket on a level, this level does not need updating
            # Simply recompute the coloring of the most recent bucket and return
            if self.isEmptyBucketOnLevel(i):
                b.coloring = nx.coloring.greedy_color(self.G.subgraph(b.vertices))
                return
            else:
                # Else, empty all level i buckets into a single level i+1 bucket, update b to point at new bucket
                vertices = self.emptyLevel(i)   # Note that level i is stored at index i-1 by taking the nodes from the..
                b = self.bucketLevels[i][0]     # ..bucket on level i and moving them to the bucket at index i, we are moving them to the next level
                b.addVertices(self.G, vertices)
                i += 1
        self.resetBuckets(self.G)
        return

    # Do a random recolor step instead of bucket insertion
    def randomRecolor(self, v, b):
        g = self.G
        coloring = self.staticColoring
        if (b != None):
            g = self.G.subgraph(b.vertices)
            coloring = b.coloring

        occupiedColors: set = set({})
        for neighbor in list(g.neighbors(v)):
            occupiedColors.add(coloring.get(neighbor))

        colors: set = set({})
        for i in range(0, g.degree[v]+1):
            if i not in occupiedColors:
                colors.add(i)
        
        Cnew = random.choice(tuple(colors))
        coloring[v] = Cnew


    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.elemCounter = 0
        self.G.remove_edge(s, t)
        return self.elemCounter

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return

        self.elemCounter = 0
        b = self.G.nodes[v]['bucket']
        if b != None:
            b.removeVertices(self.G, [v])
        self.G.remove_node(v)
        self.staticColoring.pop(v, None)
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

        rb = random.uniform(0, 1) <= self.p
        if rb:
            sColor = self.staticColoring.get(s, None)
            tColor = self.staticColoring.get(t, None)
            if (self.G.nodes[s]['bucket'] == self.G.nodes[t]['bucket']):
                bucket = self.G.nodes[s]['bucket']
                if (bucket != None):
                    sColor = bucket.coloring.get(s)
                    tColor = bucket.coloring.get(t)
                if (sColor == tColor):
                    # Simply recolor one 
                    if bool(random.getrandbits(1)):
                        v = s
                    else:
                        v = t
                    b = bucket
                    self.randomRecolor(v, b)

        else:
            # Select one of the endpoints at random, remove it from a bucket and add it as usual
            if bool(random.getrandbits(1)):
                v = s
            else:
                v = t
                
            b = self.G.nodes[v]['bucket']
            if b != None:
                b.removeVertices(self.G, [v])
            self.staticColoring.pop(v, None)

            # Add vertex to an empty bucket
            bucket = self.bucketLevels[0][0]
            bucket.addVertices(self.G, [v])
            self.updateBuckets(bucket)
        return self.elemCounter

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.elemCounter = 0
        self.G.add_node(v)
        rb = random.uniform(0, 1) <= self.p
        if rb:
            self.randomRecolor(v)
        else:
            bucket = self.bucketLevels[0][0]
            bucket.addVertices(self.G, [v])
            self.updateBuckets(bucket)
        return self.elemCounter


    def getColoring(self):
        bucketColorings = [misc.useUniquePalette(self.staticColoring, 0)]
        i = 1
        for bucketLevel in self.bucketLevels:
            for bucket in bucketLevel:
                bucketColorings.append(misc.useUniquePalette(bucket.coloring, i))
                i += 1
        combinedColoring = misc.combineColoringsUnique(bucketColorings)   
        return combinedColoring     

    def printBucketLevels(self):
        for bl in self.bucketLevels:
            for b in bl:
                print("|  " + str(b.vertices) + "  |")
            print("-----------------------------------------------")
        return
    
