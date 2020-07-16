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


# User list comprehension to create a list of lists from Dataframe rows
list_of_rows_travel_edges = [list(row) for row in travel_edges.values]
list_of_rows_all_places = [list(row) for row in all_places.values]

# Print list of lists i.e. rows
print(list_of_rows_travel_edges)
print(list_of_rows_all_places)

@dataclass
class map_graph:
    #  nodes: pd.DataFrame
    #  edges: pd.DataFrame
    #  locations: pd.DataFrame
    #     
    def __init__(self, nodes, edges, locations):
        self.nodes = nodes
        self.edges = edges
        self.locations = locations
        self.igraph_map = igraph.Graph.TupleList(list_of_rows_travel_edges, directed=True)

    def know_locations(self):
        return pd.DataFrame()

grafo = map_graph(1, 2, 3)

#  print(grafo.igraph_map)
