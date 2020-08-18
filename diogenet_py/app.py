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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/map/get/map", methods=["GET"])
def get_map_data():
    if request.method != "GET":
        return make_response("Malformed request", 400)

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
        sub_igraph = ng.grafo.create_subgraph()
        subgraph = ng.grafo
        subgraph.igraph_map = sub_igraph
        data = subgraph.get_map_data(min_weight=min_node_size, max_weight=max_node_size)
        all_data = subgraph.get_max_min()
    if data:
        all_data["data"] = data
        headers = {"Content-Type": "application/json"}
        return make_response(jsonify(all_data), 200, headers)
    else:
        return make_response("Error accessing MapGraph Object", 400)


@app.route("/map/get/table/<phylosopher>")
def get_metrics_table(phylosopher="All"):
    data = []
    cities = ng.grafo.get_vertex_names()
    degree = ng.grafo.calculate_degree()
    betweeness = ng.grafo.calculate_betweenness()
    closeness = ng.grafo.calculate_closeness()
    eigenvector = ng.grafo.calculate_eigenvector()

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
    if data:
        headers = {"Content-Type": "application/json"}
        return make_response(jsonify(data), 200, headers)
    else:
        return make_response("Error accessing MapGraph Object", 400)


@app.route("/map/get/graph/<centrality_index>/<min_max>/<filter>")
def get_graph_data(centrality_index, min_max="4,6", filter="All"):
    if centrality_index:
        ng.grafo.current_centrality_index = centrality_index

    min_node_size = int(min_max.split(",")[0])
    max_node_size = int(min_max.split(",")[1])

    if filter == "All":
        pvis_graph = ng.grafo.get_pyvis(
            min_weight=min_node_size, max_weight=max_node_size
        )
    else:
        ng.grafo.set_edges_filter(filter)
        sub_igraph = ng.grafo.create_subgraph()
        subgraph = ng.grafo
        subgraph.igraph_map = sub_igraph
        pvis_graph = subgraph.get_pyvis()
    if pvis_graph:
        temp_file_name = next(tempfile._get_candidate_names()) + ".html"
        full_filename = os.path.join(app.root_path, "temp", temp_file_name)
        pvis_graph.write_html(full_filename)
        return send_from_directory("temp", temp_file_name)
    else:
        return make_response("Error accessing MapGraph Object", 400)


@app.route("/horus")
def horus():
    return render_template("horus.html")
