"""Main flask application entry point."""
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map():
    return render_template("map.html")


@app.route("map/get_graph")
def get_graph():

    return


@app.route("/horus")
def horus():
    return render_template("horus.html")
