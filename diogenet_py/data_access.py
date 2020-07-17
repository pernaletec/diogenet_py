"""Module to handle Complex Networks Graph relations in ancient Greece.

.. platform:: Unix, Windows, Mac
.. moduleauthor:: Elio Linarez <elinarezv@gmail.com>
"""
import pandas as pd
import io
import requests
#  Not needed. Data is called from the class. .    
#  from . import network_graph

# VARS to fullfill dataframes
# Define data access method: local, url or database

def get_data_entity(entity_name, method):
    """Retrieve a dataset with Complex Network's data.

    :param str entity_name: The name of the entity (csv file name or table name).
    :param str method: String with access method: local (csv), url(csv) or database.
    :return: A Data Frame filled with the entity's data.
    :rtype: :py:class:`pd.DataFrame`
    """
    df = None
    if method == "local":
        df = pd.read_csv("./" + entity_name, delimiter=",", header=0)
    if method == "url":
        url = BASE_URL + "/" + entity_name
        request = requests.get(url).content
        df = pd.read_csv(io.StringIO(request.decode("utf-8")), delimiter=",", header=0)
    if method == "database":
        # Define methods for access node from database
        df = None
    return df


# def get_graph(
#     nodes_entity="new_Nodes.csv",
#     edges_entity="new_Edges.csv",
#     location_entity="locations_data.csv",
#     method="local",
#     url="",
# ):
#  graph = network_graph.Graph()


travel_edges =  pd.read_csv("travel_edges_graph.csv", delimiter=',')
all_places = pd.read_csv("all_places_graph.csv", delimiter=',')
