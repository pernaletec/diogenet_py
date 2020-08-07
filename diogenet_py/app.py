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


@app.route("/map/get_travels_graph_data", methods=["GET"])
def get_travels_graph_data():
    if request.method != "GET":
        return make_response("Malformed request", 400)
    data = ng.grafo.get_map_data()
    if data:
        headers = {"Content-Type": "application/json"}
        return make_response(data, 200, headers)
    else:
        return make_response("Error accessing MapGraph Object", 400)


# @app.route("/map/get_travelers_data", methods=["GET"])
# def get_travelers_data():
#     if request.method != "GET":
#         return make_response("Malformed request", 400)
#     philosophers = map.phylosophers_known_origin.to_json()
#     headers = {"Content-Type": "application/json"}
#     return make_response(jsonify(philosophers), 200, headers)


@app.route("/horus")
def horus():
    return render_template("horus.html")
