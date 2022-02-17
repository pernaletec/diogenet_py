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
    id='navbar-communities'
)

sidebar_content = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_communnities',
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
        id='graph_filter_communities',
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
        id='graph_algorithm_communnities',
        options=[
            {'label': 'Cluster Edge Betweenness', 'value': 'community_edge_betweenness'},
            {'label': 'Cluster Fast Greedy', 'value': 'community_fastgreedy'},
            {'label': 'Cluster Infomap', 'value': 'community_infomap'},
            {'label': 'Cluster Label Prop', 'value': 'community_label_propagation'},
            {'label': 'Cluster Leading Eigen', 'value': 'community_leading_eigenvector'},
            {'label': 'Cluster Louvain', 'value': 'community_leiden'},
            {'label': 'Cluster Walktrap', 'value': 'community_walktrap'},
        ],
        value='community_edge_betweenness',
        searchable=False,
    ),
    dcc.Checklist(
        id='show_gender_communities',
        options=[
            {'label': ' Gender and Gods', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Visualization',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='visualization_communnities',
        options=[
            {'label': 'VisNetwork', 'value': 'pyvis'},
            {'label': 'Igraph', 'value': 'igraph'},
        ],
        value='pyvis',
        searchable=False,
    ),
    dcc.Checklist(
        id='crossing_ties',
        options=[
            {'label': ' Show crossing ties', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='label_size_communities',
        min=0,
        max=10,
        step=1,
        marks={
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
        },
        value=[4, 6]
    ),
    html.H6('Node Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='node_size_communities',
        min=0,
        max=10,
        step=1,
        marks={
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
        },
        value=[4, 6]
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
                dbc.Col(id='main-netowrk-graph-communities', children=[]),
                dcc.ConfirmDialog(
                        id='confirm-warning-tie',
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
    Output('main-netowrk-graph-communities', 'children'),
    Input('dataset_selection_communnities', 'value'),
    Input('graph_filter_communities', 'value'),
    Input('graph_algorithm_communnities', 'value'),
    Input('show_gender_communities', 'value'),
    Input('visualization_communnities', 'value'),
    Input('crossing_ties', 'value'),
    Input('label_size_communities', 'value'),
    Input('node_size_communities', 'value'),)
def horus_get_local_graph(dataset_selection,
                        graph_filter,
                        graph_algorithm,
                        show_gender,
                        visualization,
                        crossing_ties,
                        label_size,  
                        node_size):
    communities_graph = diogenetGraph(
        "communities",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )   

    pvis_graph = None
    warning_tie = False
    node_min_size = int(node_size[0])
    node_max_size = int(node_size[1])
    label_min_size = int(label_size[0])
    label_max_size = int(label_size[1])
    graph_filter = graph_filter
    algorithm_value = graph_algorithm
    not_centrality = False
    crossing_ties = crossing_ties
    graph_layout = "fr"
    plot_type = visualization

    if graph_algorithm in ["", "None", None]:
        algorithm_value = "community_infomap"

    communities_graph.comm_alg = algorithm_value
    communities_graph.identify_communities()

    if crossing_ties in ["True", "true", True]:
        communities_graph.pyvis_show_crossing_ties = True
    else:
        communities_graph.pyvis_show_crossing_ties = False
        
    if not graph_filter:
        communities_graph.set_edges_filter("is teacher of")
    else:
        communities_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            communities_graph.set_edges_filter(m_filter)

    if show_gender in ["True", "true", True]:
        communities_graph.pyvis_show_gender = True
    else:
        communities_graph.pyvis_show_gender = False

    communities_graph.create_subgraph()

    if plot_type == "pyvis":
        pvis_graph = communities_graph.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
            avoid_centrality=not_centrality,
        )
        suffix = ".html"
        temp_file_name = next(tempfile._get_candidate_names()) + suffix
        full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
        pvis_graph.write_html(full_filename)
        return [html.H6('Graph',className="mt-1 mb-2 text-center"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})]

    # if plot_type == "igraph":
    #     suffix = ".svg" 
    #     temp_file_name = next(tempfile._get_candidate_names()) + suffix
    #     full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
    #     if plot_type == "igraph":
    #         modularity, clusters = communities_graph.identify_communities()
    #         dendogram_communities_list = [
    #             "community_edge_betweenness",
    #             "community_walktrap",
    #             "community_fastgreedy",
    #         ]
    #         communities_graph.igraph_subgraph.vs["label"] = communities_graph.igraph_subgraph.vs["name"]
    #         if communities_graph.comm_alg not in dendogram_communities_list:
    #             plot(
    #                 communities_graph.comm,
    #                 full_filename,
    #                 layout=communities_graph.graph_layout,
    #                 bbox=(450, 450),
    #                 margin=20,
    #                 mark_groups=True,
    #                 vertex_label_size=7,
    #                 vertex_label_angle=200,
    #                 vertex_label_dist=1,
    #                 vertex_size=8,
    #             )
    #         with open(full_filename, "r") as file:
    #             if communities_graph.comm_alg not in dendogram_communities_list:
    #                 data = file.read().replace('width="450pt"', 'width="100%"')
    #             else:
    #                 data = file.read()
    #             full_html_file_content = HTML_PLOT_CONTENT.format(file=data)
    #             temp_html_file_name = (
    #                 next(tempfile._get_candidate_names()) + HTML_SUFFIX
    #             )
    #             full_html_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
    #             full_html_file = open(full_html_filename, "w")
    #             _ = full_html_file.write(full_html_file_content)
    #             full_html_file.close()
    #             full_filename = full_html_filename
    #     else:
    #         pvis_graph.write_html(full_filename)
        
    # print(full_filename)


    