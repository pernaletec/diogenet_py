import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash import dash_table
from dash.exceptions import PreventUpdate
import pathlib
import os
import sys
import requests
import tempfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from igraph import plot
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    send_from_directory,
    send_file,
    jsonify,
)
from data_analysis_module.network_graph import diogenetGraph


app = dash.Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
#app = dash.Dash(__name__,external_stylesheets= [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], url_base_pathname = '/diogenet_horus/')
#app.config.suppress_callback_exceptions = True
server = app.server

################################################### Generic Layout #######################################################
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
                    color="secondary"
                ),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Graph", href="/apps/local_network_graph"),
                        dbc.DropdownMenuItem("Graph + centrality", href="/apps/local_network_graph_centrality")
                    ],
                    label="Local Network",
                    style=STYLE_A_ITEM,
                    color="secondary"
                ),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Graph", href="/apps/communities_graph"),
                        dbc.DropdownMenuItem("Treemap", href="/apps/communities_treemap")
                    ],
                    label="Communities",
                    style=STYLE_A_ITEM,
                    color="secondary"
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
    color="#6c757d",
    className="d-flex justify-content-between",
    style={'color':'#ffffff'},
    id='Navbar'
)
################################################### End Generic Layout ###################################################

################################################# Layout Global Graph ####################################################
sidebar_content_global_graph = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection',
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
        id='graph_filter_global',
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
    html.H5('Graph layout',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='graph_layout_global',
        options=[
            {'label': 'Fruchterman-Reingold', 'value': 'fr'},
            {'label': 'Kamada-Kawai', 'value': 'kk'},
            {'label': 'On Sphere', 'value': 'sphere'},
            {'label': 'In Circle', 'value': 'circle'},
            {'label': 'On Grid', 'value': 'grid_fr'},
        ],
        value='fr',
        searchable=False,
    ),
    dcc.Checklist(
        id='show_gender',
        options=[
            {'label': ' Gender and Gods', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='label_size_global',
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
        id='node_size_global',
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
    dbc.Button("Download Data", id="btn_csv", color="secondary", className="ml-3", n_clicks=0),
    dcc.Download(id="download-dataframe-csv"),
]

row_global_graph = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_global_graph), id='sidebar', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
                dbc.Col(id='main-netowrk-graph'),
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

layout_global_graph = html.Div(
    [
        row_global_graph
    ],  
    style={"height": "100vh"}
)
################################################# End Layout Global Graph #################################################

################################################# Layout Global Graph Centrality ####################################################
sidebar_content_global_centrality = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_global_centrality',
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
        id='graph_filter_global_centrality',
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
    html.H5('Graph layout',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='graph_layout_global_centrality',
        options=[
            {'label': 'Fruchterman-Reingold', 'value': 'fr'},
            {'label': 'Kamada-Kawai', 'value': 'kk'},
            {'label': 'On Sphere', 'value': 'sphere'},
            {'label': 'In Circle', 'value': 'circle'},
            {'label': 'On Grid', 'value': 'grid_fr'},
        ],
        value='fr',
        searchable=False,
    ),
    dcc.Checklist(
        id='show_gender_global_centrality',
        options=[
            {'label': ' Gender and Gods', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Centrality index',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='centrality_index_global_centrality',
        options=[
            {'label': 'Degree', 'value': 'Degree'},
            {'label': 'Betweeness', 'value': 'Betweeness'},
            {'label': 'Closeness', 'value': 'Closeness'},
            {'label': 'Eigenvector', 'value': 'Eigenvector'},
        ],
        value='Degree',
        searchable=False,
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='label_size_global_centrality',
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
        id='node_size_global_centrality',
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
    dbc.Button("Download Data", id="btn_csv_global", color="secondary", className="ml-3"),
    dcc.Download(id="download-dataframe-csv-global"),
]

tabs_global_centrality = dcc.Tabs(
        id='tabs_global_cetrality', 
        value='graph_global_cetrality',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Graph', 
                value='graph_global_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'    
            ),
                
            dcc.Tab(
                label='Heatmap', 
                value='heatmap_global_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Metrics', 
                value='metrics_global_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ])


row_global_centrality = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_global_centrality), id='sidebar_global_centrality', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div([tabs_global_centrality, html.Div(id="content", style={'height': '100vh'})]), id='main_global_centrality'),
                dcc.ConfirmDialog(
                        id='confirm-warning-tie-centrality',
                        message='You must select at least one tie',
                    ),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout_global_centrality = html.Div([
    row_global_centrality
    ],  style={"height": "100vh"})
################################################# End Layout Global Graph Centrality ####################################################

################################################# Layout Local Graph ####################################################
sidebar_content_local = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_local',
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
        id='graph_filter_local',
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
    html.H5('Ego',className="mt-5 mb-3"),
    html.Div(
        id='dropdown_container_local',
        children=[]
    ),
    html.H5('Order',className="mt-5 mb-3"),
    dcc.RangeSlider(
        id='order_local',
        min=0,
        max=4,
        step=1,
        marks={
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
        },
        value=[2]
    ),
    dcc.Checklist(
        id='show_gender_local',
        options=[
            {'label': ' Gender and Gods', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Centrality index',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='centrality_index_local',
        options=[
            {'label': 'Degree', 'value': 'Degree'},
            {'label': 'Betweeness', 'value': 'Betweeness'},
            {'label': 'Closeness', 'value': 'Closeness'},
            {'label': 'Eigenvector', 'value': 'Eigenvector'},
        ],
        value='Degree',
        searchable=False,
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='label_size_local',
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
        id='node_size_local',
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
    dbc.Button("Download Data", id="btn_csv_local", color="secondary", className="ml-3"),
    dcc.Download(id="download_dataframe_csv_local"),
]

row_local = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_local), id='sidebar_local', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
                dbc.Col(id='main_local_netowrk_graph'),
                dcc.ConfirmDialog(
                        id='confirm_warning_tie_local',
                        message='You must select at least one tie',
                    ),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout_local = html.Div(
    [
    row_local
    ],  
    style={"height": "100vh"}
)
################################################# End Layout Local Graph ####################################################

################################################# Layout Local Graph Centrality ####################################################
sidebar_content_local_centrality = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_local_centrality',
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
        id='graph_filter_local_centrality',
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
    html.H5('Ego',className="mt-5 mb-3"),
    html.Div(
        id='dropdown_container_local_centrality',
        children=[]
    ),
    html.H5('Order',className="mt-5 mb-3"),
    dcc.RangeSlider(
        id='order_local_centrality',
        min=0,
        max=4,
        step=1,
        marks={
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
        },
        value=[2]
    ),
    dcc.Checklist(
        id='show_gender_local_centrality',
        options=[
            {'label': ' Gender and Gods', 'value': "True"}
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Centrality index',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='centrality_index_local_centrality',
        options=[
            {'label': 'Degree', 'value': 'Degree'},
            {'label': 'Betweeness', 'value': 'Betweeness'},
            {'label': 'Closeness', 'value': 'Closeness'},
            {'label': 'Eigenvector', 'value': 'Eigenvector'},
        ],
        value='Degree',
        searchable=False,
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
        id='label_size_local_centrality',
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
        id='node_size_local_centrality',
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
    dbc.Button("Download Data", id="btn_csv_local_centrality", color="secondary", className="ml-3"),
    dcc.Download(id="download_dataframe_csv_local_centrality"),
]

tabs_local_centrality = dcc.Tabs(
        id='tabs_local_cetrality', 
        value='graph_local_cetrality',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Graph', 
                value='graph_local_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'    
            ),
                
            dcc.Tab(
                label='Heatmap', 
                value='heatmap_local_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Metrics', 
                value='metrics_local_cetrality',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ])

row_local_centrality = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_local_centrality), id='sidebar_local_centrality', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div(children=[tabs_local_centrality, html.Div(id="content_local_centrality", style={'height': '100vh'}, children=[])]), id='main_local_centrality'),
                dcc.ConfirmDialog(
                        id='confirm-warning-tie-local-centrality',
                        message='You must select at least one tie',
                    ),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout_local_centrality = html.Div(
    [
    row_local_centrality
    ],  
    style={"height": "100vh"}
)
################################################# End Layout Local Graph Centrality ####################################################

################################################# Layout Communities Graph ####################################################
sidebar_content_communnities = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_communities',
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
        id='graph_algorithm_communities',
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
        id='visualization_communities',
        options=[
            {'label': 'VisNetwork', 'value': 'pyvis'},
            {'label': 'Igraph', 'value': 'igraph'},
        ],
        value='pyvis',
        searchable=False,
    ),
    dcc.Checklist(
        id='crossing_ties_communities',
        options=[
            {'label': 'Show crossing ties', 'value': "True"}
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
    dbc.Button("Download Data", id="btn_csv_community_graph", color="secondary", className="ml-3"),
    dcc.Download(id="download_dataframe_csv_community_graph"),
]

row_communnities = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_communnities), id='sidebar', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
                dbc.Col(id='main-netowrk-graph-communities', children=[]),
                dcc.ConfirmDialog(
                        id='confirm-warning-tie-coomunities',
                        message='You must select at least one tie',
                    ),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout_communnities = html.Div(
    [
        row_communnities
    ],  
    style={"height": "100vh"}
)
################################################# End Layout Communities Graph ####################################################

