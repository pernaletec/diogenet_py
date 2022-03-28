import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
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
import base64
import datetime
import io
import networkx as nx

from data_analysis_module.network_graph import diogenetGraph

app = dash.Dash(__name__,
        external_stylesheets= [dbc.themes.BOOTSTRAP, 
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap"], 
        title="Map", url_base_pathname = '/map_private/') 

# for develop mode uncomment this line
app.config.suppress_callback_exceptions = True 

server = app.server

############################################# Map graph layout###################################
dict_of_datasets = {'Diogenes Laertius': 'diogenes', 'Life of Pythagoras Iamblichus': 'iamblichus', 'Custom Dataset': 'custom'}

STYLE_A_ITEM = {
    'color':'#ffffff',
    'textDecoration': 'none',
    'marginRight': '12px',
    'marginLeft': '12px',
    'fontSize': '16px',
    'letterSpacing':'4px',
    'font-weight':'400',
    'padding': '12px'
}

navbar = dbc.Navbar(
    children=[
        html.Div(
            [
                dbc.NavLink("Map", style=STYLE_A_ITEM),
                dbc.NavLink("Traveler", style=STYLE_A_ITEM),
            ],
            className="d-flex",
        ),
        dbc.NavLink(
            [
                html.I(className="bi bi-house-fill me-2 text-white")
            ], 
            href="https://diogenet.ucsd.edu/", style=STYLE_A_ITEM,
            target="blank"
        )
    ],
    color="#000000",
    className="d-flex justify-content-between",
    style={'color':'#ffffff', 'border-bottom': '1px black solid'},
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
    dbc.Button("Download Data", id="btn_csv_map", style={'backgroundColor': '#716450'}, className="ml-3"),
    dcc.Download(id="download-dataframe-csv-map"),
    html.H6('Upload travel dataset',className="mt-5 mb-3"),
    dcc.Upload(
            id='upload-data',
            children = dbc.Button('Upload File', id="btn_upload_csv_map", style={'backgroundColor': '#716450'}, className="ml-3"),

            multiple=False
        ),
    html.Div(id='output-data-upload',children=[]),
    dcc.Store(id='memory-output')
]

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    df = None
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            #print(df)
            return df.to_dict('records')
    else: 
        pass
        

tabs = dcc.Tabs(
        id='tabs_map', 
        value='map_maps',
        parent_className='custom-tabs',
        className='custom-tabs-container',
        children=[
            dcc.Tab(
                label='Map', 
                value='map_maps',
                id='map-maps',
                className='custom-tab',
                selected_className='custom-tab--selected'    
            ),
                
            dcc.Tab(
                label='Metrics', 
                value='map_metrics',
                id="map-metrics",
                className='custom-tab',
                selected_className='custom-tab--selected'
            ),
            dcc.Tab(
                label='Graph', 
                id="map-graphs",
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
                dbc.Col(html.Div(sidebar_content), id='sidebar_map', width=3, style={"backgroundColor": "#eee", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div(children=[tabs, html.Div(id="content_map", style={'height': '100vh'}, children=[])]), id='main_map'),
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
######################################## end map graph layout ####################################

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content-map', children=[])
])

# Update the index
@app.callback(Output('page-content-map', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/map_private/':
        return layout
    elif pathname != '/' or pathname != '/map_private/':
        return '404'

############################################# map graph callbacks ######################################
@app.callback(
    [Output("map-metrics", "disabled"), Output("map-graphs", "disabled")],
    [Input("dataset_selection_map", "value")],
)
def disabled_if_custom(dataset_selection):
    if dataset_selection == 'custom':
        return True, True
    else: 
        return False, False


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def warning_processing_file(content, name): 
    if content is not None:
        if 'csv' in name:
                pass
        else: 
            return html.Div([
            dcc.ConfirmDialog(
                        id='warning_upload_map',
                        message='There was an error processing this file. Repeat the process',
                        displayed=True
                    ),
        ])


@app.callback(Output('memory-output', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_data_store(content, name, date): 
    if content is not None:
        content_type, content_string = content.split(',')
        df = None
        decoded = base64.b64decode(content_string)
        if 'csv' in name:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
                #print(df)
                return df.to_dict('records')
        else: 
            pass


@app.callback(
    Output('dropdown_container_traveler', 'children'),
    Input('dataset_selection_map', 'value'),
    Input('memory-output', 'data'))
def get_traveler(dataset_selection,
                dataframe_upload):
    
    if dataset_selection == "custom" and dataframe_upload is not None:
        df = pd.DataFrame.from_dict(dataframe_upload)
        sorted_list_name = sorted(list(set(df['name'])))
        return dcc.Dropdown(
            id='traveler_map',
            options=[       
                {'label': traveler, 'value': traveler}
                for traveler in sorted_list_name
            ],
            value="All",
            searchable=False,
            multi=True
        ),
    if dataset_selection != "custom":
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
    Input('node_size_map', 'value'),
    Input('memory-output', 'data')
    ]
)
def get_map_map_custom(
                                    tab,
                                    dataset_selection,
                                    traveler,
                                    centrality_index,
                                    label_size,  
                                    node_size,
                                    dataframe_upload):

    if dataset_selection == 'custom' and dataframe_upload is not None:
        map_graph = diogenetGraph(
        "map",
        "diogenes",
        "diogenes",
        'locations_data.csv',
        'travels_blacklist.csv'
        )
        
        if tab == "map_maps":
            #print(traveler)
            df_to_search_data = pd.DataFrame.from_dict(dataframe_upload)
            if traveler == "All" or len(traveler)==0:
                df = map_graph.create_edges_for_custom_map(df_to_search_data)
            else:
                df_prev_filter = map_graph.create_edges_for_custom_map(df_to_search_data)
                df_prev_filter_copy = df_prev_filter.copy()
                df = df_prev_filter_copy.loc[df_prev_filter_copy['name'].isin(list(traveler))].reset_index(drop=True)

            fig = go.Figure()
            list_text_from=[]
            list_text_to=[]
            list_text_line=[]

            for i in range(len(df)):
                list_text_from.append(f'{df["source"][i]} ({round(df["lat_source"][i],2)}°, {round(df["lon_source"][i],2)}°)')

                list_text_to.append(f'{df["target"][i]} ({round(df["lat_target"][i],2)}°, {round(df["lon_target"][i],2)}°)')

                list_text_line.append(f'{df["name"][i]} travel from {df["source"][i]} to {df["target"][i]}')

            fig.add_trace(go.Scattermapbox(
                lat=df["lat_source"],
                lon=df["lon_source"],
                mode='markers+text',
                marker=go.scattermapbox.Marker(
                    size = 4*3.5,
                    color = df["color_source"]
                ),
                text=list_text_from,
                hoverinfo="text",
                showlegend=False
            ))

            fig.add_trace(go.Scattermapbox(
                lon=df["lon_target"],
                lat=df["lat_target"],
                mode='markers+text',
                marker=go.scattermapbox.Marker(
                    size = 4*3.5,
                    color = df["color_target"]
                ),
                text=list_text_to,
                hoverinfo="text",
                showlegend=False
            ))

            for i in range(len(df["target"])):

                fig.add_trace(
                    go.Scattermapbox(
                        mode = "lines",
                        lon = [round(df["lon_source"][i],2), round(df["lon_target"][i],3)],
                        lat = [round(df["lat_source"][i],2), round(df["lat_target"][i],3)],
                        text=f'{df["name"][i]} travel from {df["source"][i]} to {df["target"][i]}',
                        hoverinfo='text',
                        showlegend=False,
                        line = dict(width = 1,color = '#ced4da'),
                    )
                )

            fig.update_layout(
                mapbox_style="white-bg",
                mapbox = {
                    'center': {'lon': 35, 'lat': 30},
                    'zoom': 3.2},
                mapbox_layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ])
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            return dcc.Graph(figure=fig, style={"height": "100%", "width": "100%"})
            
        
    if dataset_selection != 'custom':
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
            #print(df)
        
            fig = go.Figure()
            list_text_from=[]
            list_text_to=[]
            list_text_line=[]
            for i in range(len(df)):
                list_text_from.append(f'{df["Source"][i]} ({round(df["SourceLatitude"][i],2)}°, {round(df["SourceLongitude"][i],2)}°)')

                list_text_to.append(f'{df["Destination"][i]} ({round(df["DestLatitude"][i],2)}°, {round(df["DestLongitude"][i],2)}°)')

                list_text_line.append(f'{df["Philosopher"][i]} travel from {df["Source"][i]} to {df["Destination"][i]}')

                

            fig.add_trace(go.Scattermapbox(
                lat=df["SourceLatitude"],
                lon=df["SourceLongitude"],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size = df["SourceSize"]*3.5,
                    color = df["SourceColor"]
                ),
                text=list_text_from,
                hoverinfo='text',
                showlegend=False
            ))

            fig.add_trace(go.Scattermapbox(
                lon=df["DestLongitude"],
                lat=df["DestLatitude"],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size = df["DestinationSize"]*3.5,
                    color = df["DestinationColor"]
                ),
                text=list_text_to,
                hoverinfo='text',
                showlegend=False
            ))

            for i in range(len(df)):
                fig.add_trace(
                    go.Scattermapbox(
                        mode = "lines",
                        lon = [df["SourceLongitude"][i], df["DestLongitude"][i]],
                        lat = [df["SourceLatitude"][i], df["DestLatitude"][i]],
                        text=f'{df["Philosopher"][i]} travel from {df["Source"][i]} to {df["Destination"][i]}',
                        hoverinfo='text',
                        showlegend=False,
                        line = dict(width = 1,color = '#ced4da'),
                    )
                )

            fig.update_layout(
                mapbox_style="white-bg",
                mapbox = {
                    'center': {'lon': 35, 'lat': 30},
                    'zoom': 3.2},
                mapbox_layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ])
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
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
 
            
            calculated_network_betweenness = list(pd.DataFrame.from_dict(nx.betweenness_centrality(map_graph.networkx_subgraph).items())[1])
            calculated_network_degree = list(pd.DataFrame.from_dict(nx.degree_centrality(map_graph.networkx_subgraph).items())[1])
            calculated_network_closeness = list(pd.DataFrame.from_dict(nx.closeness_centrality(map_graph.networkx_subgraph).items())[1])
            calculated_network_eigenvector = list(pd.DataFrame.from_dict(nx.eigenvector_centrality(map_graph.networkx_subgraph).items())[1])

            calculated_degree = [round(value) for value in map_graph.calculate_degree()]
            calculated_betweenness = round_list_values(map_graph.calculate_betweenness())
            calculated_closeness = round_list_values(map_graph.calculate_closeness())
            calculated_eigenvector = round_list_values(map_graph.calculate_eigenvector())

            dict_map_data_tables ={
                "City": map_graph.get_vertex_names(),
                "Degree": round_list_values(calculated_network_degree),
                "Betweeness": round_list_values(calculated_network_eigenvector),
                "Closeness": round_list_values(calculated_network_closeness),
                "Eigenvector": round_list_values(calculated_network_eigenvector), 
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
                style_header={'textAlign': 'center'},
                page_current=0,
                page_size=20,
                page_action='custom',
                sort_mode='single',
                sort_by=[{'column_id': 'Degree', 'direction': 'asc'}]
            )
            foot_note = html.Div(children=[html.Span('Metrics obtained using the algorithms of '), html.A('Networkx', href='https://networkx.org/documentation/stable/', target='_blank')])
            return [html.H6('Centrality Scores',className="mt-1 mb-2"), html.Hr(className='py-0'), dt_map, foot_note]
        
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
                full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '.', 'assets',temp_file_name))

                pvis_graph.write_html(full_filename)
                return [html.Iframe(src=app.get_asset_url(f'{temp_file_name}'),style={"height":"100%", "width": "100%"})]


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

    calculated_network_betweenness = list(pd.DataFrame.from_dict(nx.betweenness_centrality(map_graph.networkx_subgraph).items())[1])
    calculated_network_degree = list(pd.DataFrame.from_dict(nx.degree_centrality(map_graph.networkx_subgraph).items())[1])
    calculated_network_closeness = list(pd.DataFrame.from_dict(nx.closeness_centrality(map_graph.networkx_subgraph).items())[1])
    calculated_network_eigenvector = list(pd.DataFrame.from_dict(nx.eigenvector_centrality(map_graph.networkx_subgraph).items())[1])
    
    calculated_degree = [round(value) for value in map_graph.calculate_degree()]
    calculated_betweenness = round_list_values(map_graph.calculate_betweenness())
    calculated_closeness = round_list_values(map_graph.calculate_closeness())
    calculated_eigenvector = round_list_values(map_graph.calculate_eigenvector())

    dict_map_data_tables ={
        "City": map_graph.get_vertex_names(),
        "Degree": round_list_values(calculated_network_degree),
        "Betweeness": round_list_values(calculated_network_eigenvector),
        "Closeness": round_list_values(calculated_network_closeness),
        "Eigenvector": round_list_values(calculated_network_eigenvector), 
    }

    df_map_data_tables = pd.DataFrame(dict_map_data_tables)
    
    #print(sort_by)
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
    Input('memory-output', 'data'),
    prevent_initial_call=True,
)
def download_handler(n_clicks, 
                    dataset_selection,
                    traveler,
                    centrality_index,
                    label_size,  
                    node_size,
                    dataframe_upload):

    if dataset_selection == 'custom':
        map_graph = diogenetGraph(
        "map",
        "diogenes",
        "diogenes",
        'locations_data.csv',
        'travels_blacklist.csv'
        )

        df_to_search_data = pd.DataFrame.from_dict(dataframe_upload)

        if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_map.n_clicks':
            if n_clicks is None:
                raise PreventUpdate
            else:
                if traveler == "All" or len(traveler)==0:
                    df = map_graph.create_edges_for_custom_map(df_to_search_data)
                    header= ["name", "source", "target", "lat_source", "lon_source", "lat_target", "lon_target"]
                    return dcc.send_data_frame(df.to_csv, 'travel_edges_graph.csv', columns=header)
                else:
                    df_prev_filter = map_graph.create_edges_for_custom_map(df_to_search_data)
                    df_prev_filter_copy = df_prev_filter.copy()
                    df = df_prev_filter_copy.loc[df_prev_filter_copy['name'].isin(list(traveler))].reset_index(drop=True)
                    header= ["name", "source", "target", "lat_source", "lon_source", "lat_target", "lon_target"]
                    return dcc.send_data_frame(df.to_csv, 'travel_edges_graph.csv', columns=header)
        else:
            pass
            

    if dataset_selection != 'custom':
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

                header = ['source', 'target', 'name', 'SourceLatitude','SourceLongitude', 'DestLatitude', 'DestLongitude']    
                return dcc.send_data_frame(df_to_save.to_csv, 'travel_edges_graph.csv', columns=header)
        else:
            pass

    

    ################################################## end graph map callbacks ##############################################

# for develop mode uncomment this lines
if __name__ == '__main__':
    app.run_server(debug=True, port=8060) 

# for develop mode comment this line
# if __name__ == '__main__':
#     app.run_server(debug=False, port=8060) 