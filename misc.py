import networkx as nx
import matplotlib
import matplotlib.pyplot as plt


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

