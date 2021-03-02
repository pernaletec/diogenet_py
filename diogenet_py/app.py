"""Main flask application entry point."""
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    send_from_directory,
    send_file,
    jsonify,
)
from igraph import *
from igraph import layout
from traitlets.traitlets import Undefined
from .network_graph import (
    global_graph,
    map_graph,
    local_graph,
    communities_graph,
    map_graph_change_dataset,
)

import os
import tempfile
import random
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import igraph

app = Flask(__name__)

app_global_graph = global_graph


def setup_app(app):
    # All your initialization code
    random.seed(1234)


setup_app(app)

MALFORMED_REQUEST = "Malformed request"
MAP_GRAPH_ERROR = "Error accessing MapGraph Object"
HTML_PLOT_CONTENT = """<!DOCTYPE html>
<html>
    <head>
        <title>Communities iGraph Plot</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous"></script>
    </head>
<body>
    <div class="row justify-content-center">
        <div class="col-11">
            {file}
        </div>
    </div>
</body>
</html> 
"""
JSON_HEADER = {"Content-Type": "application/json"}
HTML_SUFFIX = ".html"
DEFAULT_FILTER_VALUE = "is teacher of"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/map/get/map", methods=["GET"])
def get_map_data():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    centrality_index = str(request.args.get("centrality"))
    min_max = str(request.args.get("min_max"))
    map_filter = str(request.args.get("filter"))
    grafo = map_graph

    if centrality_index:
        grafo.current_centrality_index = centrality_index
    if not min_max:
        min_max = "4,6"
    if not map_filter:
        map_filter = "All"

    min_node_size = int(min_max.split(",")[0])
    max_node_size = int(min_max.split(",")[1])

    all_data = {}
    data = None
    if map_filter != "All":
        filters = map_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)
    else:
        grafo.edges_filter = []
    grafo.create_subgraph()
    data = grafo.get_map_data(min_weight=min_node_size, max_weight=max_node_size)
    all_data = grafo.get_max_min()

    if data:
        all_data["data"] = data
        headers = JSON_HEADER
        return make_response(jsonify(all_data), 200, headers)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


def get_map_data_table(filter_string):
    graph = None
    graph = map_graph
    if filter_string != "All":
        filters = filter_string.split(";")
        for m_filter in filters:
            graph.set_edges_filter(m_filter)
        graph.create_subgraph()
        # graph = subgraph
    return (
        graph.get_vertex_names(),
        graph.calculate_degree(),
        graph.calculate_betweenness(),
        graph.calculate_closeness(),
        graph.calculate_eigenvector(),
    )


def get_global_data_table(filter_string):

    if global_graph:
        # graph = None
        # graph = global_graph
        # print('graph')
        # print(graph)
        # subgraph = None

        filters = filter_string.split(";")
        # print(filters)
        global_graph.edges_filter = []
        for m_filter in filters:
            global_graph.set_edges_filter(m_filter)
        # print("graph.current_edges")
        # print(graph.current_edges)
        global_graph.create_subgraph()
        # subgraph = graph.get_subgraph()
        # print('subgraph')
        # print(subgraph)
        # graph = global_graph
        # global_graph.get_vertex_names()

        return (
            global_graph,
            global_graph.get_vertex_names(),
            global_graph.calculate_degree(),
            global_graph.calculate_betweenness(),
            global_graph.calculate_closeness(),
            global_graph.calculate_eigenvector(),
        )


def get_local_data_table(filter_string, ego_value, order_value):

    if local_graph:
        # subgraph = None

        if ego_value not in [None, "None"]:
            local_graph.local_phylosopher = ego_value
        else:
            local_graph.local_phylosopher = "Plato"

        if order_value not in [None, "None"]:
            local_graph.local_order = int(order_value)
        else:
            local_graph.local_order = 1

        filters = filter_string.split(";")
        local_graph.edges_filter = []
        for m_filter in filters:
            local_graph.set_edges_filter(m_filter)

        local_graph.create_subgraph()
        # graph = graph.get_localgraph()
        # subgraph = graph.get_subgraph()
        # graph = local_graph

    return (
        local_graph,
        local_graph.get_vertex_names(),
        local_graph.calculate_degree(),
        local_graph.calculate_betweenness(),
        local_graph.calculate_closeness(),
        local_graph.calculate_eigenvector(),
    )