################################################# Layout Communities Treemap ####################################################
sidebar_content_communities_treemap = [
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
    dbc.Button("Download Data", id="btn_csv_community_treemap", color="secondary", className="ml-3"),
    dcc.Download(id="download_dataframe_csv_community_treemap"),
]

row_communities_treemap = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content_communities_treemap), id='sidebar', width=3, style={"backgroundColor": "#ced4da", "padding":'30px 10px 10px 10px'}),
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

layout_communities_treemap = html.Div(
    [
        row_communities_treemap
    ],  
    style={"height": "100vh"}
)
################################################# End Layout Communities Treemap ####################################################

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[])
])

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layout_global_graph
    if pathname == '/apps/global_network_graph':
        return layout_global_graph
    if pathname == '/apps/global_network_graph_centrality':
        return layout_global_centrality
    if pathname == '/apps/local_network_graph':
        return layout_local
    if pathname == '/apps/local_network_graph_centrality':
        return layout_local_centrality
    if pathname == '/apps/communities_graph':
        return layout_communnities
    if pathname == '/apps/communities_treemap':
        return layout_communities_treemap
    else:
        return '404'

############################################ Callbacks Global Graph #####################################################
@app.callback(
    Output('main-netowrk-graph', 'children'),
    Input('dataset_selection', 'value'),
    Input('graph_filter_global', 'value'),
    Input('graph_layout_global', 'value'),
    Input('show_gender', 'value'),
    Input('label_size_global', 'value'),
    Input('node_size_global', 'value'),)
