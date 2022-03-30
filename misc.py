import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import random
import math


def head(a: dict, i: int) -> dict:
    return dict(list(a.items())[0:i])


# Draws the graph in a safe fashion, with optional coloring and persistent layout parameters
def draw(G: nx.Graph, coloring: dict=None, pos: nx.layout=None):

    # Ensure layout exists
    if pos is None:
        pos = nx.spring_layout(G)

    if coloring is None:
        # Draw graph without colors if none were provided
        plt.figure()
        nx.draw(G, pos, with_labels=True)
    else:
        # Create drawable color_list from coloring in the right order
        drawableColoring = toDrawableColoring(coloring)
        color_list = []
        for node in G.nodes:
            color_list.append(drawableColoring.get(node))

        # Draw colored graph with color_list if colors were provided
        plt.figure()
        nx.draw(G, pos, node_color=color_list, with_labels=True)
        plt.show()


# Returns the number of colors used in a coloring
def numberOfColors(coloring: dict) -> int:
    # Create drawable color_list from coloring in the right order
    color_list = []
    for key in coloring.keys():
        color_list.append(coloring.get(key))
    return len(set(color_list))

# Find maximum degree of G
def getMaxDegree(G):
    maxDeg = 0
    degreeTuples = list(G.degree(list(G.nodes())))
    for tuple in degreeTuples:
        maxDeg = max(maxDeg, tuple[1])
    return maxDeg

# Find average degree of G
def getAverageDegree(G):
    totalDegree = 0
    degreeTuples = list(G.degree(list(G.nodes())))
    for tuple in degreeTuples:
        totalDegree += tuple[1]
    return totalDegree/len(degreeTuples)
    
# Subroutine for combineColorings that increases all values in a dictionary by an integer
# Note: modifies the original dictionary passed as parameter!
def increaseColorValues(coloring: dict, inc: int):
    for key in coloring.keys():
        coloring[key] = coloring[key] + inc


# Combines different coloring dictionaries by incrementing color values
# Intuitively this gives each coloring a unique set of colors to use

# DEPRECATED
def combineColoringsAdjacent(colorings):
    print("Using deprecated method combineColoringsAdjacent")
    # Initialize incremental counter with 0 and create empty dictionary
    inc = 0
    d = dict()
    for coloring in colorings:
        #Create copy to avoid changing original dicts
        copy = coloring.copy()
        # Add incremental counter to avoid overlap and increase counter for the next coloring
        increaseColorValues(copy, inc)
        inc = inc + numberOfColors(coloring)
        # Merge all dictionaries so far
        d.update(copy)
    
    # Return combined coloring
    return d

# Combines different coloring dictionaries by incrementing color values
# Intuitively this gives each coloring a unique set of colors to use
# This variation takes delta as parameter, which is the upper bound on the colors each subcoloring should be allowed to use
# By combining the colorings in this way, other subcolorings are not affected by changes in other subcolorings, making it more stable

# DEPRECATED
def combineColoringsStable(colorings, delta: int):
    print("Using deprecated method combineColoringsStable")
    # Initialize incremental counter with 0 and create empty dictionary
    inc = 0
    d = dict()
    for coloring in colorings:
        #Create copy to avoid changing original dicts
        copy = coloring.copy()
        # Add incremental counter to avoid overlap and increase counter for the next coloring
        increaseColorValues(copy, inc)
        if delta < numberOfColors(coloring):
            print("Incorrect upper bound passed")
        inc = inc + delta
        # Merge all dictionaries so far
        d.update(copy)
    
    # Return combined coloring
    return d

# Combines colorings that are already unique labeled
def combineColoringsUnique(colorings):
    d = dict()
    for coloring in colorings:
        d.update(coloring)
    return d


# Labels any coloring with level information
# Used to make the color pallete of each level unique
def useUniquePalette(coloring, level):
    uniqueColoring = coloring.copy()
    for key in coloring.keys():
        uniqueColoring[key] = 'L' + str(level) + 'C' + str(coloring[key])
    return uniqueColoring


# Converts any coloring to a drawable coloring by transforming non-integer values to integers
def toDrawableColoring(coloring):
    colorDict = {}
    i = 0
    for key in coloring.keys():
        if coloring[key] not in colorDict:
            colorDict[coloring[key]] = i
            i += 1
    
    drawableColoring = {}
    for key in coloring.keys():
        drawableColoring[key] = colorDict[coloring[key]]

    return drawableColoring


# Returns the number of recolors between two coloring dictionaries
# Does not count adding a new node as a recolor
def numberOfRecolors(c1: dict, c2: dict) -> int:
    rc = 0
    for key in c1.keys():
        if key in c2.keys():
            if c1[key] != c2[key]:
                rc += 1
    return rc


