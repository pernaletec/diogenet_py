"""Module to handle Complex Networks Graph relations in ancient Greece.

.. platform:: Unix, Windows, Mac
.. moduleauthor:: Elio Linarez <elinarezv@gmail.com>
"""

import igraph
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class Graph:
    nodes: pd.DataFrame
    edges: pd.DataFrame
    locations: pd.DataFrame

    def know_locations(self):
        return pd.DataFrame()
