from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/apps/global_network_graph"), id="page-1-link"),
        dbc.NavItem(dbc.NavLink("Page 2", href="/apps/app2"), id="page-2-link")
    ],
    brand="Home",
    brand_href="/",
    color="primary",
    dark=True,
)

layout = html.Div([
    navbar,
    html.H3('App 2'),
    dcc.Dropdown(
        id='app-2-dropdown',
        options=[
            {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-2-display-value'),
    dcc.Link('Go to App 1', href='/apps/global_network_graph'),
    dcc.Link('Go to home', href='/')
])


@app.callback(
    Output('app-2-display-value', 'children'),
    Input('app-2-dropdown', 'value'))
def display_value(value):
    return 'You have selected "{}"'.format(value)