@app.route("/map/get/table")
def get_metrics_table():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    map_filter = str(request.args.get("filter"))
    graph_type = str(request.args.get("type"))
    ego_value = str(request.args.get("ego"))
    order_value = str(request.args.get("order"))

    if graph_type in [None, "None"]:
        graph_type = "map"
    if map_filter in [None, "None"]:
        map_filter = "All"

    data = []
    grafo = None
    cities = degree = betweeness = closeness = eigenvector = []

    if graph_type == "map":
        (cities, degree, betweeness, closeness, eigenvector,) = get_map_data_table(
            map_filter
        )
        grafo = map_graph
    elif graph_type == "global":
        (
            grafo,
            cities,
            degree,
            betweeness,
            closeness,
            eigenvector,
        ) = get_global_data_table(map_filter)
    else:
        (
            grafo,
            cities,
            degree,
            betweeness,
            closeness,
            eigenvector,
        ) = get_local_data_table(map_filter, ego_value, order_value)

    for (
        city_name,
        city_degree,
        city_betweeness,
        city_closeness,
        city_eigenvector,
    ) in zip(cities, degree, betweeness, closeness, eigenvector):
        record = {
            "City": city_name,
            "Degree": city_degree,
            "Betweenness": city_betweeness,
            "Closeness": city_closeness,
            "Eigenvector": city_eigenvector,
        }
        data.append(record)

    data_table = {}
    data_table["CentralizationDegree"] = grafo.centralization_degree()
    data_table["CentralizationBetweenness"] = grafo.centralization_betweenness()
    data_table["CentralizationCloseness"] = grafo.centralization_closeness()
    data_table["CentralizationEigenvector"] = grafo.centralization_eigenvector()
    data_table["CityData"] = data

    if data:
        headers = JSON_HEADER
        return make_response(jsonify(data_table), 200, headers)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/map/get/graph")
def get_graph_data():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    centrality_index = str(request.args.get("centrality"))
    node_min_max = str(request.args.get("node_min_max"))
    label_min_max = str(request.args.get("label_min_max"))
    map_filter = str(request.args.get("filter"))
    graph_layout = str(request.args.get("layout"))

    # selected_edges = str(request.args.get("edges"))

    grafo = map_graph

    if centrality_index:
        grafo.current_centrality_index = centrality_index
    if not node_min_max:
        node_min_max = "4,6"
    if not label_min_max:
        label_min_max = "4,6"
    if not map_filter:
        map_filter = "All"
    if not graph_layout:
        # "fr", "kk", "circle", "sphere" or "grid_fr"
        graph_layout = "fr"

    node_min_size = int(node_min_max.split(",")[0])
    node_max_size = int(node_min_max.split(",")[1])
    label_min_size = int(label_min_max.split(",")[0])
    label_max_size = int(label_min_max.split(",")[1])

    if map_filter == "All":
        pvis_graph = grafo.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
        )
    else:
        filters = map_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)
        grafo.create_subgraph()
        # subgraph = grafo.get_subgraph()
        pvis_graph = grafo.get_pyvis()
    if pvis_graph:
        temp_file_name = next(tempfile._get_candidate_names()) + HTML_SUFFIX
        full_filename = os.path.join(app.root_path, "temp", temp_file_name)
        pvis_graph.write_html(full_filename)
        return send_from_directory("temp", temp_file_name)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/horus")
def horus():
    return render_template("horus.html")


