"""Module to handle Complex Networks Graph relations in ancient Greece.

.. platform:: Unix, Windows, Mac
.. moduleauthor:: Elio Linarez <elinarezv@gmail.com>
"""

import igraph
import pandas as pd
import numpy as np
from dataclasses import dataclass
#import data_access

@dataclass
class map_graph:
    nodes: pd.DataFrame
    edges: pd.DataFrame
    locations: pd.DataFrame
    
    def __init__(self, n, e, l, m):
        self.nodes = n
        self.edges = e
        self.locations = l
        self.map_graph_objm = igraph.Graph()

    def know_locations(self):
        return pd.DataFrame()

grafo = map_graph(1,2,3,4)

print(grafo.map_graph_objm)


