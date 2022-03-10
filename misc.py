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
        color_list = []
        for node in G.nodes:
            color_list.append(coloring.get(node))

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


# Subroutine for combineColorings that increases all values in a dictionary by an integer
# Note: modifies the original dictionary passed as parameter!
def increaseColorValues(coloring: dict, inc: int):
    for key in coloring.keys():
        coloring[key] = coloring[key] + inc


# Combines different coloring dictionaries by incrementing color values
# Intuitively this gives each coloring a unique set of colors to use
def combineColorings(colorings):
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
def combineColoringsStable(colorings, delta: int):
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