def horus_get_global_graph(dataset_selection, 
                            graph_filter_global, 
                            graph_layout_global, 
                            show_gender, 
                            label_size_global, 
                            node_size_global):

    grafo = diogenetGraph(
        "global",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )
    
    plot_type = "pyvis"
    warning_tie = False
    node_min_size = int(node_size_global[0])
    node_max_size = int(node_size_global[1])
    label_min_size = int(label_size_global[0])
    label_max_size = int(label_size_global[1])
    grafo.current_centrality_index = "Degree"
    not_centrality = True
    graph_layout = graph_layout_global

    grafo.edges_filter = []
    filters = graph_filter_global
    for m_filter in filters:
        grafo.set_edges_filter(m_filter)

    if not graph_layout:
        graph_layout = "fr"

    if show_gender:
        grafo.pyvis_show_gender = True
    else:
        grafo.pyvis_show_gender = False

    grafo.create_subgraph()

    pvis_graph = None

    if plot_type == "pyvis":
        pvis_graph = grafo.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
            avoid_centrality=not_centrality,
        )
    
    if pvis_graph:
        suffix = ".html"
        temp_file_name = next(tempfile._get_candidate_names()) + suffix
        full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
        pvis_graph.write_html(full_filename)
        return [html.H6('Global Network',className="mt-1 mb-2 text-center"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})]

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    Input('dataset_selection', 'value'),
    Input('graph_filter_global', 'value'),
    prevent_initial_call=True,
)
def download_handler_global_graph(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass

@app.callback(Output('confirm-warning-tie', 'displayed'),
              Input('graph_filter_global', 'value'))
def display_confirm_missing_tie_global_graph(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False
############################################ End Callbacks Global Graph #####################################################

############################################ Callbacks Global Graph Centrality #####################################################
@app.callback(
    Output("content", "children"),[
    Input('tabs_global_cetrality', 'value'),
    Input('dataset_selection_global_centrality', 'value'),
    Input('graph_filter_global_centrality', 'value'),
    Input('graph_layout_global_centrality', 'value'),
    Input('show_gender_global_centrality', 'value'),
    Input('centrality_index_global_centrality', 'value'),
    Input('label_size_global_centrality', 'value'),
    Input('node_size_global_centrality', 'value')
    ]
)
def horus_get_global_graph_centrality(
                                    tab,
                                    dataset_selection_global_centrality,
                                    graph_filter_global_centrality,
                                    graph_layout_global_centrality,
                                    show_gender_global_centrality,
                                    centrality_index_global_centrality,
                                    label_size_global_centrality,
                                    node_size_global_centrality):
    global_graph = diogenetGraph(
            "global",
            dataset_selection_global_centrality,
            dataset_selection_global_centrality,
            'locations_data.csv',
            'travels_blacklist.csv'
        )

    plot_type = "pyvis"
    centrality_index = centrality_index_global_centrality
    node_min_size = int(node_size_global_centrality[0])
    node_max_size = int(node_size_global_centrality[1])
    label_min_size = int(label_size_global_centrality[0])
    label_max_size = int(label_size_global_centrality[1])
    global_graph.current_centrality_index = "Degree"
    not_centrality = False
    graph_layout = graph_layout_global_centrality
    graph_filter = graph_filter_global_centrality
    
    if tab == "graph_global_cetrality":
        if centrality_index:
            if centrality_index in [None, "", "None"]:
                global_graph.current_centrality_index = "Degree"
                not_centrality = True
            else:
                global_graph.current_centrality_index = centrality_index


        if not graph_filter:
            global_graph.set_edges_filter("is teacher of")
        else:
            global_graph.edges_filter = []
            filters = graph_filter
            for m_filter in filters:
                global_graph.set_edges_filter(m_filter)

        if not graph_layout_global_centrality:
            graph_layout_global_centrality = "fr"

        if show_gender_global_centrality:
            global_graph.pyvis_show_gender = True
        else:
            global_graph.pyvis_show_gender = False

        global_graph.create_subgraph()
        pvis_graph = None

        if plot_type == "pyvis":
            pvis_graph = global_graph.get_pyvis(
                min_weight=node_min_size,
                max_weight=node_max_size,
                min_label_size=label_min_size,
                max_label_size=label_max_size,
                layout=graph_layout_global_centrality,
                avoid_centrality=not_centrality,
            )

        if pvis_graph:
            suffix = ".html"
            temp_file_name = next(tempfile._get_candidate_names()) + suffix
            full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
            pvis_graph.write_html(full_filename)
            return html.Iframe(src=f"/assets/{temp_file_name}",style={"height": "900px", "width": "100%"})

    if tab == "heatmap_global_cetrality":
        plotly_graph = None

        if not graph_filter:
            global_graph.set_edges_filter("is teacher of")
        else:
            global_graph.edges_filter = []
            filters = graph_filter
            for m_filter in filters:
                global_graph.set_edges_filter(m_filter)

        def round_list_values(list_in):
            return [round(value, 4) for value in list_in]

        calculated_degree = [round(value) for value in global_graph.calculate_degree()]
        calculated_betweenness = round_list_values(global_graph.calculate_betweenness())
        calculated_closeness = round_list_values(global_graph.calculate_closeness())
        calculated_eigenvector = round_list_values(global_graph.calculate_eigenvector())

        dict_global_data_tables ={
            "Phylosopher": global_graph.get_vertex_names(),
            "Degree": calculated_degree,
            "Betweeness": calculated_betweenness,
            "Closeness": calculated_betweenness,
            "Eigenvector": calculated_eigenvector 
        }

        interpolated_data = {
            "Phylosopher": dict_global_data_tables["Phylosopher"],
            "Degree": np.interp(
                dict_global_data_tables["Degree"], (min(dict_global_data_tables["Degree"]), max(dict_global_data_tables["Degree"])), (0, +1)
            ),
            "Betweeness": np.interp(
                dict_global_data_tables["Betweeness"],
                (min(dict_global_data_tables["Betweeness"]), max(dict_global_data_tables["Betweeness"])),
                (0, +1),
            ),
            "Closeness": np.interp(
                dict_global_data_tables["Closeness"],
                (min(dict_global_data_tables["Closeness"]), max(dict_global_data_tables["Closeness"])),
                (0, +1),
            ),
            "Eigenvector": np.interp(
                dict_global_data_tables["Eigenvector"],
                (min(dict_global_data_tables["Eigenvector"]), max(dict_global_data_tables["Eigenvector"])),
                (0, +1),
            ),
        }

        df_global_heatmap = pd.DataFrame(interpolated_data).sort_values(["Degree", "Betweeness", "Closeness"])
                            
        plotly_graph = go.Figure(
            data=go.Heatmap(
                z=df_global_heatmap[["Degree", "Betweeness", "Closeness", "Eigenvector"]],
                y=df_global_heatmap["Phylosopher"],
                x=["Degree", "Betweeness", "Closeness", "Eigenvector"],
                hoverongaps=False,
                type="heatmap",
                colorscale="Viridis",
            )
        )
        plotly_graph.update_layout(
            legend_font_size=12, legend_title_font_size=12, font_size=8
        )
        
        return html.Div([dcc.Graph(figure=plotly_graph, style={"height": "100%", "width": "100%"})], style={"height": "100%", "width": "100%"})

    if tab == "metrics_global_cetrality":
        if not graph_filter:
            global_graph.set_edges_filter("is teacher of")
        else:
            global_graph.edges_filter = []
            filters = graph_filter
            for m_filter in filters:
                global_graph.set_edges_filter(m_filter)
        
        def round_list_values(list_in):
            return [round(value, 4) for value in list_in]

        calculated_degree = [round(value) for value in global_graph.calculate_degree()]
        calculated_betweenness = round_list_values(global_graph.calculate_betweenness())
        calculated_closeness = round_list_values(global_graph.calculate_closeness())
        calculated_eigenvector = round_list_values(global_graph.calculate_eigenvector())

        dict_global_data_tables ={
            "Phylosopher": global_graph.get_vertex_names(),
            "Degree": calculated_degree,
            "Betweeness": calculated_betweenness,
            "Closeness": calculated_betweenness,
            "Eigenvector": calculated_eigenvector 
        }

        df_global_data_tables = pd.DataFrame(dict_global_data_tables)

        dt = dash_table.DataTable( 
            id='table-global-graph', 
            columns=[{"name": i, "id": i, 'deletable': True} for i in df_global_data_tables.columns],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                }
            ],
            style_cell={'textAlign': 'center'}, 
            page_current=0,
            page_size=20,
            page_action='custom',
            sort_mode='single',
            sort_by=[{'column_id': 'Degree', 'direction': 'asc'}]
        )
        
        return [html.H6('Centrality Scores',className="mt-1 mb-2"), html.Hr(className='py-0'), dt]

