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
    map = []
    map_dict_strings = [
        "Source",
        "Destination",
        "Philosopher",
        "SourceLatitude",
        "SourceLongitude",
        "DestLatitude",
        "DestLongitude",
    ]
    if ng.grafo.travels_graph_data:
        for record in ng.grafo.travels_graph_data:
            index = 0
            map_record = {}
            for item in record:
                tmp_value = item
                if isinstance(item, list):
                    if len(item) == 1:
                        tmp_value = item[0]
                map_record[map_dict_strings[index]] = tmp_value
                index = index + 1
            map.append(map_record)
    headers = {"Content-Type": "application/json"}
    if map:
        return make_response(jsonify(map), 200, headers)
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
