from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash import dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pathlib
import os
import sys
import requests
import tempfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    send_from_directory,
    send_file,
    jsonify,
)


from app import app
from data_analysis_module.network_graph import diogenetGraph

dict_of_datasets = {'Diogenes Laertius': 'diogenes', 'Life of Pythagoras Iamblichus': 'iamblichus'}

STYLE_A_ITEM = {
    'color':'#ffffff',
    'textDecoration': 'none'
}

navbar = dbc.Navbar(
    children=[
        html.Div(
            [
                dbc.NavLink("Horus", style=STYLE_A_ITEM),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Graph", href="global_network_graph"), 
                        dbc.DropdownMenuItem("Graph + centrality", href="/apps/global_network_graph_centrality")
                    ],
                    label="Global Network",
                    style=STYLE_A_ITEM,
                    color="#1a6ecc"
                ),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Graph", href="/apps/local_network_graph"),
                        dbc.DropdownMenuItem("Graph + centrality", href="/apps/local_network_graph_centrality")
                    ],
                    label="Local Network",
                    style=STYLE_A_ITEM,
                    color="#1a6ecc"
                ),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Graph", href="/apps/communities_graph"),
                        dbc.DropdownMenuItem("Treemap", href="/apps/communities_treemap")
                    ],
                    label="Communities",
                    style=STYLE_A_ITEM,
                    color="#1a6ecc"
                )
            ],
            className="d-flex",

        ),
        dbc.NavLink(
            [
                html.I(className="bi bi-house-fill me-2 text-white")
            ], 
            href="https://diogenet.ucsd.edu/", style=STYLE_A_ITEM,
            target="blank"
        ),
            
    ],
    color="#1a6ecc",
    className="d-flex justify-content-between",
    style={'color':'#ffffff'},
    id='navbar-communities-treemap'
)

sidebar_content = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_communities_treemap',
        options=[
            {'label': key, 'value': value}
            for key, value in dict_of_datasets.items()
        ],
        searchable=False,
        placeholder="Select a dataset",
        value='diogenes'
    ),
    html.H5('Network ties', className="mt-5 mb-3"),
    dcc.Checklist( 
        id='graph_filter_communities_treemap',
        options=[
            {'label': ' Is teacher of', 'value': 'is teacher of'},
                {'label': ' Is friend of', 'value': 'is friend of'},
                {'label': ' Is family of', 'value': 'is family of'},
                {'label': ' Studied the work of', 'value': 'studied the work of'},
                {'label': ' Sent letters to', 'value': 'sent letters to'},
                {'label': ' Is benefactor of', 'value': 'is benefactor of'},
        ],
        value=['is teacher of'],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
    ),
    html.H5('Community detection',className="mt-5 mb-3"),
    html.H6("Algorithm"),
    dcc.Dropdown(
        id='graph_algorithm_communities_treemap',
        options=[
            {'label': 'Cluster Edge Betweenness', 'value': 'community_edge_betweenness'},
            {'label': 'Cluster Fast Greedy', 'value': 'community_fastgreedy'},
            {'label': 'Cluster Infomap', 'value': 'community_infomap'},
            {'label': 'Cluster Label Prop', 'value': 'community_label_propagation'},
            {'label': 'Cluster Leading Eigen', 'value': 'community_leading_eigenvector'},
            {'label': 'Cluster Leiden', 'value': 'community_leiden'},
            {'label': 'Cluster Walktrap', 'value': 'community_walktrap'},
        ],
        value='community_edge_betweenness',
        searchable=False,
    ),
    html.H6('Download current dataset',className="mt-5 mb-3"),
    dbc.Button("Download Data", id="btn_csv", color="secondary", className="ml-3"),
    dcc.Download(id="download-dataframe-csv"),
]

row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
                dbc.Col(id='main-netowrk-graph-communities-treemap'),
                dcc.ConfirmDialog(
                        id='confirm-warning-tie-treemap',
                        message='You must select at least one tie',
                    ),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout = html.Div(
    [
        row
    ],  
    style={"height": "100vh"}
)

@app.callback(
    Output('main-netowrk-graph-communities-treemap', 'children'),
    Input('dataset_selection_communities_treemap', 'value'),
    Input('graph_filter_communities_treemap', 'value'),
    Input('graph_algorithm_communities_treemap', 'value'),)
def horus_get_communities_treemap(
                        dataset_selection,
                        graph_filter,
                        graph_algorithm):
                        
    communities_graph = diogenetGraph(
        "communities",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    warning_tie = False
    graph_filter = graph_filter
    communities_graph.current_centrality_index = "communities"
    communities_graph.comm_alg = str(graph_algorithm)
    graph_layout = "fr"
    communities_graph.set_graph_layout(graph_layout)
    communities_graph.pyvis_show_crossing_ties = False

    if not graph_filter:
        communities_graph.set_edges_filter("is teacher of")
    else:
        communities_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            communities_graph.set_edges_filter(m_filter)

    communities_graph.create_subgraph()
    subgraph = communities_graph
    modularity, clusters_dict = subgraph.identify_communities()

    communities_index = []

    for i in range(len(subgraph.igraph_subgraph.vs)):
        if subgraph.igraph_subgraph.vs[i]["name"] in clusters_dict.keys():
            communities_index.append(
                clusters_dict[subgraph.igraph_subgraph.vs[i]["name"]]
            )

    data = {
        "Philosopher": subgraph.igraph_subgraph.vs["name"],
        "Degree": subgraph.calculate_degree(),
        "Community": communities_index,
    }

    df = pd.DataFrame(data=data)
    df1 = df.sort_values(by=["Community", "Degree"]).set_index(
        "Philosopher", drop=False
    )

    plotly_graph = px.treemap(df1, path=["Community", "Philosopher"], values="Degree",)

    plotly_graph.update_layout(
        legend_font_size=12, legend_title_font_size=12, font_size=8
    )

    return html.Div([dcc.Graph(figure=plotly_graph, style={"height": "100%", "width": "100%"})], style={"height": "100%", "width": "100%"})

@app.callback(Output('confirm-warning-tie-treemap', 'displayed'),
              Input('graph_filter_communities_treemap', 'value'))
def display_confirm(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False    