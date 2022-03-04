import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
#app = dash.Dash(__name__,external_stylesheets= [dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], url_base_pathname = '/diogenet_horus/')
#app.config.suppress_callback_exceptions = True

server = app.server

from apps import global_network_graph, global_network_graph_centrality, local_network_graph, local_network_graph_centrality, communities_graph, communities_treemap

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[])
])

# Update the index
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return global_network_graph.layout
    if pathname == '/apps/global_network_graph':
        return global_network_graph.layout
    if pathname == '/apps/global_network_graph_centrality':
        return global_network_graph_centrality.layout
    if pathname == '/apps/local_network_graph':
        return local_network_graph.layout
    if pathname == '/apps/local_network_graph_centrality':
        return local_network_graph_centrality.layout
    if pathname == '/apps/communities_graph':
        return communities_graph.layout
    if pathname == '/apps/communities_treemap':
        return communities_treemap.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)