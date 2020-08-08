"""Main flask application entry point."""
from flask import Flask, render_template, make_response, request, jsonify
from . import network_graph as ng
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("/map/get/<centrality_index>", methods=["GET"])
def get_travels_graph_data(centrality_index):
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


@app.route("/horus")
def horus():
    return render_template("horus.html")