@app.route("/horus/get/graph")
def horus_get_graph():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    pvis_graph = None
    centrality_index = str(request.args.get("centrality"))
    node_min_max = str(request.args.get("node_min_max"))
    label_min_max = str(request.args.get("label_min_max"))
    graph_filter = str(request.args.get("filter"))
    graph_layout = str(request.args.get("layout"))
    graph_type = str(request.args.get("graph_type"))
    ego_value = str(request.args.get("ego"))
    order_value = str(request.args.get("order"))
    algorithm_value = str(request.args.get("algorithm"))
    plot_type = str(request.args.get("plot"))
    differentiate_gender = str(request.args.get("diffGodGender"))
    show_crossing_ties = str(request.args.get("showCrossingTies"))

    if not plot_type or plot_type == "" or plot_type == "None":
        plot_type = "pyvis"

    if graph_type == "local":
        grafo = local_graph

        if ego_value not in [Undefined, None, "undefined", ""]:
            grafo.local_phylosopher = ego_value
        else:
            grafo.local_phylosopher = "Plato"

        if order_value not in [Undefined, None, "undefined", ""]:
            grafo.local_order = int(order_value)
        else:
            grafo.local_order = 1

    elif graph_type == "community":
        grafo = communities_graph
        if algorithm_value == "" or algorithm_value == "None":
            algorithm_value = "community_infomap"
        grafo.comm_alg = algorithm_value
        grafo.identify_communities()
        if show_crossing_ties in ["True", "true"]:
            grafo.pyvis_show_crossing_ties = True
        else:
            grafo.pyvis_show_crossing_ties = False
    else:
        grafo = global_graph

    not_centrality = False

    if centrality_index:
        if centrality_index == "None":
            grafo.current_centrality_index = "Degree"
            not_centrality = True
        else:
            grafo.current_centrality_index = centrality_index

    if not node_min_max:
        node_min_max = "4,6"

    if not label_min_max:
        label_min_max = "4,6"

    if not graph_filter:
        graph_filter = DEFAULT_FILTER_VALUE
        grafo.set_edges_filter(graph_filter)
    else:
        grafo.edges_filter = []
        filters = graph_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)

    if not graph_layout:
        graph_layout = "fr"

    node_min_size = int(node_min_max.split(",")[0])
    node_max_size = int(node_min_max.split(",")[1])
    label_min_size = int(label_min_max.split(",")[0])
    label_max_size = int(label_min_max.split(",")[1])

    #    if graph_type == "local":
    #        grafo.create_local_graph()
    #        grafo = grafo.get_localgraph()

    if differentiate_gender in ["True", "true"]:
        grafo.pyvis_show_gender = True
    else:
        grafo.pyvis_show_gender = False

    grafo.create_subgraph()
    # subgraph = grafo

    pvis_graph = None
    if plot_type == "pyvis":
        pvis_graph = grafo.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
            avoid_centrality=not_centrality,
        )
    full_filename = ""
    if pvis_graph or plot_type == "igraph":
        suffix = ".svg" if plot_type == "igraph" else HTML_SUFFIX
        temp_file_name = next(tempfile._get_candidate_names()) + suffix
        full_filename = os.path.join(app.root_path, "temp", temp_file_name)
        if plot_type == "igraph":
            modularity, clusters = grafo.identify_communities()
            dendogram_communities_list = [
                "community_edge_betweenness",
                "community_walktrap",
                "community_fastgreedy",
            ]
            grafo.igraph_subgraph.vs["label"] = grafo.igraph_subgraph.vs["name"]
            if grafo.comm_alg not in dendogram_communities_list:
                plot(
                    grafo.comm,
                    full_filename,
                    layout=grafo.graph_layout,
                    bbox=(450, 450),
                    margin=20,
                    mark_groups=True,
                    vertex_label_size=7,
                    vertex_label_angle=200,
                    vertex_label_dist=1,
                    vertex_size=8,
                )
            else:
                full_filename = os.path.join(app.root_path, "not_available.svg")
            with open(full_filename, "r") as file:
                if grafo.comm_alg not in dendogram_communities_list:
                    data = file.read().replace('width="450pt"', 'width="100%"')
                else:
                    data = file.read()
                full_html_file_content = HTML_PLOT_CONTENT.format(file=data)
                temp_html_file_name = (
                    next(tempfile._get_candidate_names()) + HTML_SUFFIX
                )
                full_html_filename = os.path.join(
                    app.root_path, "temp", temp_html_file_name
                )
                full_html_file = open(full_html_filename, "w")
                _ = full_html_file.write(full_html_file_content)
                full_html_file.close()
                full_filename = full_html_filename

        else:
            pvis_graph.write_html(full_filename)
        print(full_filename)
        return send_file(full_filename)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/horus/get/ego")