# Checks whether a coloring is indeed correct
# by iterating over all edges and verifying no two neighbors have the same color
def verifyColoring(G, coloring) -> bool:
    for edge in G.edges():
        n1 = edge[0]
        n2 = edge[1]
        if (not n1 in coloring) or (not n2 in coloring):
            print("Graph includes nodes not present in the coloring")
            return False
        if coloring.get(n1) == coloring.get(n2):
            return False
    return True
    

# Prints some graph information
def graphInfo(G):
    print("Nodes: " + str(G.number_of_nodes()))
    print("Edges: " + str(G.number_of_edges()))
    print("Density: " + str(nx.density(G)))
    print("Max Degree: " + str(getMaxDegree(G)))
    print("Average Degree: " + str(getAverageDegree(G)))
    print("Static Coloring uses " + str(numberOfColors(nx.coloring.greedy_color(G))) + " colors")


# Extracts updates from a (generated) graph G
# Sorted, random and skewed orderings are available
def extractUpdates(G, ordering=None):
    if ordering == None:
        ordering = 'random'
    selection = ['random', 'expanding', 'prioritized', 'shuffled', 'sorted']
    if ordering not in selection:
        raise ValueError("Invalid ordering choice. Expected one of: %s" % selection)

    # Get potential edges and nodes
    nodes = list(G.nodes())
    edges = list(G.edges())

    # Initialize empty update list
    updates = []

    # Depending on the selection made, fill update list in different order
    if ordering == 'sorted':
        updates = edges
    elif ordering == 'random':
        for i in range(0, len(edges)):
            edge = random.sample(edges, 1)[0]
            edges.remove(edge)
            updates.append(edge)
    elif ordering == 'expanding':
        # Make edges adjacent to nodes already in the graph have a higher probability of being chosen
        # Initialize weights fairly
        weights = []
        for i in range(0, len(edges)):
            weights.append(1)

        # Add edges one by one
        for i in range(0, len(edges)):
            edge = random.choices(edges, weights=weights, k=1)[0]
            index = edges.index(edge)
            edges.remove(edge)
            weights.pop(index)
            updates.append(edge)

            # Update weights
            for i in range(0, len(weights)):
                if edge[0] in edges[i]:
                    weights[i] += 2000                             # Scaling is possible here, but has little effect
                if edge[1] in edges[i]:
                    weights[i] += 2000
    elif ordering == 'prioritized':
        # Get priority for nodes   
        priorities = []
        for i in range(0, len(nodes)):
            priorities.append(int(random.uniform(1, 100)))          # Perhaps scaling is possible here

        while len(edges) > 0:
            # Pick a random node
            node = random.choices(nodes, weights=priorities, k=1)[0]
            # Get all edges for that node
            nodeEdges = []
            for edge in edges:
                if node in edge:
                    nodeEdges.append(edge)
            if len(nodeEdges) == 0:
                # This node has no edges left, remove it from the selection set
                priorities.pop(nodes.index(node))
                nodes.remove(node)
            else:
                # Select random edge from nodeEdges
                edge = random.sample(nodeEdges, 1)[0]
                # Add edge to updates and remove edge from remaining edges
                updates.append(edge)
                edges.remove(edge)
    elif ordering == 'shuffled':
        p = 0.6
        freeIndices = []

        for i in range(0, len(edges)):
            updates.append(None)
            freeIndices.append(i)

        copiedEdges = edges.copy()
        for edge in copiedEdges:
            if random.uniform(0, 1) > p:
                # Keep position same
                index = copiedEdges.index(edge)
                updates[index] = edge
                edges.remove(edge)
                freeIndices.remove(index)
        
        for edge in edges:
            # Give remaining edges a position in the update sequence at random
            index = random.sample(freeIndices, 1)[0]
            updates[index] = edge
            freeIndices.remove(index)

    return updates


# Iterates over a list of updates, for easier testing
# Can be extended to work with updates other than edge insertions as well
class UpdateIterator:
    def __init__(self, algo, updates):
        self.algo = algo
        self.updateIterator = iter(updates)
    
    # Uses the given algorithm to run the next i updates
    def runUpdate(self, i):
        for x in range(0, i):
            update = next(self.updateIterator, None)
            if update == None:
                #print("No more updates in given update sequence")
                return False
            else:
                self.algo.addEdge(update[0], update[1])
        return True


# Function to read the reddit database from the text file
# Access edges and vertices using misc.edges and misc.vertices
def readRedditData():
    file = open('data/reddit_edges.txt', 'r')
    global edges
    edges = []
    for line in file.readlines():
        edges.append((line.split()[0], line.split()[1]))
    file.close()
    file = open('data/reddit_vertices.txt', 'r')
    global vertices
    vertices = []
    for line in file.readlines():
        vertices.append(line.strip())
    file.close()


