import dash
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
    id='navbar_local'
)

sidebar_content = [
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

row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar_local', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
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

layout = html.Div(
    [
    row
    ],  
    style={"height": "100vh"}
)

@app.callback(
    Output('dropdown_container_local', 'children'),
    Input('dataset_selection_local', 'value'),
    Input('graph_filter_local', 'value'))
def get_philosopher(dataset_selection,
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
            full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
            pvis_graph.write_html(full_filename)
            return [html.H6('Local Network',className="mt-1 mb-2 text-center"), html.Hr(className='py-0'), html.Iframe(src=f"/assets/{temp_file_name}",style={"height":"1050px", "width": "100%"})]

@app.callback(Output('confirm_warning_tie_local', 'displayed'),
              Input('graph_filter_local', 'value'))
def display_confirm(graph_filter_global):
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
def func(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_local.n_clicks':
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