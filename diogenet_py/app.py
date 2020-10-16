"""Main flask application entry point."""
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    send_from_directory,
    jsonify,
)
from . import network_graph as ng
import os
import tempfile

app = Flask(__name__)

MALFORMED_REQUEST = "Malformed request"
MAP_GRAPH_ERROR = "Error accessing MapGraph Object"


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

    if centrality_index:
        ng.grafo.current_centrality_index = centrality_index
    if not min_max:
        min_max = "4,6"
    if not map_filter:
        map_filter = "All"

    min_node_size = int(min_max.split(",")[0])
    max_node_size = int(min_max.split(",")[1])

    all_data = {}
    data = None
    if map_filter == "All":
        data = ng.grafo.get_map_data(min_weight=min_node_size, max_weight=max_node_size)
        all_data = ng.grafo.get_max_min()
    else:
        filters = map_filter.split(";")
        for m_filter in filters:
            ng.grafo.set_edges_filter(m_filter)
        subgraph = ng.grafo.get_subgraph()
        data = subgraph.get_map_data(min_weight=min_node_size, max_weight=max_node_size)
        all_data = subgraph.get_max_min()
    if data:
        all_data["data"] = data
        headers = {"Content-Type": "application/json"}
        return make_response(jsonify(all_data), 200, headers)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/map/get/table")
def get_metrics_table():
    if request.method != "GET":
        return make_response(MALFORMED_REQUEST, 400)

    map_filter = str(request.args.get("filter"))
    print(map_filter)

    if not map_filter:
        map_filter = "All"

    data = []

    print(map_filter)
    if map_filter == "All":
        cities = ng.grafo.get_vertex_names()
        degree = ng.grafo.calculate_degree()
        betweeness = ng.grafo.calculate_betweenness()
        closeness = ng.grafo.calculate_closeness()
        eigenvector = ng.grafo.calculate_eigenvector()
    else:
        filters = map_filter.split(";")
        for m_filter in filters:
            ng.grafo.set_edges_filter(m_filter)
        print(m_filter)
        subgraph = ng.grafo.get_subgraph()

        cities = subgraph.get_vertex_names()
        print(len(cities))
        degree = subgraph.calculate_degree()
        print(len(degree))
        betweeness = subgraph.calculate_betweenness()
        print(len(betweeness))
        closeness = subgraph.calculate_closeness()
        print(len(closeness))
        eigenvector = subgraph.calculate_eigenvector()
        print(len(eigenvector))

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
    data_table["CentralizationDegree"] = ng.grafo.centralization_degree()
    data_table["CentralizationBetweenness"] = ng.grafo.centralization_betweenness()
    data_table["CentralizationCloseness"] = ng.grafo.centralization_closeness()
    data_table["CentralizationEigenvector"] = ng.grafo.centralization_eigenvector()
    data_table["CityData"] = data

    if data:
        headers = {"Content-Type": "application/json"}
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
    selected_edges = str(request.args.get("edges"))

    if centrality_index:
        ng.grafo.current_centrality_index = centrality_index
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
        pvis_graph = ng.grafo.get_pyvis(
            min_weight=node_min_size,
            max_weight=node_max_size,
            min_label_size=label_min_size,
            max_label_size=label_max_size,
            layout=graph_layout,
        )
    else:
        filters = map_filter.split(";")
        for m_filter in filters:
            ng.grafo.set_edges_filter(m_filter)
        subgraph = ng.grafo.get_subgraph()
        pvis_graph = subgraph.get_pyvis()
    if pvis_graph:
        temp_file_name = next(tempfile._get_candidate_names()) + ".html"
        full_filename = os.path.join(app.root_path, "temp", temp_file_name)
        pvis_graph.write_html(full_filename)
        return send_from_directory("temp", temp_file_name)
    else:
        return make_response(MAP_GRAPH_ERROR, 400)


@app.route("/horus")
def horus():
    return render_template("horus.html")