# Creates a random graph with parameters to adjust size, density, max degree and the variation present in these values
def createRandomGraph(size=30, density=0.5, variation=0.5, maxDegree=None, sizeVariation=None, densityVariation=None, maxDegreeVariation=None, prioritized=False):

    G = nx.Graph() 

    # Variation parameters decide how much randomness is used in the generation of the graph
    # There is a general variation parameter and three specific ones: if the specific variation is None, it is assigned the general variation
    # Variation must be between 0 and 1, where 0 means no variation and 1 means the values may vary as much as the value itself (thus, range from 0 to 2*value)
    if sizeVariation == None:
        sizeVariation = variation
    if densityVariation == None:
        densityVariation = variation
    if maxDegreeVariation == None:
        maxDegreeVariation = variation
    
    # Do some input tests to see if parameters are correct
    if size < 0 or density < 0 or density > 1 or \
        variation < 0 or variation > 1 or \
        sizeVariation < 0 or sizeVariation > 1 or \
        densityVariation < 0 or densityVariation > 1 or \
        maxDegreeVariation < 0 or maxDegreeVariation > 1:
            print("Incorrect parameter passed, returning empty graph")
            return G

    # Finalize values for graph creation by using randomness
    fSizeVariation = random.uniform(-sizeVariation, sizeVariation)
    fSize = int(max(2, size + (fSizeVariation*size)))
    
    densityRange = (max(0, density-densityVariation*density), min(1, density+densityVariation*density))
    fDensity = random.uniform(densityRange[0], densityRange[1])
    fEdges = int(fDensity * fSize*(fSize-1) / 2)
    fDensity = 2*fEdges / (fSize*(fSize-1))

    fMaxDegree = None
    if maxDegree != None:
        # Potentially inaccurate lower/upper bounds
        maxDegreeRange = (max(math.ceil(fDensity*(fSize-1)), min(min(fSize-1, fEdges), maxDegree-maxDegreeVariation*maxDegree))), min(min(fSize-1, fEdges), max(math.ceil(fDensity*(fSize-1)), maxDegree+maxDegreeVariation*maxDegree))
        if maxDegree < maxDegreeRange[0] or maxDegree > maxDegreeRange[1]:
            print("Chosen max degree does not fall into range (" + str(math.ceil(fDensity*(fSize-1))) + ", " + str(min(fSize-1, fEdges)) + ") permitted by other parameters, so picking closest value instead")
        fMaxDegree = int(random.uniform(maxDegreeRange[0], maxDegreeRange[1]))

    # Start creation of the graph using finalized parameters
    # Create the graphs vertices
    for i in range(0, fSize):
        G.add_node(i)

    allEdges = []
    for i in range(0, fSize):
        for j in range(0, fSize):
            if i > j:
                allEdges.append((i,j))

    # Create the graphs edges
    edgeSet = []

    #If we want prioritized nodes, disregard max degree parameter
    if prioritized:
        priorities = []
        for i in range(0, len(allEdges)):
            priorities.append(random.uniform(0, 1))
        
        remainingEdges = fEdges

        while remainingEdges > 0:
            edge = random.sample(allEdges, 1)[0]
            index = allEdges.index(edge)

            if random.uniform(0, 1) < priorities[index]:
                edgeSet.append(edge)
                allEdges.remove(edge)
                priorities.pop(index)
                remainingEdges -= 1

    # If we require a certain max degree first ensure one node fulfills this requirement
    elif fMaxDegree != None:

        # Create an array which keeps track of the current degree of each node
        degreeCounter = []
        for i in range(0, fSize):
            degreeCounter.append(0)
        
        # Pick one node to give max degree
        node = random.randint(0, fSize-1)

        # Get all potential edges for this node and select the correct amount of them
        maxNodeEdges = []
        for edge in allEdges:
            if node in edge:
                maxNodeEdges.append(edge)
        edgeSet = random.sample(maxNodeEdges, fMaxDegree)
        degreeCounter[node] = fMaxDegree    # Update the selected node counter
        for edge in maxNodeEdges:           # Remove all edges connected to the selected node from the available edge set
            allEdges.remove(edge)

        # For the remaining edges, select at random while keeping track of counters
        remainingEdges = fEdges - fMaxDegree
        while remainingEdges > 0:
            edge = random.sample(allEdges, 1)[0]
            if degreeCounter[edge[0]] < fMaxDegree and degreeCounter[edge[1]] < fMaxDegree:
                edgeSet.append(edge)
                degreeCounter[edge[0]] += 1
                degreeCounter[edge[1]] += 1
                remainingEdges -= 1
            allEdges.remove(edge)

    # If the max degree is not specified simply select the correct amount of random edges
    else:
        edgeSet = random.sample(allEdges, fEdges)

    G.add_edges_from(edgeSet)

    return G