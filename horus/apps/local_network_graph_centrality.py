import dash
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


from index import app
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
    id='navbar_local_centrality'
)

sidebar_content = [
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

tabs = dcc.Tabs(
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

row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar_local_centrality', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div(children=[tabs, html.Div(id="content_local_centrality", style={'height': '100vh'}, children=[])]), id='main_local_centrality'),
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
    Output('dropdown_container_local_centrality', 'children'),
    Input('dataset_selection_local_centrality', 'value'),
    Input('graph_filter_local_centrality', 'value'))
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
                full_filename = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets',temp_file_name))
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
def update_table(
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
def display_confirm(graph_filter_global):
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
def func(n_clicks, dataset_selection, graph_filter):
    if dash.callback_context.triggered[0]['prop_id'] == 'btn_csv_local_centrality.n_clicks':
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