@app.callback(
    Output('table-global-graph', 'data'),
    Input('table-global-graph', "page_current"),
    Input('table-global-graph', "page_size"),
    Input('table-global-graph', 'sort_by'),
    Input('dataset_selection_global_centrality', 'value'),
    Input('graph_filter_global_centrality', 'value'),
    Input('graph_layout_global_centrality', 'value'),
    Input('show_gender_global_centrality', 'value'),
    Input('centrality_index_global_centrality', 'value'),
    Input('label_size_global_centrality', 'value'),
    Input('node_size_global_centrality', 'value')
)
def update_table_global_centrality(
                page_current, 
                page_size, 
                sort_by,
                dataset_selection_global_centrality,
                graph_filter_global_centrality,
                graph_layout_global_centrality,
                show_gender_global_centrality,
                centrality_index_global_centrality,
                label_size_global_centrality,
                node_size_global_centrality
):
    global_graph = diogenetGraph(
                "global",
                dataset_selection_global_centrality,
                dataset_selection_global_centrality,
                'locations_data.csv',
                'travels_blacklist.csv'
            )

    plot_type = "pyvis"
    centrality_index = centrality_index_global_centrality
    node_min_size = int(label_size_global_centrality[0])
    node_max_size = int(label_size_global_centrality[1])
    label_min_size = int(node_size_global_centrality[0])
    label_max_size = int(node_size_global_centrality[1])
    global_graph.current_centrality_index = "Degree"
    not_centrality = False
    graph_layout = graph_layout_global_centrality
    graph_filter = graph_filter_global_centrality


    if not graph_filter:
            global_graph.set_edges_filter("is teacher of")
    else:
        global_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            global_graph.set_edges_filter(m_filter)
        
    def round_list_values(list_in):
        return [round(value, 4) for value in list_in]

    calculated_degree = [round(value) for value in global_graph.calculate_degree()]
    calculated_betweenness = round_list_values(global_graph.calculate_betweenness())
    calculated_closeness = round_list_values(global_graph.calculate_closeness())
    calculated_eigenvector = round_list_values(global_graph.calculate_eigenvector())

    dict_global_data_tables ={
        "Phylosopher": global_graph.get_vertex_names(),
        "Degree": calculated_degree,
        "Betweeness": calculated_betweenness,
        "Closeness": calculated_betweenness,
        "Eigenvector": calculated_eigenvector 
    }

    df_global_data_tables = pd.DataFrame(dict_global_data_tables)
    
    print(sort_by)
    if len(sort_by):
        dff = df_global_data_tables.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'desc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = df_global_data_tables

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

