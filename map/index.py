import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app
from app import server
from apps import map_graph

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content-map', children=[])
])

# Update the index
@app.callback(Output('page-content-map', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return map_graph.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)