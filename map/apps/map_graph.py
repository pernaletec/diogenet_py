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
        value='map_maps',
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
def get_map_map(
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

        all_data = {}
        data = None
        df = None
        map_graph.current_centrality_index = centrality_index
        if traveler == "All":
            map_graph.edges_filter = []
        elif traveler == []:
            map_graph.edges_filter = []
        else:
            for m_filter in traveler:
                map_graph.set_edges_filter(m_filter)

        map_graph.create_subgraph()
        data = map_graph.get_map_data(min_weight=node_size[0], max_weight=node_size[1])
        all_data = map_graph.get_max_min()
        if data:
            all_data["data"] = data

        df = pd.DataFrame(data)
    
        fig = go.Figure()
        list_text_from=[]
        list_text_to=[]
        for i in range(len(df)):
            list_text_from.append(f'{df["Philosopher"][i]} travel from {df["Source"][i]} ({round(df["SourceLatitude"][i],2)}°, {round(df["SourceLongitude"][i],2)}°) to {df["Destination"][i]} ')

            list_text_to.append(f'{df["Philosopher"][i]} travel from {df["Source"][i]} to {df["Destination"][i]} ({round(df["DestLatitude"][i],2)}°, {round(df["DestLongitude"][i],2)}°)')

        
        
        fig.add_trace(go.Scattergeo(
            lon = df["SourceLongitude"],
            lat = df["SourceLatitude"],
            hoverinfo = 'text',
            text = list_text_from,
            mode = 'markers',
            showlegend=False,
            marker = dict(
                size = df["SourceSize"],
                color = df["SourceColor"],
                line = dict(
                    width = df["SourceSize"],
                    color = df["SourceColor"]
                )
        )))

        fig.add_trace(go.Scattergeo(
            lon = df["DestLongitude"],
            lat = df["DestLatitude"],
            hoverinfo = 'text',
            text = list_text_to,
            mode = 'markers',
            showlegend=False,
            marker = dict(
                size = df["DestinationSize"],
                color = df["DestinationSize"],
                showscale=False,
                line = dict(
                    width = df["DestinationSize"],
                    color = df["DestinationSize"]
                )
        )))


        for i in range(len(df)):
            fig.add_trace(
                go.Scattergeo(
                    lon = [df["SourceLongitude"][i], df["DestLongitude"][i]],
                    lat = [df["SourceLatitude"][i], df["DestLatitude"][i]],
                    hoverinfo='skip',
                    mode = 'lines',
                    line = dict(width = 1,color = 'black'),
                    showlegend=False,
                )
            )

        fig.update_layout(
            showlegend = False,
            margin ={'l':0,'t':0,'b':0,'r':0},
            mapbox = {
                'style': "stamen-terrain",
                'center': {'lon': -50, 'lat': -80},
                'zoom': 2}
        )

        return dcc.Graph(figure=fig, style={"height": "100%", "width": "100%"})

    if tab == "map_metrics":
        
        if traveler == "All":
            all_travelers = sorted(list(set(map_graph.get_edges_names())))
            map_graph.edges_filter = []
            for m_filter in all_travelers:
                map_graph.set_edges_filter(m_filter)
            map_graph.create_subgraph()
        elif traveler == []:
            all_travelers = sorted(list(set(map_graph.get_edges_names())))
            map_graph.edges_filter = []
            for m_filter in all_travelers:
                map_graph.set_edges_filter(m_filter)
            map_graph.create_subgraph()
        else:
            map_graph.edges_filter = []
            for m_filter in traveler:
                map_graph.set_edges_filter(m_filter)
            map_graph.create_subgraph()

        def round_list_values(list_in):
            return [round(value, 4) for value in list_in]

        calculated_degree = [round(value) for value in map_graph.calculate_degree()]
        calculated_betweenness = round_list_values(map_graph.calculate_betweenness())
        calculated_closeness = round_list_values(map_graph.calculate_closeness())
        calculated_eigenvector = round_list_values(map_graph.calculate_eigenvector())

        dict_map_data_tables ={
            "City": map_graph.get_vertex_names(),
            "Degree": calculated_degree,
            "Betweeness": calculated_betweenness,
            "Closeness": calculated_betweenness,
            "Eigenvector": calculated_eigenvector 
        }

        df_map_data_tables = pd.DataFrame(dict_map_data_tables)
        
        dt_map = dash_table.DataTable( 
            id='table-map', 
            columns=[{"name": i, "id": i, 'deletable': True} for i in df_map_data_tables.columns],
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
        
        return [html.H6('Centrality Scores',className="mt-1 mb-2"), html.Hr(className='py-0'), dt_map]
    
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


@app.callback(
    Output('table-map', 'data'),
    Input('table-map', "page_current"),
    Input('table-map', "page_size"),
    Input('table-map', 'sort_by'),
    Input('dataset_selection_map', 'value'),
    Input('traveler_map','value'),
)
def update_table(
                page_current, 
                page_size, 
                sort_by,
                dataset_selection,
                traveler,
):
    map_graph = diogenetGraph(
        "map",
        dataset_selection,
        dataset_selection,
        'locations_data.csv',
        'travels_blacklist.csv'
    )

    if traveler == "All":
        all_travelers = sorted(list(set(map_graph.get_edges_names())))
        map_graph.edges_filter = []
        for m_filter in all_travelers:
            map_graph.set_edges_filter(m_filter)
        map_graph.create_subgraph()
    elif traveler == []:
        all_travelers = sorted(list(set(map_graph.get_edges_names())))
        map_graph.edges_filter = []
        for m_filter in all_travelers:
            map_graph.set_edges_filter(m_filter)
        map_graph.create_subgraph()
    else:
        map_graph.edges_filter = []
        for m_filter in traveler:
            map_graph.set_edges_filter(m_filter)
        map_graph.create_subgraph()

    def round_list_values(list_in):
        return [round(value, 4) for value in list_in]

    calculated_degree = [round(value) for value in map_graph.calculate_degree()]
    calculated_betweenness = round_list_values(map_graph.calculate_betweenness())
    calculated_closeness = round_list_values(map_graph.calculate_closeness())
    calculated_eigenvector = round_list_values(map_graph.calculate_eigenvector())

    dict_map_data_tables ={
        "City": map_graph.get_vertex_names(),
        "Degree": calculated_degree,
        "Betweeness": calculated_betweenness,
        "Closeness": calculated_betweenness,
        "Eigenvector": calculated_eigenvector 
    }
    df_map_data_tables = pd.DataFrame(dict_map_data_tables)
    
    print(sort_by)
    if len(sort_by):
        dff = df_map_data_tables.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'desc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = df_map_data_tables

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

@app.callback(
    Output("download-dataframe-csv-map", "data"),
    Input("btn_csv_map", "n_clicks"),
    Input('dataset_selection_map', 'value'),
    Input('traveler_map','value'),
    Input('centrality_type_map', 'value'),
    Input('label_size_map', 'value'),
    Input('node_size_map', 'value'),
    prevent_initial_call=True,
)
def download_handler(n_clicks, 
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

    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_map.n_clicks':

        data = None
        df = None
        map_graph.current_centrality_index = centrality_index
        if traveler == "All":
            map_graph.edges_filter = []
        elif traveler == []:
            map_graph.edges_filter = []
        else:
            for m_filter in traveler:
                map_graph.set_edges_filter(m_filter)

        map_graph.create_subgraph()
        data = map_graph.get_map_data(min_weight=node_size[0], max_weight=node_size[1])

        df = pd.DataFrame(data)

        if n_clicks is None:
            raise PreventUpdate
        else:
            if traveler == "All":
                all_travelers = sorted(list(set(map_graph.get_edges_names())))
                df_to_save = df[df["Philosopher"].isin(all_travelers)]
            elif traveler == []:
                all_travelers = sorted(list(set(map_graph.get_edges_names())))
                df_to_save = df[df["Philosopher"].isin(all_travelers)]
            else:
                df_to_save = df[df["Philosopher"].isin(traveler)]
            return dcc.send_data_frame(df_to_save.to_csv, 'travel_edges_graph.csv')
    else:
        pass