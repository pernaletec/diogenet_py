"""Module to handle Complex Networks Graph relations in ancient Greece.
    This module must create a graph given a set of nodes and edges
    The set of nodes and edges will be pandas data frames
    In this map_graph nodes are locations and edges are people traveling
    from one location to another

.. platform:: Unix, Windows, Mac
.. moduleauthor:: César Pernalete <pernalete.cg@gmail.com>
"""

import igraph
import pyvis
import json
import copy
import pandas as pd
import numpy as np
import networkx as nx
from dataclasses import dataclass
from . import data_access as da
import random

# import cairocffi
#  I need to see how to handle the locations
#  Because locations are related to nodes


############
#####
##
# Source data configuration
##
#####
############

# In case local or url method define file names
GRAPH_TYPE = "global"
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

# This is referential these structures must be created departing from the root files
#  Create a dataframe from csv
travel_edges = pd.read_csv("travel_edges_graph.csv", delimiter=",")
travel_edges = da.get_data_entity(TRAVEL_EDGES_FILE, "local")
# all_places = pd.read_csv("all_places_graph.csv", delimiter=',')
# all_places = da.get_data_entity(ALL_PLACES_FILE, "local")
# User list comprehension to create a list of lists from Dataframe rows
list_of_rows_travel_edges = [list(row[1:]) for row in travel_edges.values]
# list_of_rows_all_places = [list(row[1:2]) for row in all_places.values]

VIRIDIS_COLORMAP = [
    (68, 1, 84),
    (72, 40, 120),
    (62, 74, 137),
    (49, 104, 142),
    (38, 130, 142),
    (31, 158, 137),
    (53, 183, 121),
    (109, 205, 89),
    (180, 222, 44),
    (253, 231, 37),
]


