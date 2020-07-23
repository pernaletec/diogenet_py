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

############
#####
##
# Source data configuration
##
#####
############

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

## This is referential these structures must be created departing from the root files
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

    def __init__(self, nodes_file, edges_file, locations_file):
        """Create parameters for the class graph 

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param igraph_map: Python igraph graph object
          
        """
        #:return: 
        #:rtype: :py:class:`pd.DataFrame`
        
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.locations_file = locations_file

        self.nodes_raw_data = None
        self.edges_raw_data = None
        self.location_raw_data = None

        self.igraph_map = None        
        self.know_locations()
        self.set_locations("local")
        self.set_nodes("local")
        self.set_edges("local")

    def know_locations(self):
        return pd.DataFrame()

    # Now all the functions that implement data treatment should be implemented
    def set_locations(self, method):
        self.location_raw_data = da.get_data_entity(self.locations_file, method)
        print("self.location_raw_data")
        print(self.location_raw_data)

    def set_nodes(self, method):
        self.nodes_raw_data = da.get_data_entity(self.nodes_file, method)
        print("self.nodes_raw_data")
        print(self.nodes_raw_data)
        
    def set_edges(self, method):
        self.edges_raw_data = da.get_data_entity(self.edges_file, method)
        print("self.edges_raw_data")
        print(self.edges_raw_data)

    def validate_nodes_edges(self):
        return()

    def validate_nodes_locations(self):
        return()    

    def update_graph(self):
        self.igraph_map = igraph.Graph.TupleList(list_of_rows_travel_edges, directed=True, edge_attrs = ['edge_name'])

    def calculate_degree(self):
        return()    

    def calculate_closeness(self):
        return()            

    def calculate_betweenness(self):
        return()    

    def calculate_eigenvectos(self):
        return()            

    def set_colour_scale(self):
        return()            

grafo = map_graph(NODES_DATA_FILE, EDGES_DATA_FILE, LOCATIONS_DATA_FILE)

#print(grafo.nodes_raw_data)
#print(grafo.edges_raw_data)
#print(grafo.location_raw_data)

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