def horus_get_filosophers():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    graph_filter = str(request.args.get("filter"))

    grafo = global_graph

    if not graph_filter:
        graph_filter = DEFAULT_FILTER_VALUE
        grafo.set_edges_filter(graph_filter)
    else:
        grafo.edges_filter = []
        filters = graph_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)

    data = []
    grafo.create_subgraph()

    for philosopher in grafo.igraph_subgraph.vs:
        data.append({"name": philosopher["name"]})

    sorted_data = sorted(data, key=lambda k: k["name"])
    if data:
        headers = JSON_HEADER
        return make_response(jsonify(sorted_data), 200, headers)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/horus/get/heatmap")
def horus_get_heatmap():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    plotly_graph = None
    graph_filter = str(request.args.get("filter"))
    graph_type = str(request.args.get("graph_type"))
    ego_value = str(request.args.get("ego"))
    order_value = str(request.args.get("order"))

    grafo = global_graph

    if not graph_filter:
        graph_filter = DEFAULT_FILTER_VALUE
        grafo.set_edges_filter(graph_filter)
    else:
        grafo.edges_filter = []
        filters = graph_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)

    if graph_type == "local":
        # grafo = local_graph
        grafo.local_phylosopher = ego_value if ego_value else "Plato"
        grafo.local_order = int(order_value) if order_value else 1
        grafo.create_local_graph()
    # else:
    #    grafo = global_graph

    # if graph_type == "local":
    #     grafo = local_graph
    #     grafo.local_phylosopher = ego_value if ego_value else "Plato"
    #     if order_value and order_value != "None":
    #         grafo.local_order = int(order_value)
    #     else:
    #         grafo.local_order = 4
    # else:
    #     grafo = global_graph

    # if graph_type == "local":
    #    grafo.create_local_graph()
    # grafo = grafo.get_localgraph()
    # subgraph = grafo.get_subgraph()
    subgraph = grafo

    data = {
        "Philosopher": subgraph.igraph_subgraph.vs["name"],
        "Degree": subgraph.calculate_degree(),
        "Betweeness": subgraph.calculate_betweenness(),
        "Closeness": subgraph.calculate_closeness(),
        "Eigenvector": subgraph.calculate_eigenvector(),
    }

    interpolated_data = {
        "Philosopher": data["Philosopher"],
        "Degree": np.interp(
            data["Degree"], (min(data["Degree"]), max(data["Degree"])), (0, +1)
        ),
        "Betweeness": np.interp(
            data["Betweeness"],
            (min(data["Betweeness"]), max(data["Betweeness"])),
            (0, +1),
        ),
        "Closeness": np.interp(
            data["Closeness"],
            (min(data["Closeness"]), max(data["Closeness"])),
            (0, +1),
        ),
        "Eigenvector": np.interp(
            data["Eigenvector"],
            (min(data["Eigenvector"]), max(data["Eigenvector"])),
            (0, +1),
        ),
    }

    # Interpolate all values to betweetn 0 -  1

    df = pd.DataFrame(data=interpolated_data)
    df1 = df.sort_values(by=["Degree", "Betweeness", "Closeness"]).set_index(
        "Philosopher", drop=False
    )

    # heatmap = go.Figure(
    #     data=go.Heatmap(
    #         z=[df.Degree, df.Betweeness, df.Closeness, df.Eigenvector],
    #         y=df.Philosopher,
    #         x=["Degree", "Betweeness", "Closeness", "Eigenvector"],
    #         hoverongaps=False,
    #     )
    # )
    plotly_graph = go.Figure(
        data=go.Heatmap(
            z=df1[["Degree", "Betweeness", "Closeness", "Eigenvector"]],
            y=df1.Philosopher,
            x=["Degree", "Betweeness", "Closeness", "Eigenvector"],
            hoverongaps=False,
            type="heatmap",
            colorscale="Viridis",
        )
    )

    plotly_graph.update_layout(
        legend_font_size=12, legend_title_font_size=12, font_size=8
    )

    temp_file_name = next(tempfile._get_candidate_names()) + HTML_SUFFIX
    full_filename = os.path.join(app.root_path, "temp", temp_file_name)
    plotly_graph.write_html(full_filename)
    print("Sending " + full_filename + " file")
    return send_from_directory("temp", temp_file_name)