@dataclass
class diogenetGraph:

    graph_type = None

    nodes_file = None
    edges_file = None
    locations_file = None
    blacklist_file = None
    current_edges = None

    nodes_raw_data = None
    edges_raw_data = None
    location_raw_data = None
    blacklist_raw_data = None
    igraph_graph = None
    igraph_subgraph = None

    phylosophers_known_origin = None
    multi_origin_phylosophers = None

    graph_layout = None
    graph_layout_name = "None"
    Xn = []
    Yn = []

    # Estetic's attributes (plot attribs)
    node_min_size = 4
    node_max_size = 6
    label_min_size = 4
    label_max_size = 6
    current_centrality_index = "Degree"
    graph_color_map = VIRIDIS_COLORMAP
    vertex_filter = None

    nodes_graph_data = pd.DataFrame()
    edges_graph_data = pd.DataFrame()
    locations_graph_data = pd.DataFrame()
    travels_graph_data = None
    travels_subgraph_data = pd.DataFrame()

    located_nodes = None

    def __init__(
        self,
        graph_type=GRAPH_TYPE,
        nodes_file=NODES_DATA_FILE,
        edges_file=EDGES_DATA_FILE,
        locations_file=LOCATIONS_DATA_FILE,
        blacklist_file=TRAVELS_BLACK_LIST_FILE,
    ):
        """Create parameters for the class graph

        :param graph_type: It defines the type of the graph (map, global, local, communities)
        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param blacklist_file: File with list of blacklisted places (.csv)
        :param vertex_filter: Array with the vertex that will  be used to
        create the subgraph

        :param nodes_raw_data: Raw data for nodes
        :param edges_raw_data: Raw data for edges
        :param location_raw_data: Raw data for locations
        :param blacklist_raw_data: Raw data for blacklisted places

        :param igraph_graph: Python igraph graph object
        :param igraph_graph: Python igraph sub-graph object

        :param phylosophers_known_origin: Data for phylosophers and their origin
        :param multi_origin_phylosophers: List of phylosophers with more than one
        origin "is from"

        :param nodes_graph_data: Nodes data processed for graph
        :param edges_graph_data: Edges data processed for graph
        :param locations_graph_data: Locations data processed for graph
        :param travels_graph_data: Full data for graph including edges names,
        phylosopher name and coordinates
        :param travels_subgraph_data: Full data for subgraph including edges names,
        phylosopher name and coordinates

        :param located_nodes: Nodes with an identified location in locations data

        """
        # :return:
        # :rtype: :py:class:`pd.DataFrame`

        self.graph_type = graph_type
        self.nodes_file = nodes_file
        self.edges_file = edges_file
        self.locations_file = locations_file
        self.blacklist_file = blacklist_file

        self.edges_filter = []

        # self.know_locations()

        self.set_locations("local")
        self.set_nodes("local")
        self.set_edges("local")
        self.set_blacklist("local")

        if self.graph_type == "map":
            self.validate_nodes_locations()
            self.validate_phylosopher_origin()
            self.validate_travels_locations()

        self.create_edges_for_graph()
        self.update_graph()
        self.create_subgraph()
        self.tabulate_subgraph_data()

    def know_locations(self):
        """Create parameters for the class graph

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param igraph_graph: Python igraph graph object

        """
        print("def know_locations(self): Not implemented")
        return pd.DataFrame()

    # Now all the functions that implement data treatment should be implemented
    def set_locations(self, method):
        """Retrieve and store locations data in the graph object
        :param method: Declare the source of data  ('local'/'url')

        """
        self.location_raw_data = da.get_data_entity(self.locations_file, method)

    def set_nodes(self, method):
        """Retrieve and store nodes data in the graph object
        :param method: Declare the source of data  ('local'/'url')

        """
        self.nodes_raw_data = da.get_data_entity(self.nodes_file, method)

    def set_edges(self, method):
        """Retrieve and store edges data in the graph object
        :param method: Declare the source of data  ('local'/'url')

        """
        self.edges_raw_data = da.get_data_entity(self.edges_file, method)

    def set_blacklist(self, method):
        """Retrieve and store blacklist of travelers (impossible travelers!)
        :param method: Declare the source of data  ('local'/'url')

        """
        self.blacklist_raw_data = da.get_data_entity(self.blacklist_file, method)

    def validate_nodes_locations(self):
        """Determine if places in nodes have the corresponding location
        and update located nodes

        """
        node_place = self.nodes_raw_data["Groups"] == "Place"
        self.located_nodes = self.nodes_raw_data.loc[
            node_place,
        ]
        located_nodes_bool = self.located_nodes.Name.isin(self.location_raw_data.name)
        self.located_nodes = self.located_nodes.loc[
            located_nodes_bool,
        ]

    def validate_travels_locations(self):
        """Filter edges (travels) where travelers have unidentified origin (no coordinates)

        """
        traveled_to_edges = self.edges_raw_data.Relation == "traveled to"
        names_in_traveled_to = self.edges_raw_data.loc[traveled_to_edges, "Source"]
        destiny_in_traveled_to = self.edges_raw_data.loc[traveled_to_edges, "Target"]

        names_in_traveled_to_blacklisted = names_in_traveled_to.isin(
            self.blacklist_raw_data
        )
        names_in_traveled_to = names_in_traveled_to[-names_in_traveled_to_blacklisted]
        destiny_in_traveled_to = destiny_in_traveled_to[
            -names_in_traveled_to_blacklisted
        ]

        pko = np.array(self.phylosophers_known_origin.name)
        ntt = np.array(names_in_traveled_to)
        located_names_in_traveled_to = names_in_traveled_to.isin(pko)
        names_in_traveled_to = names_in_traveled_to[located_names_in_traveled_to]
        destiny_in_traveled_to = destiny_in_traveled_to[located_names_in_traveled_to]
        located_destiny_in_traveled_to = destiny_in_traveled_to.isin(
            self.located_nodes.Name
        )
        names_in_traveled_to = names_in_traveled_to[located_destiny_in_traveled_to]
        destiny_in_traveled_to = destiny_in_traveled_to[located_destiny_in_traveled_to]
        list_of_tuples = list(zip(names_in_traveled_to, destiny_in_traveled_to))

        self.travels_graph_data = pd.DataFrame(
            list_of_tuples, columns=["Source", "Target"]
        )

    def validate_phylosopher_origin(self):
        """Filter "is from" edges where the target (place) is unidentified (no coordinates)

        """
        is_from_edges = self.edges_raw_data.Relation == "is from"
        names_in_is_from = self.edges_raw_data.loc[is_from_edges, "Source"]
        origin_in_is_from = self.edges_raw_data.loc[is_from_edges, "Target"]
        located_origin_in_is_from = origin_in_is_from.isin(self.located_nodes.Name)
        origin_in_is_from = origin_in_is_from[located_origin_in_is_from]
        names_in_is_from = names_in_is_from[located_origin_in_is_from]

        list_of_tuples = list(zip(names_in_is_from, origin_in_is_from))
        self.phylosophers_known_origin = pd.DataFrame(
            list_of_tuples, columns=["name", "origin"]
        )

    def create_edges_for_graph(self):
        """Create Data Frame with all edge's data for graph construction

        """

        traveler_origin = []
        lat_source = []
        lon_source = []
        lat_target = []
        lon_target = []
        multi_origin = []  # Phylosopher with more than one origin city
        Source = []
        Target = []
        Relation = []

        if self.graph_type == "map":
            for idx, cell in enumerate(self.travels_graph_data.Source):
                current_origin = pd.Series.to_list(
                    self.phylosophers_known_origin.origin[
                        self.phylosophers_known_origin.name == cell
                    ]
                )
                current_destiny = self.travels_graph_data.Target[idx]
                current_origin = current_origin[0]
                if len(current_origin) > 1:
                    # If the traveler shows multiple origins by default the
                    multi_origin.append(cell)
                traveler_origin.append(current_origin)
                current_origin = "".join(current_origin)
                self.multi_origin_phylosophers = multi_origin
                lat_source.append(
                    pd.Series.to_list(
                        self.location_raw_data.lat[
                            self.location_raw_data.name.isin([current_origin])
                        ]
                    )
                )
                lon_source.append(
                    pd.Series.to_list(
                        self.location_raw_data.lon[
                            self.location_raw_data.name.isin([current_origin])
                        ]
                    )
                )
                lat_target.append(
                    pd.Series.to_list(
                        self.location_raw_data.lat[
                            self.location_raw_data.name.isin([current_destiny])
                        ]
                    )
                )
                lon_target.append(
                    pd.Series.to_list(
                        self.location_raw_data.lon[
                            self.location_raw_data.name.isin([current_destiny])
                        ]
                    )
                )

            source = traveler_origin
            target = pd.Series.to_list(self.travels_graph_data.Target)
            name = pd.Series.to_list(self.travels_graph_data.Source)

            list_of_tuples = list(
                zip(
                    source, target, name, lat_source, lon_source, lat_target, lon_target
                )
            )
            list_of_tuples_ = list(list(row[0:]) for row in list_of_tuples)
            self.travels_graph_data = list_of_tuples_

        if self.graph_type == "global":
            node_list = self.nodes_raw_data[
                (self.nodes_raw_data.Groups == "Male")
                | (self.nodes_raw_data.Groups == "Female")
            ]
            edges = self.edges_raw_data[
                (self.edges_raw_data.Relation == "is teacher of")
                | (self.edges_raw_data.Relation == "is teacher of")
                | (self.edges_raw_data.Relation == "is friend of")
                | (self.edges_raw_data.Relation == "is family of")
                | (self.edges_raw_data.Relation == "studied the work of")
                | (self.edges_raw_data.Relation == "sent letters to")
                | (self.edges_raw_data.Relation == "is benefactor of")
            ]
            source = edges["Source"]
            target = edges["Target"]
            name = edges["Relation"]
            self.current_edges = name.unique()
            list_of_tuples = list(zip(source, target, name))
            list_of_tuples_ = list(list(row[0:]) for row in list_of_tuples)
            self.travels_graph_data = list_of_tuples_

        return self.travels_graph_data

    def update_graph(self):
        """Create graph once defined source data
        """
        if self.travels_graph_data is not None:
            self.igraph_graph = igraph.Graph.TupleList(
                self.travels_graph_data, directed=False, edge_attrs=["edge_name"]
            )

    def calculate_degree(self):
        """Calculate degree for the graph
        """
        if self.igraph_graph is not None:
            return self.igraph_graph.degree()

    def calculate_closeness(self):
        """Create closeness for the graph
        """
        if self.igraph_graph is not None:
            return self.igraph_graph.closeness()

    def calculate_betweenness(self):
        """Calculate betweenness for the graph
        """
        if self.igraph_graph is not None:
            return self.igraph_graph.betweenness()

    def calculate_eigenvector(self):
        """Create degree for the graph
        """
        if self.igraph_graph is not None:
            return self.igraph_graph.evcent()

    def centralization_degree(self):
        """Calculate unnormalized centralization degree for the graph
        """
        if self.igraph_graph is not None:
            degree = self.calculate_degree()
            max_degree = max(degree)
            cent_degree = 0
            for centrality in degree:
                cent_degree = cent_degree + (max_degree - centrality)
            return cent_degree

    def centralization_betweenness(self):
        """Calculate unnormalized centralization betweenness for the graph
        """
        if self.igraph_graph is not None:
            betweenness = self.calculate_betweenness()
            max_betweenness = max(betweenness)
            cent_betweenness = 0
            for centrality in betweenness:
                cent_betweenness = cent_betweenness + (max_betweenness - centrality)
            return cent_betweenness

    def centralization_closeness(self):
        """Calculate unnormalized centralization closeness for the graph
        """
        if self.igraph_graph is not None:
            closeness = self.calculate_closeness()
            max_closeness = max(closeness)
            cent_closeness = 0
            for centrality in closeness:
                cent_closeness = cent_closeness + (max_closeness - centrality)
            return cent_closeness

    def centralization_eigenvector(self):
        """Calculate unnormalized centralization eigen vector for the graph
        """
        if self.igraph_graph is not None:
            eigenvector = self.calculate_eigenvector()
            max_eigenvector = max(eigenvector)
            cent_eigenvector = 0
            for centrality in eigenvector:
                cent_eigenvector = cent_eigenvector + (max_eigenvector - centrality)
            return cent_eigenvector

    def get_vertex_names(self):
        """Return names for each vertex of the graph
        """
        if self.igraph_graph is not None:
            vertex_names = []
            for vertex in self.igraph_graph.vs:
                vertex_names.append(vertex["name"])
            return vertex_names

    def get_max_min(self):
        if self.igraph_graph is not None:
            centrality_indexes = []
            ret_val = {}
            if self.current_centrality_index == "Degree":
                centrality_indexes = self.calculate_degree()
            elif self.current_centrality_index == "Betweeness":
                centrality_indexes = self.calculate_betweenness()
            elif self.current_centrality_index == "Closeness":
                centrality_indexes = self.calculate_closeness()
            else:
                centrality_indexes = self.calculate_eigenvector()
            ret_val["min"] = min(centrality_indexes)
            ret_val["max"] = max(centrality_indexes)

            return ret_val

    def get_interpolated_index(self, r1_min, r1_max, r1_value, r2_min=0, r2_max=9):
        """Get an interpolated integer from range [r1_min, r1_max] to [r2_min..r2_max]
        """
        index = 0
        if r1_max > r1_min:
            index = int(
                round(
                    (
                        r2_min
                        + ((r1_value - r1_min) / (r1_max - r1_min)) * (r2_max - r2_min)
                    ),
                    0,
                )
            )
        elif r1_max == r1_min:
            index = r1_min

        return index

    def rgb_to_hex(self, rgb):
        """Converts a triplet (r, g, b) of bytes (0-255) in web color #000000
        :param url: a Triplet of bites with RGB color info
        :returns a string with web color format
        :rtype: :py:str

        """
        return "%02x%02x%02x" % rgb

    def get_pyvis(
        self,
        min_weight=4,
        max_weight=6,
        min_label_size=4,
        max_label_size=6,
        layout="fr",
        avoid_centrality=False,
    ):
        """Create a pyvis object based on current igraph network
        :param int min_weight: Integer with min node size
        :param int max_weight: Integer with max node size
        :param int min_label_size: Integer with min label size
        :param int max_label_size: Integer with max label size
        :param str layout: String with a valid iGraph Layout like
        "fruchterman_reingold", "kamada_kawai" or "circle"
        :return: A PyVis Object filled with the network's data.
        :rtype: :py:class:`pyvis`
        """
        pv_graph = None
        factor = 0

        print("Entering get_pyvis")
        print("self.graph_layout_name: " + str(repr(self.graph_layout_name)))
        print("layout: " + layout)
        random.seed(1234)

        if self.igraph_graph is not None:
            centrality_indexes = []
            if self.current_centrality_index == "Degree":
                centrality_indexes = self.calculate_degree()
            elif self.current_centrality_index == "Betweeness":
                centrality_indexes = self.calculate_betweenness()
            elif self.current_centrality_index == "Closeness":
                centrality_indexes = self.calculate_closeness()
            else:
                centrality_indexes = self.calculate_eigenvector()

            centrality_indexes_min = min(centrality_indexes)
            centrality_indexes_max = max(centrality_indexes)

            N = len(self.igraph_graph.vs)
            factor = 50

            if (self.graph_layout is None) or (layout != self.graph_layout_name):
                print("Recalculating layout...")
                print("self.graph_layout_name: " + str(repr(self.graph_layout_name)))
                print("layout: " + layout)
                if layout == "kk":
                    self.graph_layout = self.igraph_graph.layout_kamada_kawai()
                    self.graph_layout_name = "kk"
                elif layout == "grid_fr":
                    self.graph_layout = self.igraph_graph.layout_grid()
                    self.graph_layout_name = "grid_fr"
                    factor = 150
                elif layout == "circle":
                    self.graph_layout = self.igraph_graph.layout_circle()
                    self.graph_layout_name = "circle"
                    factor = 250
                elif layout == "sphere":
                    self.graph_layout = self.igraph_graph.layout_sphere()
                    self.graph_layout_name = "sphere"
                    factor = 250
                else:
                    self.graph_layout = self.igraph_graph.layout_fruchterman_reingold()
                    self.graph_layout_name = "fr"

                self.Xn = [self.graph_layout[k][0] for k in range(N)]
                self.Yn = [self.graph_layout[k][1] for k in range(N)]
            else:
                print("using same layout...")

            pv_graph = pyvis.network.Network(height="100%", width="100%", heading="")
            pyvis_map_options = {}
            pyvis_map_options["nodes"] = {
                "font": {"size": min_weight + 8},
                "scaling": {"min": min_weight, "max": max_weight},
            }
            show_arrows = True
            if self.graph_type == "global" and len(self.edges_filter) > 1:
                show_arrows = False

            pyvis_map_options["edges"] = {
                "arrows": {"to": {"enabled": show_arrows, "scaleFactor": 0.4}},
                "color": {"inherit": True},
                "smooth": True,
                "scaling": {
                    "label": {
                        "min": min_weight + 8,
                        "max": max_weight + 8,
                        "maxVisible": 18,
                    }
                },
            }
            pyvis_map_options["physics"] = {"enabled": False}
            pyvis_map_options["interaction"] = {
                "dragNodes": True,
                "hideEdgesOnDrag": True,
                "hover": True,
                "navigationButtons": True,
                "selectable": True,
                "multiselect": True,
            }
            pyvis_map_options["manipulation"] = {
                "enabled": False,
                "initiallyActive": True,
            }
            pyvis_map_options["configure"] = {"enabled": False}
            pv_graph.set_options(json.dumps(pyvis_map_options))
            # pv_graph.show_buttons()

            # Add Nodes
            for node in self.igraph_graph.vs:
                if not avoid_centrality:
                    color_index = self.get_interpolated_index(
                        centrality_indexes_min,
                        centrality_indexes_max,
                        centrality_indexes[node.index],
                    )
                else:
                    color_index = 4
                color = "#" + self.rgb_to_hex(VIRIDIS_COLORMAP[color_index])
                size = self.get_interpolated_index(
                    centrality_indexes_min,
                    centrality_indexes_max,
                    centrality_indexes[node.index],
                    min_weight,
                    max_weight,
                )
                pv_graph.add_node(
                    node.index,
                    label=node["name"],
                    color=color,
                    size=int(size * 2),
                    x=int(self.Xn[node.index] * factor),
                    y=int(self.Yn[node.index] * factor),
                    shape="dot",
                    # x=int(Xn[node.index]),
                    # y=int(Yn[node.index]),
                )
            for edge in self.igraph_graph.es:
                if self.graph_type == "map":
                    title = (
                        edge["edge_name"]
                        + " travels from: "
                        + self.igraph_graph.vs[edge.source]["name"]
                        + " to: "
                        + self.igraph_graph.vs[edge.target]["name"]
                    )
                else:
                    title = (
                        self.igraph_graph.vs[edge.source]["name"]
                        + " "
                        + edge["edge_name"]
                        + " "
                        + self.igraph_graph.vs[edge.target]["name"]
                    )
                pv_graph.add_edge(edge.source, edge.target, title=title)
        return pv_graph

    def get_map_data(
        self, min_weight=4, max_weight=6, min_label_size=4, max_label_size=6,
    ):
        if self.igraph_graph is not None:
            centrality_indexes = []
            if self.current_centrality_index == "Degree":
                centrality_indexes = self.calculate_degree()
            elif self.current_centrality_index == "Betweeness":
                centrality_indexes = self.calculate_betweenness()
            elif self.current_centrality_index == "Closeness":
                centrality_indexes = self.calculate_closeness()
            else:
                centrality_indexes = self.calculate_eigenvector()

            centrality_indexes_min = min(centrality_indexes)
            centrality_indexes_max = max(centrality_indexes)

            map = []
            nodes = self.get_vertex_names()
            map_dict_strings = [
                "Source",
                "Destination",
                "Philosopher",
                "SourceLatitude",
                "SourceLongitude",
                "DestLatitude",
                "DestLongitude",
            ]
            if self.travels_graph_data:
                for record in self.travels_graph_data:
                    index = 0
                    map_record = {}
                    for item in record:
                        tmp_value = item
                        if isinstance(item, list):
                            if len(item) == 1:
                                tmp_value = item[0]
                        map_record[map_dict_strings[index]] = tmp_value
                        if index == 0:
                            i = nodes.index(tmp_value)
                            color_index = self.get_interpolated_index(
                                centrality_indexes_min,
                                centrality_indexes_max,
                                centrality_indexes[i],
                            )
                            color = "#" + self.rgb_to_hex(VIRIDIS_COLORMAP[color_index])
                            map_record["SourceColor"] = color
                            size = self.get_interpolated_index(
                                centrality_indexes_min,
                                centrality_indexes_max,
                                centrality_indexes[i],
                                min_weight,
                                max_weight,
                            )
                            map_record["SourceSize"] = size
                        elif index == 1:
                            i = nodes.index(tmp_value)
                            color_index = self.get_interpolated_index(
                                centrality_indexes_min,
                                centrality_indexes_max,
                                centrality_indexes[i],
                            )
                            color = "#" + self.rgb_to_hex(VIRIDIS_COLORMAP[color_index])
                            map_record["DestinationColor"] = color
                            size = self.get_interpolated_index(
                                centrality_indexes_min,
                                centrality_indexes_max,
                                centrality_indexes[i],
                                min_weight,
                                max_weight,
                            )
                            map_record["DestinationSize"] = size
                        index = index + 1
                    map.append(map_record)
        return map

    def set_edges_filter(self, edges_filter):
        """Create subgraph depending on vertex selected
        """
        self.edges_filter.append(edges_filter)

    def create_subgraph(self):
        """Create subgraph depending on edges selected (i.e travellers)
        """
        subgraph = None
        if self.igraph_graph is not None:
            if not self.edges_filter:
                subgraph = self.igraph_graph
            else:
                edges = self.igraph_graph.es
                edge_names = self.igraph_graph.es["edge_name"]
                travellers = self.edges_filter if self.edges_filter else edges_filter
                edge_indexes = [
                    j.index for i, j in zip(edge_names, edges) if i in travellers
                ]
                subgraph = self.igraph_graph.subgraph_edges(edge_indexes)

            self.igraph_subgraph = subgraph

        return subgraph

    def get_subgraph(self):
        subgraph = None
        if self.edges_filter:
            sub_igraph = self.create_subgraph()
            self.tabulate_subgraph_data()
            sub_travels_map_data = self.travels_subgraph_data
            subgraph = copy.deepcopy(self)
            subgraph.igraph_graph = sub_igraph
            subgraph.travels_graph_data = sub_travels_map_data
        return subgraph

    def set_colour_scale(self):
        """Create parameters for the class graph

        :param nodes_file: File with the full list of nodes name/group (.csv)
        :param edges_file: File with full list of edges (.csv)
        :param locations_file: File with list of nodees/localization (.csv).
        :param igraph_graph: Python igraph graph object

        """
        return ()

    def tabulate_subgraph_data(self):
        """Create datatable for subgraph
        """
        source = []
        target = []
        name = []
        lat_source = []
        lon_source = []
        lat_target = []
        lon_target = []

        vertex_list = []
        edges_list = []

        if self.igraph_subgraph:
            for vertex in self.igraph_subgraph.vs:
                vertex_list.append(vertex["name"])

        if self.igraph_subgraph:
            for idx, edges in enumerate(self.igraph_subgraph.es):
                source.append(vertex_list[edges.tuple[0]])
                target.append(vertex_list[edges.tuple[1]])
                name.append(edges["edge_name"])
                lat_source.append(
                    pd.Series.to_list(
                        self.location_raw_data.lat[
                            self.location_raw_data.name.isin(
                                [vertex_list[edges.tuple[0]]]
                            )
                        ]
                    )
                )

                lon_source.append(
                    pd.Series.to_list(
                        self.location_raw_data.lon[
                            self.location_raw_data.name.isin(
                                [vertex_list[edges.tuple[0]]]
                            )
                        ]
                    )
                )

                lat_target.append(
                    pd.Series.to_list(
                        self.location_raw_data.lat[
                            self.location_raw_data.name.isin(
                                [vertex_list[edges.tuple[1]]]
                            )
                        ]
                    )
                )

                lon_target.append(
                    pd.Series.to_list(
                        self.location_raw_data.lon[
                            self.location_raw_data.name.isin(
                                [vertex_list[edges.tuple[1]]]
                            )
                        ]
                    )
                )

        list_of_tuples = list(
            zip(source, target, name, lat_source, lon_source, lat_target, lon_target)
        )
        list_of_tuples_ = list(list(row[0:]) for row in list_of_tuples)
        self.travels_subgraph_data = list_of_tuples_

    def get_current_edges(self):
        if self.current_edges is not None:
            return self.current_edges

    def get_global_edges_types(self):
        edges_types = []
        for edge_name in self.igraph_graph.es:
            if edge_name["edge_name"] not in edges_types:
                edges_types.append(edge_name["edge_name"])
        return edges_types


global_graph = diogenetGraph(
    "global",
    NODES_DATA_FILE,
    EDGES_DATA_FILE,
    LOCATIONS_DATA_FILE,
    TRAVELS_BLACK_LIST_FILE,
)

map_graph = diogenetGraph(
    "map",
    NODES_DATA_FILE,
    EDGES_DATA_FILE,
    LOCATIONS_DATA_FILE,
    TRAVELS_BLACK_LIST_FILE,
)

# grafo.centralization_degree()
# grafo.centralization_betweenness()
# grafo.centralization_closeness()
# grafo.centralization_eigenvector()

# grafo.set_edges_filter("Aristotle")
# # grafo.set_edges_filter("Pythagoras")
# grafo.create_subgraph()
# # print(grafo.igraph_subgraph)

# grafo.tabulate_subgraph_data()

# datos_sub_grafo =
# print(datos_sub_grafo)

# grafo.set_edges_filter("Aristotle")
# grafo.set_edges_filter("Pythagoras")
# print(grafo.create_subgraph())
