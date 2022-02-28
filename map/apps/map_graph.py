import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
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
                dbc.NavLink("Traveler", style=STYLE_A_ITEM),
            ],
            className="d-flex",

        ),
    ],
    color="#1a6ecc",
    className="d-flex justify-content-between",
    style={'color':'#ffffff'},
    id='navbar-map'
)

sidebar_content = [
    html.H5('Dataset selection', className="mt-3 mb-3"),
    dcc.Dropdown(
        id='dataset_selection_map',
        options=[
            {'label': key, 'value': value}
            for key, value in dict_of_datasets.items()
        ],
        searchable=False,
        placeholder="Select a dataset",
        value='diogenes'
    ),
    html.H5('traveler',className="mt-5 mb-3"),
    html.Div(
        id='dropdown_container_traveler',
        children=[]
    ),
    html.H5('Centrality type',className="mt-5 mb-3"),
    dcc.Dropdown(
        id='centrality_type_map',
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
        id='label_size_map',
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
        id='node_size_map',
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
    html.H6('Download travel edges graph data',className="mt-5 mb-3"),
    dbc.Button("Download Data", id="btn_csv_map", color="secondary", className="ml-3"),
    dcc.Download(id="download-dataframe-csv-map"),
]

tabs = dcc.Tabs(
        id='tabs_map', 
        value='map_graph',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Map', 
                value='map_maps',
                className='custom-tab',
                selected_className='custom-tab--selected'    
            ),
                
            dcc.Tab(
                label='Metrics', 
                value='map_metrics',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Graph', 
                value='map_graphs',
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
        ])

row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar_map', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div(children=[tabs, html.Div(id="content_map", style={'height': '100vh'}, children=[])]), id='main_map'),
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

layout = html.Div(
    [
    row
    ],  
    style={"height": "100vh"}
)

@app.callback(
    Output('dropdown_container_traveler', 'children'),
    Input('dataset_selection_map', 'value'),)
def get_traveler(dataset_selection):
    map_graph = diogenetGraph(
    "map",
    dataset_selection,
    dataset_selection,
    'locations_data.csv',
    'travels_blacklist.csv'
    )
    
    list_of_traveler = sorted(list(set(map_graph.get_edges_names())))

    return dcc.Dropdown(
        id='traveler_map',
        options=[       
            {'label': traveler, 'value': traveler}
            for traveler in list_of_traveler
        ],
        value="All",
        searchable=False,
        multi=True
    ),

@app.callback(
    Output("content_map", "children"),[
    Input('tabs_map', 'value'),
    Input('dataset_selection_map', 'value'),
    Input('traveler_map','value'),
    Input('centrality_type_map', 'value'),
    Input('label_size_map', 'value'),
    Input('node_size_map', 'value')
    ]
)
def horus_get_local_graph_centrality(
                                    tab,
                                    dataset_selection,
                                    traveler,
                                    centrality_index,
                                    label_size,  
                                    node_size):

    map_graph = diogenetGraph(
    "map",
    dataset_selection,
    dataset_selection,
    'locations_data.csv',
    'travels_blacklist.csv'
    )    

    if tab == "map_maps":
        map_graph.current_centrality_index = centrality_index
        if traveler == "All" or traveler == []:
            map_graph.edges_filter = []
        if traveler != "All" or traveler != []:
            for m_filter in traveler:
                map_graph.set_edges_filter(m_filter)

        map_graph.create_subgraph()
        data = map_graph.get_map_data(min_weight=node_size[0], max_weight=node_size[1])
        all_data = map_graph.get_max_min()
        if data:
            all_data["data"] = data

        print(all_data)
        return "map"

    if tab == "map_metrics":

        def get_map_data_table(filter_string):
            graph = None
            graph = map_graph
            if filter_string != "All" or filter_string != []:
                for m_filter in filter_string:
                    graph.set_edges_filter(m_filter)
                graph.create_subgraph()
            return (
                graph.get_vertex_names(),
                graph.calculate_degree(),
                graph.calculate_betweenness(),
                graph.calculate_closeness(),
                graph.calculate_eigenvector(),
            )

        
        if traveler == "All" or traveler == []:
            traveler = "All"

        graph_type = "map"
        data = []
        cities = degree = betweeness = closeness = eigenvector = []

        if graph_type == "map":
            (cities, degree, betweeness, closeness, eigenvector) = get_map_data_table(
                traveler
            )

        for (
        city_name,
        city_degree,
        city_betweeness,
        city_closeness,
        city_eigenvector,
        ) in zip(cities, degree, betweeness, closeness, eigenvector):
            record = {
                "City": city_name,
                "Degree": city_degree,
                "Betweenness": city_betweeness,
                "Closeness": city_closeness,
                "Eigenvector": city_eigenvector,
            }
            data.append(record)

        data_table = {}
        data_table["CentralizationDegree"] = map_graph.centralization_degree()
        data_table["CentralizationBetweenness"] = map_graph.centralization_betweenness()
        data_table["CentralizationCloseness"] = map_graph.centralization_closeness()
        data_table["CentralizationEigenvector"] = map_graph.centralization_eigenvector()
        data_table["CityData"] = data

        print(data_table)

        return  "metrics"
    
    if tab == "map_graphs":

        map_graph.current_centrality_index = centrality_index
        
        graph_layout = "fr"
        pvis_graph = None

        if traveler == "All" or traveler == []:
            #map_graph.edges_filter = []
            pvis_graph = map_graph.get_pyvis(
                min_weight=node_size[0],
                max_weight=node_size[1],
                min_label_size=label_size[0],
                max_label_size=label_size[1],
                layout=graph_layout,
            )
        else:
            for m_filter in traveler:
                map_graph.set_edges_filter(m_filter)
            map_graph.create_subgraph()
            pvis_graph = map_graph.get_pyvis()

        if pvis_graph:
            suffix = ".html"
            temp_file_name = next(tempfile._get_candidate_names()) + suffix
            full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))

            pvis_graph.write_html(full_filename)
            return [html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"100%", "width": "100%"})]