@app.callback(
    Output("download-dataframe-csv-global", "data"),
    Input("btn_csv_global", "n_clicks"),
    Input('dataset_selection_global_centrality', 'value'),
    Input('graph_filter_global_centrality', 'value'),
    prevent_initial_call=True,
)
def download_handler_global_graph_centrality(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_global.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass


@app.callback(Output('confirm-warning-tie-centrality', 'displayed'),
              Input('graph_filter_global_centrality', 'value'))
def display_confirm_missing_tie_global_graph_centrality(graph_filter_global_centrality):
    if len(graph_filter_global_centrality) == 0:
        return True
    return False
############################################ End Callbacks Global Graph Centrality #####################################################

############################################ Callbacks Local Graph #####################################################
@app.callback(
    Output('dropdown_container_local', 'children'),
    Input('dataset_selection_local', 'value'),
    Input('graph_filter_local', 'value'))
def get_philosopher_local(dataset_selection,
                    graph_filter):

    graph_filter = graph_filter

    local_graph = diogenetGraph(
        "local",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    if not graph_filter:
        graph_filter = "is teacher of"
        local_graph.set_edges_filter(graph_filter)
    else:
        local_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)

    data = []

    for philosopher in local_graph.igraph_subgraph.vs:
        data.append(philosopher["name"])

    sorted_data = sorted(data)

    if dataset_selection == 'diogenes':
        return dcc.Dropdown(
            id='ego_local',
            options=[       
                {'label': philosopher, 'value': philosopher}
                for philosopher in sorted_data
            ],
            value="Plato",
            searchable=False,
        ),
    
    if dataset_selection == 'iamblichus':
        return dcc.Dropdown(
            id='ego_local',
            options=[       
                {'label': philosopher, 'value': philosopher}
                for philosopher in sorted_data
            ],
            value="Pythagoras",
            searchable=False,
        ),

@app.callback(
    Output('main_local_netowrk_graph', 'children'),
    Input('dataset_selection_local', 'value'),
    Input('graph_filter_local', 'value'),
    Input('ego_local', 'value'),
    Input('order_local', 'value'),
    Input('show_gender_local', 'value'),
    Input('centrality_index_local', 'value'),
    Input('label_size_local', 'value'),
    Input('node_size_local', 'value'),)
def horus_get_local_graph(dataset_selection,
                        graph_filter,
                        ego_local,
                        order_local,
                        show_gender,
                        centrality_index,
                        label_size,  
                        node_size):

    local_graph = diogenetGraph(
        "local",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    plot_type = "pyvis"
    warning_tie = False
    centrality_index = centrality_index
    node_min_size = int(node_size[0])
    node_max_size = int(node_size[1])
    label_min_size = int(label_size[0])
    label_max_size = int(label_size[1])
    local_graph.current_centrality_index = "Degree"
    not_centrality = False
    graph_filter = graph_filter

    if dataset_selection == 'diogenes':
        if ego_local not in [None, "", "None"]:
            local_graph.local_phylosopher = ego_local
        else:
            local_graph.local_phylosopher = "Plato"
    if dataset_selection == 'iamblichus':
        if ego_local not in [None, "", "None"]:
            local_graph.local_phylosopher = ego_local
        else:
            local_graph.local_phylosopher = "Pythagoras"

    if order_local not in [None, "", "None"]:
        local_graph.local_order = order_local[0]
    else:
        local_graph.local_order = 1

    if centrality_index:
        if centrality_index in [None, "", "None"]:
            local_graph.current_centrality_index = "Degree"
            not_centrality = True
        else:
            local_graph.current_centrality_index = centrality_index

    if not graph_filter:
        local_graph.set_edges_filter("is teacher of")
    else:
        local_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)

    if show_gender:
        local_graph.pyvis_show_gender = True
    else:
        local_graph.pyvis_show_gender = False

    local_graph.create_subgraph()
    pvis_graph = None

    graph_layout = "fr"

    if plot_type == "pyvis":
        pvis_graph = local_graph.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
            avoid_centrality=not_centrality,
        )

    if pvis_graph:
            suffix = ".html"
            temp_file_name = next(tempfile._get_candidate_names()) + suffix
            full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
            pvis_graph.write_html(full_filename)
            return [html.H6('Local Network',className="mt-1 mb-2 text-center"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})]