@app.route("/horus/get/treemap")
def horus_get_treemap():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    centrality_index = "communities"
    graph_filter = str(request.args.get("filter"))
    graph_type = "community"
    algorithm_value = str(request.args.get("algorithm"))

    grafo = communities_graph
    algorithm_value = (
        algorithm_value
        if (algorithm_value and algorithm_value != "")
        else "community_edge_betweenness"
    )
    grafo.comm_alg = algorithm_value

    if not graph_filter:
        graph_filter = DEFAULT_FILTER_VALUE
        grafo.set_edges_filter(graph_filter)
    else:
        grafo.edges_filter = []
        filters = graph_filter.split(";")
        for m_filter in filters:
            grafo.set_edges_filter(m_filter)

    # subgraph = grafo.get_subgraph()
    grafo.create_subgraph()
    subgraph = grafo

    modularity, clusters_dict = subgraph.identify_communities()

    communities_index = []

    for i in range(len(subgraph.igraph_subgraph.vs)):
        if subgraph.igraph_subgraph.vs[i]["name"] in clusters_dict.keys():
            communities_index.append(
                clusters_dict[subgraph.igraph_subgraph.vs[i]["name"]]
            )

    data = {
        "Philosopher": subgraph.igraph_subgraph.vs["name"],
        "Degree": subgraph.calculate_degree(),
        "Community": communities_index,
    }

    df = pd.DataFrame(data=data)
    df1 = df.sort_values(by=["Community", "Degree"]).set_index(
        "Philosopher", drop=False
    )

    # plotly_graph = go.Figure(
    #     data=go.Heatmap(
    #         z=df1[["Degree", "Betweeness", "Closeness", "Eigenvector"]],
    #         y=df1.Philosopher,
    #         x=["Degree", "Betweeness", "Closeness", "Eigenvector"],
    #         hoverongaps=False,
    #         type="heatmap",
    #         colorscale="Viridis",
    #     )
    # )

    plotly_graph = px.treemap(df1, path=["Community", "Philosopher"], values="Degree",)

    plotly_graph.update_layout(
        legend_font_size=12, legend_title_font_size=12, font_size=8
    )

    temp_file_name = next(tempfile._get_candidate_names()) + HTML_SUFFIX
    full_filename = os.path.join(app.root_path, "temp", temp_file_name)
    plotly_graph.write_html(full_filename)
    print("Sending " + full_filename + " file")
    return send_from_directory("temp", temp_file_name)


@app.route("/map/set/dataset")
def horus_set_dataset():
    global map_graph
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    dataset = str(request.args.get("dataset"))

    if not dataset or dataset != "iamblichus":
        map_graph = map_graph_change_dataset("diogenes_laertius")
    else:
        map_graph = map_graph_change_dataset("iamblichus")

    return make_response(jsonify({"success": True}), 200, JSON_HEADER)

