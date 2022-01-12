from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from apps import global_network_graph, app2

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/apps/global_network_graph"), id="network-graph-link"),
        dbc.NavItem(dbc.NavLink("Page 2", href="/apps/app2"), id="page-2-link")
    ],
    brand="Home",
    brand_href="/",
    color="primary",
    dark=True,
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

main_layout = html.Div([
    navbar,
    html.H3('Home'),
    dcc.Link('Go to Global Network', href='/apps/global_network_graph'),
    dcc.Link('Go to App 2', href='/apps/app2'),
])

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/global_network_graph':
        return global_network_graph.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/':
        return main_layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)