@app.callback(Output('confirm_warning_tie_local', 'displayed'),
              Input('graph_filter_local', 'value'))
def display_confirm_missing_tie_local_graph(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False

@app.callback(
    Output("download_dataframe_csv_local", "data"),
    Input("btn_csv_local", "n_clicks"),
    Input('dataset_selection_local', 'value'),
    Input('graph_filter_local', 'value'),
    prevent_initial_call=True,
)
def download_handler_local_graph(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_local.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass
############################################ End Callbacks Local Graph #####################################################

############################################ Callbacks Local Graph Centrality #####################################################
@app.callback(
    Output('dropdown_container_local_centrality', 'children'),
    Input('dataset_selection_local_centrality', 'value'),
    Input('graph_filter_local_centrality', 'value'))
def get_philosopher_local_centrality(dataset_selection,
                    graph_filter):

    graph_filter = graph_filter

    local_graph = diogenetGraph(
        "local",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    if not graph_filter:
        graph_filter = "is teacher of"
        local_graph.set_edges_filter(graph_filter)
    else:
        local_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)

    data = []

    for philosopher in local_graph.igraph_subgraph.vs:
        data.append(philosopher["name"])

    sorted_data = sorted(data)

    if dataset_selection == 'diogenes':
        return dcc.Dropdown(
            id='ego_local_centrality',
            options=[       
                {'label': philosopher, 'value': philosopher}
                for philosopher in sorted_data
            ],
            value="Plato",
            searchable=False,
        ),
    
    if dataset_selection == 'iamblichus':
        return dcc.Dropdown(
            id='ego_local_centrality',
            options=[       
                {'label': philosopher, 'value': philosopher}
                for philosopher in sorted_data
            ],
            value="Pythagoras",
            searchable=False,
        ),


@app.callback(
    Output("content_local_centrality", "children"),[
    Input('tabs_local_cetrality', 'value'),
    Input('dataset_selection_local_centrality', 'value'),
    Input('graph_filter_local_centrality', 'value'),
    Input('ego_local_centrality', 'value'),
    Input('order_local_centrality', 'value'),
    Input('show_gender_local_centrality', 'value'),
    Input('centrality_index_local_centrality', 'value'),
    Input('label_size_local_centrality', 'value'),
    Input('node_size_local_centrality', 'value')
    ]
)
def horus_get_local_graph_centrality(
                                    tab,
                                    dataset_selection,
                                    graph_filter,
                                    ego_local,
                                    order_local,
                                    show_gender,
                                    centrality_index,
                                    label_size,  
                                    node_size):
    local_graph = diogenetGraph(
        "local",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    plot_type = "pyvis"
    warning_tie = False
    centrality_index = centrality_index
    node_min_size = int(node_size[0])
    node_max_size = int(node_size[1])
    label_min_size = int(label_size[0])
    label_max_size = int(label_size[1])
    local_graph.current_centrality_index = "Degree"
    not_centrality = False
    graph_filter = graph_filter

    if not graph_filter:
        local_graph.set_edges_filter("is teacher of")
    else:
        local_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)

    def round_list_values(list_in):
        return [round(value, 4) for value in list_in]

    calculated_degree = [round(value) for value in local_graph.calculate_degree()]
    calculated_betweenness = round_list_values(local_graph.calculate_betweenness())
    calculated_closeness = round_list_values(local_graph.calculate_closeness())
    calculated_eigenvector = round_list_values(local_graph.calculate_eigenvector())

    dict_local_data_tables ={
        "Phylosopher": local_graph.get_vertex_names(),
        "Degree": calculated_degree,
        "Betweeness": calculated_betweenness,
        "Closeness": calculated_betweenness,
        "Eigenvector": calculated_eigenvector 
    }

    if tab == "graph_local_cetrality":
    
        if dataset_selection == 'diogenes':
            if ego_local not in [None, "", "None"]:
                local_graph.local_phylosopher = ego_local
            else:
                local_graph.local_phylosopher = "Plato"
        if dataset_selection == 'iamblichus':
            if ego_local not in [None, "", "None"]:
                local_graph.local_phylosopher = ego_local
            else:
                local_graph.local_phylosopher = "Pythagoras"

        if order_local not in [None, "", "None"]:
            local_graph.local_order = order_local[0]
        else:
            local_graph.local_order = 1

        if centrality_index:
            if centrality_index in [None, "", "None"]:
                local_graph.current_centrality_index = "Degree"
                not_centrality = True
            else:
                local_graph.current_centrality_index = centrality_index

        if show_gender:
            local_graph.pyvis_show_gender = True
        else:
            local_graph.pyvis_show_gender = False

        local_graph.create_subgraph()
        pvis_graph = None

        graph_layout = "fr"

        if plot_type == "pyvis":
            pvis_graph = local_graph.get_pyvis(
                min_weight=node_min_size,
                max_weight=node_max_size,
                min_label_size=label_min_size,
                max_label_size=label_max_size,
                layout=graph_layout,
                avoid_centrality=not_centrality,
            )

        if pvis_graph:
                suffix = ".html"
                temp_file_name = next(tempfile._get_candidate_names()) + suffix
                full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
                pvis_graph.write_html(full_filename)
                return html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})

    if tab == "heatmap_local_cetrality":

        interpolated_data = {
            "Phylosopher": dict_local_data_tables["Phylosopher"],
            "Degree": np.interp(
                dict_local_data_tables["Degree"], (min(dict_local_data_tables["Degree"]), max(dict_local_data_tables["Degree"])), (0, +1)
            ),
            "Betweeness": np.interp(
                dict_local_data_tables["Betweeness"],
                (min(dict_local_data_tables["Betweeness"]), max(dict_local_data_tables["Betweeness"])),
                (0, +1),
            ),
            "Closeness": np.interp(
                dict_local_data_tables["Closeness"],
                (min(dict_local_data_tables["Closeness"]), max(dict_local_data_tables["Closeness"])),
                (0, +1),
            ),
            "Eigenvector": np.interp(
                dict_local_data_tables["Eigenvector"],
                (min(dict_local_data_tables["Eigenvector"]), max(dict_local_data_tables["Eigenvector"])),
                (0, +1),
            ),
        }

        df_local_heatmap = pd.DataFrame(interpolated_data).sort_values(["Degree", "Betweeness", "Closeness"])
        
        plotly_graph = go.Figure(
            data=go.Heatmap(
                z=df_local_heatmap[["Degree", "Betweeness", "Closeness", "Eigenvector"]],
                y=df_local_heatmap["Phylosopher"],
                x=["Degree", "Betweeness", "Closeness", "Eigenvector"],
                hoverongaps=False,
                type="heatmap",
                colorscale="Viridis",
            )
        )
        plotly_graph.update_layout(
            legend_font_size=12, legend_title_font_size=12, font_size=8
        )
        
        return html.Div([dcc.Graph(figure=plotly_graph, style={"height": "100%", "width": "100%"})], style={"height": "100%", "width": "100%"})
    
    if tab == "metrics_local_cetrality":
        df_local_data_tables = pd.DataFrame(dict_local_data_tables)

        dt = dash_table.DataTable( 
            id='table-local-graph', 
            columns=[{"name": i, "id": i, 'deletable': True} for i in df_local_data_tables.columns],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                }
            ],
            style_cell={'textAlign': 'center'}, 
            page_current=0,
            page_size=20,
            page_action='custom',
            sort_mode='single',
            sort_by=[{'column_id': 'Degree', 'direction': 'asc'}]
        )
        return [html.H6('Centrality Scores',className="mt-1 mb-2"), html.Hr(className='py-0'), dt]

