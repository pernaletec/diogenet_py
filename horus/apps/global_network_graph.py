from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pathlib
import os
import sys
import requests
import tempfile
import pandas as pd
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
        dbc.NavLink("Horus Main", href="/", style=STYLE_A_ITEM),
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Graph", href="#"), dbc.DropdownMenuItem("Graph + centrality", href="/apps/global_network_graph_centrality")],
            label="Global Network",
            style=STYLE_A_ITEM,
            color="#1a6ecc"
        ),
    ],
    color="#1a6ecc",
    style={'color':'#ffffff'},
    id='Navbar'
)

sidebar_content = [
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
    dbc.Button("Download Data", id="btn_csv", color="secondary", className="ml-3"),
    dcc.Download(id="download-dataframe-csv"),
]



row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
                dbc.Col(id='main-netowrk-graph'),
            ],
            className='h-100'
        ),
    ],
    className='h-100',
    style={'padding':'0px 10px'}
)

layout = html.Div([
    row
],  style={"height": "100vh"})

# Update the index

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
    node_min_size = int(label_size_global[0])
    node_max_size = int(label_size_global[1])
    label_min_size = int(node_size_global[0])
    label_max_size = int(node_size_global[1])
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
        full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
        pvis_graph.write_html(full_filename)
        return [html.H6('Global Network',className="mt-1 mb-2"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height": "100vh", "width": "100%"})]

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input('dataset_selection', 'value'),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(dataset_selection, n_clicks):
    if dataset_selection == 'diogenes':
        full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data','new_Edges.csv'))
    elif dataset_selection == 'iamblichus':
        full_filename_csv = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data','new_Edges_Life_of_Pythagoras_Iamblichus.csv'))
    
    if n_clicks is None:
        raise PreventUpdate
    else:
        print(full_filename_csv)
        df = pd.read_csv(full_filename_csv)
        print(df.head())
        return dcc.send_data_frame(df.to_csv, 'edges.csv')
    
