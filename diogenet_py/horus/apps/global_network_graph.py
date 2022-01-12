from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

STYLE_A_ITEM = {
    'color':'#ffffff',
    'textDecoration': 'none'
}

navbar = dbc.Navbar(
    children=[
        dbc.NavLink("Horus Main", href="/", style=STYLE_A_ITEM),
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Graph", href="#"), dbc.DropdownMenuItem("Graph + centrality", href="/apps/app2")],
            label="Local Network",
            style=STYLE_A_ITEM,
            color="#1a6ecc"
        ),
    ],
    color="#1a6ecc",
    style={'color':'#ffffff'},
    id='Navbar'
)

sidebar_content = [
    html.H5('Dataset Selection', className="mt-3 mb-3"),
    dbc.InputGroup(
            [
                dbc.Select(
                    options=[
                        {"label": "Option 1", "value": 1},
                        {"label": "Option 2", "value": 2},
                    ],
                    placeholder='Select a dataset'
                ),
            ]
     ),
    html.H5('Network Ties', className="mt-5 mb-3"),
    dcc.Checklist(
    options=[
        {'label': ' Is teacher of', 'value': 1},
            {'label': ' Is friend of', 'value': 2},
            {'label': ' Is family of', 'value': 3},
            {'label': ' Studied the work of', 'value': 4},
            {'label': ' sent letters to', 'value': 5},
            {'label': ' Is benefactor of', 'value': 6},
    ],
    value=[1],
    labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
    inputStyle={'margin':'0px 5px'},
    ),
    html.H5('Graph Layout',className="mt-5 mb-3"),
    dbc.InputGroup(
            [
                dbc.Select(
                    options=[
                        {"label": "Option 1", "value": 1},
                        {"label": "Option 2", "value": 2},
                    ],
                    placeholder='Select a layout'
                ),
            ]
     ),
    dcc.Checklist(
        options=[
            {'label': ' Gender and Gods', 'value': "true"},
        ],
        labelStyle={'display': 'flex', 'flexDirection':'row','alingItem':'center'},
        inputStyle={'margin':'0px 5px'},
        className='mt-3'
    ),
    html.H5('Appearence',className="mt-5 mb-3"),
    html.H6('Label Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
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
        value=[3, 6]
    ),
    html.H6('Node Size',className="mt-1 mb-2"),
    dcc.RangeSlider(
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
        value=[3, 6]
    )
]

row = html.Div(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(html.Div(sidebar_content), id='sidebar', width=3, style={"backgroundColor": "#2780e31a", "padding":'30px 10px 10px 10px'}),
                dbc.Col(html.Div([]), className='bg-warning', id='main-netowrk-graph'),
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
    Output('app-1-display-value', 'children'),
    Input('app-1-dropdown', 'value'))
def display_value(value):
    return 'You have selected "{}"'.format(value)