"""Module to handle Complex Networks Graph relations in ancient Greece.

.. platform:: Unix, Windows, Mac
.. moduleauthor:: Elio Linarez <elinarezv@gmail.com>
"""

import igraph
import pandas as pd
import numpy as np
from dataclasses import dataclass
import data_access as da
# import cairocffi

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
NODES_DATA_FILE = "new_Nodes.csv"
EDGES_DATA_FILE = "new_Edges.csv"
# These are the files already processed. Must be created "on the fly"
TRAVEL_EDGES_FILE = "travel_edges_graph.csv"
ALL_PLACES_FILE = "all_places_graph.csv"

DATA_ACCESS_METHOD = "url"
# In case url define BASE_URL
BASE_URL = "https://diogenet.ucsd.edu/data"

## This is referential these structures must be created departing from the root files
#  Create a dataframe from csv
travel_edges =  pd.read_csv("travel_edges_graph.csv", delimiter=',')
travel_edges = da.get_data_entity(TRAVEL_EDGES_FILE, "local")
#all_places = pd.read_csv("all_places_graph.csv", delimiter=',')
#all_places = da.get_data_entity(ALL_PLACES_FILE, "local")

#print("travel_edges")
#print(travel_edges)

# User list comprehension to create a list of lists from Dataframe rows
list_of_rows_travel_edges = [list(row[1:]) for row in travel_edges.values]
#list_of_rows_all_places = [list(row[1:2]) for row in all_places.values]

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

    def __init__(self, nodes_file, edges_file, locations_file, blacklist_file):
        """Create parameters for the class graph 

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param blacklist_file: File with list of blacklisted places (.csv)
        
        :param nodes_raw_data: Raw data for nodes
        :param edges_raw_data: Raw data for edges
        :param location_raw_data: Raw data for locations
        :param blacklist_raw_data: Raw data for blacklisted places 

        :param igraph_map: Python igraph graph object

        :param phylosophers_known_origin: Data for phylosophers and their origin
        :param multi_origin_phylosophers: List of phylosophers with more than one origin "is from"  
        
        :param nodes_graph_data: Nodes data processed for graph 
        :param edges_graph_data: Edges data processed for graph
        :param locations_graph_data: Locations data processed for graph
        :param travels_graph_data: Full data for graph including edges names, phylosopher name and coordinates 

        :param located_nodes: Nodes with an identified location in locations data

        """
        #:return: 
        #:rtype: :py:class:`pd.DataFrame`
        
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.locations_file = locations_file
        self.blacklist_file = blacklist_file

        self.nodes_raw_data = None
        self.edges_raw_data = None
        self.location_raw_data = None
        self.blacklist_raw_data = None
        self.igraph_map = None

        self.phylosophers_known_origin = None
        self.multi_origin_phylosophers = None  
        
        self.nodes_graph_data = None
        self.edges_graph_data = None
        self.locations_graph_data = None
        self.travels_graph_data = None

        self.located_nodes = None

        #self.know_locations()
        
        self.set_locations("local")
        self.set_nodes("local")
        self.set_edges("local")
        self.set_blacklist("local")

        self.validate_nodes_locations()
        self.validate_phylosopher_origin()
        self.validate_travels_locations()
        self.create_edges_for_graph()

        self.update_graph()

        self.calculate_degree()
        self.calculate_betweenness()
        self.calculate_closeness()
        self.calculate_eigenvector()

    def know_locations(self):
        """Create parameters for the class graph 

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param igraph_map: Python igraph graph object
          
        """
        print("def know_locations(self): Not implemented")
        return pd.DataFrame()

    # Now all the functions that implement data treatment should be implemented
    def set_locations(self, method):
        """Retrieve and store locations data in the graph object 
        :param method: Declare the source of data  ('local'/'url')
          
        """
        self.location_raw_data = da.get_data_entity(self.locations_file, method)
        #print("self.location_raw_data")
        #print(self.location_raw_data)

    def set_nodes(self, method):
        """Retrieve and store nodes data in the graph object 
        :param method: Declare the source of data  ('local'/'url')
          
        """
        self.nodes_raw_data = da.get_data_entity(self.nodes_file, method)
        #print("self.nodes_raw_data")
        #print(self.nodes_raw_data)
        
    def set_edges(self, method):
        """Retrieve and store edges data in the graph object 
        :param method: Declare the source of data  ('local'/'url')

        """
        self.edges_raw_data = da.get_data_entity(self.edges_file, method)
        #print("self.edges_raw_data")
        #print(self.edges_raw_data)

    def set_blacklist(self, method):
        """Retrieve and store blacklist of travelers (impossible travelers!) 
        :param method: Declare the source of data  ('local'/'url')

        """
        self.blacklist_raw_data = da.get_data_entity(self.blacklist_file, method)
        #print("self.blacklist_raw_data")
        #print(self.blacklist_raw_data)

    def validate_nodes_locations(self):
        """Determine if places in nodes have the corresponding location and update located nodes           

        """
        node_place = self.nodes_raw_data['Groups'] == 'Place' 
        self.located_nodes = self.nodes_raw_data.loc[node_place,]
        located_nodes_bool = self.located_nodes.Name.isin(self.location_raw_data.name)
        self.located_nodes = self.located_nodes.loc[located_nodes_bool,] 

        #print(node_place)
        #print(self.located_nodes)
        #print(located_places)
        #located_nodes = node_place.name.isin(located_places.name).astype(bool)
        #print(located_nodes)

    def validate_travels_locations(self):
        """Filter edges (travels) where travelers have unidentified origin (no coordinates)
        
        """
        traveled_to_edges = self.edges_raw_data.Relation == 'traveled to' 
        #print("traveled_to_edges")
        #print(traveled_to_edges)

        #print("self.edges_raw_data[traveled_to_edges,")
        #print(self.edges_raw_data[traveled_to_edges])

        names_in_traveled_to = self.edges_raw_data.loc[traveled_to_edges,'Source']
        destiny_in_traveled_to = self.edges_raw_data.loc[traveled_to_edges,'Target']
        #print("names_in_traveled_to")
        #print(names_in_traveled_to)

        #print("destiny_in_traveled_to")
        #print(destiny_in_traveled_to)

        names_in_traveled_to_blacklisted =  names_in_traveled_to.isin(self.blacklist_raw_data)
        #print("names_in_traveled_to_blacklisted")
        #print(names_in_traveled_to_blacklisted)
        
        names_in_traveled_to = names_in_traveled_to[-names_in_traveled_to_blacklisted]
        destiny_in_traveled_to = destiny_in_traveled_to[-names_in_traveled_to_blacklisted]
        #print("names_in_traveled_to")
        #print(names_in_traveled_to)
        #print("destiny_in_traveled_to")
        #print(destiny_in_traveled_to)

        #print("self.phylosophers_known_origin")
        #print(self.phylosophers_known_origin)

        #print("len(self.phylosophers_known_origin)")
        #print(len(self.phylosophers_known_origin))

        #print("len(names_in_traveled_to)")
        #print(len(names_in_traveled_to))
        
        #located_names_in_traveled_to_ = any(True for x in self.phylosophers_known_origin if x in names_in_traveled_to)

        #print("located_names_in_traveled_to_")
        #print(located_names_in_traveled_to_)

        pko = np.array(self.phylosophers_known_origin.name)
        #print("pko")
        #print(pko)

        ntt = np.array(names_in_traveled_to)
        #print("ntt")
        #print(ntt)    

        located_names_in_traveled_to = names_in_traveled_to.isin(pko)
        
        #print("located_names_in_traveled_to")
        #print(located_names_in_traveled_to)

        names_in_traveled_to = names_in_traveled_to[located_names_in_traveled_to]
        destiny_in_traveled_to = destiny_in_traveled_to[located_names_in_traveled_to]

        #print("names_in_traveled_to")
        #print(names_in_traveled_to)
        #print("destiny_in_traveled_to")
        #print(destiny_in_traveled_to)
 
        located_destiny_in_traveled_to = destiny_in_traveled_to.isin(self.located_nodes.Name)
        #print("located_destiny_in_traveled_to")
        #print(located_destiny_in_traveled_to)
        
        names_in_traveled_to = names_in_traveled_to[located_destiny_in_traveled_to]
        destiny_in_traveled_to = destiny_in_traveled_to[located_destiny_in_traveled_to]
        list_of_tuples = list(zip(names_in_traveled_to, destiny_in_traveled_to))  
        #print(list_of_tuples)
        self.travels_graph_data = pd.DataFrame(list_of_tuples,columns = ['Source','Target'])
        #print("self.edges_graph_data")
        #print(self.edges_graph_data)

    def validate_phylosopher_origin(self):
        """Filter "is from" edges where the target (place) is unidentified (no coordinates)
        
        """ 
        is_from_edges = self.edges_raw_data.Relation == 'is from' 
        names_in_is_from = self.edges_raw_data.loc[is_from_edges,'Source']
        origin_in_is_from = self.edges_raw_data.loc[is_from_edges,'Target']
        located_origin_in_is_from = origin_in_is_from.isin(self.located_nodes.Name)        
        origin_in_is_from = origin_in_is_from[located_origin_in_is_from]
        names_in_is_from = names_in_is_from[located_origin_in_is_from]

        list_of_tuples = list(zip(names_in_is_from, origin_in_is_from))  
        #print(list_of_tuples)

        self.phylosophers_known_origin = pd.DataFrame(list_of_tuples,columns = ['name','origin'])

        #print("self.phylosophers_known_origin")
        #print(self.phylosophers_known_origin)

        #print(type(origin_in_is_from))
        #self.located_edges_raw_data[]

    def create_edges_for_graph(self):
        """Create Data Frame with all edge's data for graph construction  
          
        """
        traveler_origin = []
        lat_source = []
        lon_source = []
        lat_target = []
        lon_target = []
        multi_origin = [] # Phylosopher with more than one origin city
 
        #print("self.location_raw_data.name")
        #print(self.location_raw_data.name)

        for idx, cell in enumerate(self.travels_graph_data.Source):
            
            current_origin = pd.Series.to_list(self.phylosophers_known_origin.origin[self.phylosophers_known_origin.name == cell])

            current_destiny = self.travels_graph_data.Target[idx]
            
            if len(current_origin) > 1:
                current_origin = current_origin[0]
                multi_origin.append(cell)
            traveler_origin.append(current_origin) 
            
            current_origin = "".join(current_origin) 

            self.multi_origin_phylosophers = multi_origin
            
            lat_source.append(pd.Series.to_list(self.location_raw_data.lat[self.location_raw_data.name.isin([current_origin])]))
            lon_source.append(pd.Series.to_list(self.location_raw_data.lon[self.location_raw_data.name.isin([current_origin])]))
            lat_target.append(pd.Series.to_list(self.location_raw_data.lat[self.location_raw_data.name.isin([current_destiny])]))
            lon_target.append(pd.Series.to_list(self.location_raw_data.lon[self.location_raw_data.name.isin([current_destiny])]))

        source = traveler_origin
        target = pd.Series.to_list(self.travels_graph_data.Target)
        name = pd.Series.to_list(self.travels_graph_data.Source)

        #print(type(source))
        #print(type(target))
        #print(type(name))
        #print(type(lat_source))
        #print(type(lon_source))
        #print(type(lat_target))
        #print(type(lon_target))
        

        list_of_tuples = list(zip(source, target, name, lat_source, lon_source, lat_target, lon_source))  

        list_of_tuples_ = [list(row[1:]) for row in list_of_tuples]

        #print("list_of_tuples_")
        #print(list_of_tuples_)
        self.travels_graph_data = list_of_tuples_
        #self.travels_graph_data = pd.DataFrame(list_of_tuples,columns = ['source','target','name','lat_source','lon_source','lat_target','lon_target'])

        #print("self.travels_graph_data")
        #print(self.travels_graph_data)
    
    def update_graph(self):
        """Create graph once defined source data  
          
        """
        self.igraph_map = igraph.Graph.TupleList(self.travels_graph_data, directed=False, edge_attrs = ['edge_name'])
        #self.igraph_map = igraph.Graph.TupleList(list_of_rows_travel_edges, directed=True, edge_attrs = ['edge_name'])
        #print(self.igraph_map)

        #for a in self.igraph_map.vs:
        #    print(a)
        layout = self.igraph_map.layout("kk")
        #self.igraph_map.plot(self.igraph_map, layout = layout)
        
        #self.igraph_map.plot(layout = layout)
        # Not being able to plot. Something with cairo

    def calculate_degree(self):
        """Calculate degree for the graph 

        :param self: The graph object
          
        """        

        degree = self.igraph_map.degree()
        #print("degree")
        #print(degree)
        # degree   betweenness(weights='weight')    

    def calculate_closeness(self):
        """Create closeness for the graph 

        :param self: The graph object
          
        """        

        closeness = self.igraph_map.closeness()
        #print("closeness")
        #print(closeness)

    def calculate_betweenness(self):
        """Calculate betweenness for the graph 

        :param self: The graph object
          
        """        

        betweenness = self.igraph_map.betweenness()
        #print("betweenness")
        #print(betweenness)

    def calculate_eigenvector(self):
        """Create degree for the graph 

        :param self: The graph object
          
        """        
        eigenvector = self.igraph_map.evcent()
        #print("eigenvector")
        #print(eigenvector)

    def set_colour_scale(self):
        """Create parameters for the class graph 

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param igraph_map: Python igraph graph object
          
        """
        return()            

grafo = map_graph(NODES_DATA_FILE, EDGES_DATA_FILE, LOCATIONS_DATA_FILE, TRAVELS_BLACK_LIST_FILE)


#print(grafo.travels_graph_data)

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
