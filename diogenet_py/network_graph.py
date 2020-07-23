"""Module to handle Complex Networks Graph relations in ancient Greece.

.. platform:: Unix, Windows, Mac
.. moduleauthor:: Elio Linarez <elinarezv@gmail.com>
"""

import igraph
import pandas as pd
import numpy as np
from dataclasses import dataclass
import data_access as da


#  This module must create a graph given a set of nodes and edges
#  The set of nodes and edges will be pandas data frames
#  I need to see how to handle the locations
#  Because locations are related to nodes
#  In this map_graph nodes are locations and edges are people traveling
#  from one location to another 

# In case local or url method define file names
TRAVELS_BLACK_LIST_FILE = "travels_blacklist.csv"
LOCATIONS_DATA_FILE = "locations_data.csv"
NODES_DATA_FILE = "new_nodes.csv"
EDGES_DATA_FILE = "new_edges.csv"
# These are the files already processed. Must be created "on the fly"
TRAVEL_EDGES_FILE = "travel_edges_graph.csv"
ALL_PLACES_FILE = "all_places_graph.csv"

DATA_ACCESS_METHOD = "url"
# In case url define BASE_URL
BASE_URL = "https://diogenet.ucsd.edu/data"

#  Create a dataframe from csv
#travel_edges =  pd.read_csv("travel_edges_graph.csv", delimiter=',')
travel_edges = da.get_data_entity(TRAVEL_EDGES_FILE, "local")
#all_places = pd.read_csv("all_places_graph.csv", delimiter=',')
all_places = da.get_data_entity(ALL_PLACES_FILE, "local")

#print("travel_edges")
#print(travel_edges)

# User list comprehension to create a list of lists from Dataframe rows
list_of_rows_travel_edges = [list(row[1:]) for row in travel_edges.values]
list_of_rows_all_places = [list(row[1:2]) for row in all_places.values]

# Print list of lists i.e. rows
#print("list_of_rows_travel_edges")
#print(list_of_rows_travel_edges)
#print("list_of_rows_all_places")
#print(list_of_rows_all_places)

@dataclass
class map_graph:
    #  nodes: pd.DataFrame
    #  edges: pd.DataFrame
    #  locations: pd.DataFrame
    #  The graph must receive the roor files as input.     
    def __init__(self, nodes, edges, locations):
        self.nodes_file = nodes
        self.edges_file = edges
        self.locations_file = locations
        self.igraph_map = igraph.Graph.TupleList(list_of_rows_travel_edges, directed=True, edge_attrs = ['edge_name'])
            
    def know_locations(self):
        return pd.DataFrame()

    # Now all the functions that implement data treatment should be implemented
    def function_1(self):
        return()

    def function_2(self):
        return()

    def function_3(self):
        return()

    def function_4(self):
        return()

grafo = map_graph(NODES_DATA_FILE, EDGES_DATA_FILE, LOCATIONS_DATA_FILE)

print(grafo.edges_file)
print(grafo.nodes_file)
print(grafo.locations_file)

#nodes = VertexSeq(grafo)

#print("grafo.igraph_map")
#print(grafo.igraph_map)
#print("grafo.igraph_map.vs")
#print(grafo.igraph_map.vs)

#for v in grafo.igraph_map.vs: 
#    print("v")
#    print(v)

#for e in grafo.igraph_map.es: 
#    print("e")
#    print(e)    