@app.callback(
    Output('table-local-graph', 'data'),
    Input('table-local-graph', "page_current"),
    Input('table-local-graph', "page_size"),
    Input('table-local-graph', 'sort_by'),
    Input('dataset_selection_local_centrality', 'value'),
    Input('graph_filter_local_centrality', 'value'),
)
def update_table_local_centrality(
                page_current, 
                page_size, 
                sort_by,
                dataset_selection_local_centrality,
                graph_filter_local_centrality,
):
    local_graph = diogenetGraph(
                "local",
                dataset_selection_local_centrality,
                dataset_selection_local_centrality,
                'locations_data.csv',
                'travels_blacklist.csv'
            )

    graph_filter = graph_filter_local_centrality


    if not graph_filter:
            local_graph.set_edges_filter("is teacher of")
    else:
        local_graph.edges_filter = []
        filters = graph_filter
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)
        
    def round_list_values(list_in):
        return [round(value, 4) for value in list_in]

    calculated_degree = [round(value) for value in local_graph.calculate_degree()]
    calculated_betweenness = round_list_values(local_graph.calculate_betweenness())
    calculated_closeness = round_list_values(local_graph.calculate_closeness())
    calculated_eigenvector = round_list_values(local_graph.calculate_eigenvector())

    dict_local_data_tables ={
        "Phylosopher": local_graph.get_vertex_names(),
        "Degree": calculated_degree,
        "Betweeness": calculated_betweenness,
        "Closeness": calculated_betweenness,
        "Eigenvector": calculated_eigenvector 
    }

    df_local_data_tables = pd.DataFrame(dict_local_data_tables)
    
    print(sort_by)
    if len(sort_by):
        dff = df_local_data_tables.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'desc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = df_local_data_tables

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

@app.callback(Output('confirm-warning-tie-local-centrality', 'displayed'),
              Input('graph_filter_local_centrality', 'value'))
