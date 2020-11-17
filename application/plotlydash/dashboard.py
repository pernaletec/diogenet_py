from dash import Dash


def create_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dashapp/",
        external_stylesheets=["/static/css/styles.css"],
    )

    # Create Dash Layout
    dash_app.layout = html.Div(id="dash-container")

    return dash_app.server
