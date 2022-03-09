#Imports
import networkx as nx
import misc
import math
import random

class Bucket:

  vertices: set = set({})
  coloring: dict = {}

  def __init__(self, size, level):
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


class SmallBucketAlgo:
    def __init__(self, d):
        self.G = nx.Graph()  # The complete graph
        self.d = d           # Amount of levels
        self.staticColoring = {}  # Coloring at any moment
        self.bucketLevels = []
        self.resetBuckets(self.G)

    
    # Returns whether there is still an empty bucket on the requested level
    # Also returns the index of this bucket, if applicable
    def isEmptyBucketOnLevel(self, level: int) -> tuple[bool, int]:
        for j in range(0, len(self.bucketLevels[level])):
            bucket = self.bucketLevels[level][j]
            if len(bucket.vertices) == 0:
                    return (True, j)
        return (False, -1)


    # Empties all buckets on a level and returns the union of all vertices
    # Also ensures the colorings and vertex lists in the emptied buckets are reset
    def emptyLevel(self, level: int):
        vertices: set = set({})
        for bucket in self.bucketLevels[level]:
            vertices = vertices.union(bucket.vertices)
            bucket.removeVertices(self.G, bucket.vertices)
        return vertices

    
    # Creates brand new buckets with the correct sizes
    def resetBuckets(self, G: nx.Graph):
        nx.set_node_attributes(G, None, 'bucket')   # Reset all bucket references in G to None
        nr = G.number_of_nodes()    # Number of vertices in G
        s = math.ceil(pow(nr, 1/self.d)) # Amount of buckets per level
        s = max(1, s)               # To allow the algorithm to work with empty graphs as well

        # Create d levels of s buckets each, with capacity s^i per bucket, where i the level of the bucket
        self.bucketLevels = []
        for level in range(0, self.d):
            bucketLevel = []
            for b in range(0, s):
                bucketLevel.append(Bucket(pow(s, level), level))
            self.bucketLevels.append(bucketLevel)
        self.bucketLevels.append([Bucket(nr, self.d)])
        
        self.staticColoring = nx.coloring.greedy_color(G)
        

    # Update bucket contents and recolor subgraphs
    def updateBuckets(self, b: Bucket):
        b = b
        i = 0
        while i < self.d:
            # If there is still an empty bucket on a level, this level does not need updating
            # Simply recompute the coloring of the most recent bucket and return
            if self.isEmptyBucketOnLevel(i)[0]:
                b.coloring = nx.coloring.greedy_color(self.G.subgraph(b.vertices))
                return
            else:
                # Else, empty all level i buckets into a single level i+1 bucket, update b to point at new bucket
                vertices = self.emptyLevel(i)
                b = self.bucketLevels[i+1][self.isEmptyBucketOnLevel(i+1)[1]]
                b.addVertices(self.G, vertices)
                i += 1
        self.resetBuckets(self.G)
        return


    def removeEdge(self, s, t):
        if not self.G.has_edge(s, t):    # Potentially redundant
            print("Edge not present in graph")
            return
        self.G.remove_edge(s, t)

    def removeVertex(self, v):

        if not self.G.has_node(v):   # Potentially redundant
            print("Node not present in graph")
            return

        b = self.G.nodes[v]['bucket']
        if b != None:
            b.removeVertices(self.G, [v])
        self.G.remove_node(v)

    def addEdge(self, s, t):

        if self.G.has_edge(s, t):    # Potentially redundant, but could be extended to also check if the vertices are present yet
            print("Edge already in the graph")
            return
        if (not self.G.has_node(s) or not self.G.has_node(t)):
            print("Not all nodes present in graph yet")
            return


        self.G.add_edge(s, t)
        # Select one of the endpoints at random, remove it from a bucket and add it as usual
        if bool(random.getrandbits(1)):
            v = s
        else:
            v = t
            
        b = self.G.nodes[v]['bucket']
        if b != None:
            b.removeVertices(self.G, [v])
        
        # Add vertex to an empty bucket
        bucket = self.bucketLevels[0][self.isEmptyBucketOnLevel(0)[1]]
        bucket.addVertices(self.G, [v])
        self.updateBuckets(bucket)

    def addVertex(self, v):
        if self.G.has_node(v):   # Potentially redundant, depending on the input used during the experiments
            print("Node already present in graph")
            return
        self.G.add_node(v)
        bucket = self.bucketLevels[0][self.isEmptyBucketOnLevel(0)[1]]
        bucket.addVertices(self.G, [v])
        self.updateBuckets(bucket)


    def getColoring(self):
        bucketColorings = [self.staticColoring]
        for bucketLevel in self.bucketLevels:
            for bucket in bucketLevel:
                bucketColorings.append(bucket.coloring)
        combinedColoring = misc.combineColorings(bucketColorings)   
        return combinedColoring     


    def printBucketLevels(self):
        for bl in self.bucketLevels:
            for b in bl:
                print("|  " + str(b.vertices) + "  |")
            print("-----------------------------------------------")
        return
    