def display_confirm_missing_tie_local_graph_centrality(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False

@app.callback(
    Output("download_dataframe_csv_local_centrality", "data"),
    Input("btn_csv_local_centrality", "n_clicks"),
    Input('dataset_selection_local_centrality', 'value'),
    Input('graph_filter_local_centrality', 'value'),
    prevent_initial_call=True,
)
def download_handler_local_graph_centrality(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_local_centrality.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass
############################################ End Callbacks Local Graph Centrality #####################################################

############################################ Callbacks Communities Graph #####################################################
@app.callback(
    Output('main-netowrk-graph-communities', 'children'),
    Input('dataset_selection_communities', 'value'),
    Input('graph_filter_communities', 'value'),
    Input('graph_algorithm_communities', 'value'),
    Input('show_gender_communities', 'value'),
    Input('visualization_communities', 'value'),
    Input('crossing_ties_communities', 'value'),
    Input('label_size_communities', 'value'),
    Input('node_size_communities', 'value'),)
def horus_get_communities_graph(
                        dataset_selection,
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
    not_centrality = False
    graph_layout = "fr"
    plot_type = visualization
    communities_graph.current_centrality_index = "communities"
    communities_graph.comm_alg = str(graph_algorithm)
    communities_graph.set_graph_layout(graph_layout)

    if crossing_ties:
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

    if show_gender:
        communities_graph.pyvis_show_gender = True
    else:
        communities_graph.pyvis_show_gender = False

    communities_graph.create_subgraph()
    subgraph = communities_graph
    modularity, clusters_dict = subgraph.identify_communities()
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
        full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
        pvis_graph.write_html(full_filename)
        return [html.H6('Graph',className="mt-1 mb-2 text-center"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})]

    if plot_type == "igraph":
        pass
        # edges_for_grap = communities_graph.create_edges_for_graph()
        # # list of edges
        # E=[e.tuple for e in communities_graph.get_edges_names()]
        


        # fig, ax = plt.subplots()
        # modularity, clusters = communities_graph.identify_communities()
        # dendogram_communities_list = [
        #     "community_edge_betweenness",
        #     "community_walktrap",
        #     "community_fastgreedy",
        # ]
        # communities_graph.igraph_subgraph.vs["label"] = communities_graph.igraph_subgraph.vs["name"]
        # #if communities_graph.comm_alg not in dendogram_communities_list:
        # plot(
        #     communities_graph.igraph_graph,
        #     target=ax,
        #     layout=communities_graph.graph_layout,
        #     bbox=(450, 450),
        #     margin=20,
        #     mark_groups=True,
        #     vertex_label_size=7,
        #     vertex_label_angle=200,
        #     vertex_label_dist=1,
        #     vertex_size=8,
        # )
        # suffix = '.png'
        # temp_file_name = next(tempfile._get_candidate_names()) + suffix
        # full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
        # fig.savefig(full_filename)
        # return [html.Img(src=full_filename)]

        #     suffix = ".svg" 
        #     temp_file_name = next(tempfile._get_candidate_names()) + suffix
        #     full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
        #     if plot_type == "igraph":


        #         with open(full_filename, "r") as file:
        #             if communities_graph.comm_alg not in dendogram_communities_list:
        #                 data = file.read().replace('width="450pt"', 'width="100%"')
        #             else:
        #                 data = file.read()
        #             full_html_file_content = HTML_PLOT_CONTENT.format(file=data)
        #             temp_html_file_name = (
        #                 next(tempfile._get_candidate_names()) + HTML_SUFFIX
        #             )
        #             full_html_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))
        #             full_html_file = open(full_html_filename, "w")
        #             _ = full_html_file.write(full_html_file_content)
        #             full_html_file.close()
        #             full_filename = full_html_filename
        #     else:
        #         pvis_graph.write_html(full_filename)

        # # print(full_filename)

@app.callback(Output('confirm-warning-tie-coomunities', 'displayed'),
              Input('graph_filter_communities', 'value'))
def display_confirm_missing_tie_communities_graph(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False   

@app.callback(
    Output("download_dataframe_csv_community_graph", "data"),
    Input("btn_csv_community_graph", "n_clicks"),
    Input('dataset_selection_communities', 'value'),
    Input('graph_filter_communities', 'value'),
    prevent_initial_call=True,
)
def download_handler_communities_graph(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_community_graph.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass
############################################ End Callbacks Communities Graph #####################################################

############################################ Callbacks Communities Treemap #####################################################
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
def display_confirm_missing_tie_communities_treemap(graph_filter_global):
    if len(graph_filter_global) == 0:
        return True
    return False    

@app.callback(
    Output("download_dataframe_csv_community_treemap", "data"),
    Input("btn_csv_community_treemap", "n_clicks"),
    Input('dataset_selection_communities_treemap', 'value'),
    Input('graph_filter_communities_treemap', 'value'),
    prevent_initial_call=True,
)
def download_handler_communities_treemap(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_community_treemap.n_clicks':
        # list of avaiable datasets in /data for download
        dataset_list_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data','datasetList.csv'))
        dataset_list_df = pd.read_csv(dataset_list_path)

        if n_clicks is None:
            raise PreventUpdate
        else:
            m1 = dataset_list_df['name'] == str(dataset_selection)
            m2 = dataset_list_df['type'] == 'edges'

            edges_path_name = str(list(dataset_list_df[m1&m2]['path'])[0])
            full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data', edges_path_name))

            #print(full_filename_csv)
            df = pd.read_csv(full_filename_csv)
            df_to_save = df[df["Relation"].isin(graph_filter)]
            #print(df[df["Relation"].isin(graph_filter)])
            return dcc.send_data_frame(df_to_save.to_csv, 'edges.csv')
    else:
        pass
############################################ End Callbacks Communities Treemap #####################################################

if __name__ == '__main__':
    app.run_server(debug=True)