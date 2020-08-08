"""Main flask application entry point."""
from flask import Flask, render_template, make_response, request, send_from_directory
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


@app.route("/map/get/map/<centrality_index>", methods=["GET"])
def get_map_data(centrality_index):
    if request.method != "GET":
        return make_response("Malformed request", 400)
    if centrality_index:
        ng.grafo.current_centrality_index = centrality_index
    data = ng.grafo.get_map_data()
    if data:
        headers = {"Content-Type": "application/json"}
        return make_response(data, 200, headers)
    else:
        return make_response("Error accessing MapGraph Object", 400)


@app.route("/map/get/graph/<centrality_index>")
def get_graph_data(centrality_index):
    if centrality_index:
        ng.grafo.current_centrality_index = centrality_index
    pvis_graph = ng.grafo.get_pyvis()
    if pvis_graph:
        temp_file_name = next(tempfile._get_candidate_names()) + ".html"
        full_filename = os.path.join(app.root_path, "temp", temp_file_name)
        pvis_graph.show(full_filename)
        print(temp_file_name)
        print(app.root_path)
        return send_from_directory("temp", temp_file_name)
    else:
        return make_response("Error accessing MapGraph Object", 400)


@app.route("/horus")
def horus():
    return render_template("horus.html")
