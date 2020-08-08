import "bootstrap";
import $ from "jquery";
import "!style-loader!css-loader!leaflet/dist/leaflet.css"
import * as L from "leaflet";

interface TravelsMapData {
    Source: string,
    SourceColor: string,
    SourceSize: number,
    Destination: string,
    DestinationColor: string,
    DestinationSize: number,
    Philosopher: string,
    SourceLatitude: number,
    SourceLongitude: number,
    DestLatitude: number,
    DestLongitude: number
}

const MAP_CENTER: L.LatLng = new L.LatLng(35.255, 24.92);
const MAIN_TILE_LAYER = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}";

let markers_list: TravelsMapData[];
let baseMap: L.Map;
let allMarkers: L.CircleMarker[] = [];
let allLines: L.Polyline[] = [];
let degreelayerGroup = new L.LayerGroup();
let betweenesLayerGroup = new L.LayerGroup();
let closenessLayerGroup = new L.LayerGroup();
let eigenVectorLayerGroup = new L.LayerGroup();

function addCircleMarker(popupText: string, latitude: number, longitude: number, mColor?: string, mSize?: number) {
    if (!mColor) {
        mColor = "#959595";
    }
    if (!mSize) {
        mSize = 3;
    }
    const mark = L.circleMarker({ lat: latitude, lng: longitude },
        {
            radius: (mSize + 3),
            opacity: 1,
            color: mColor
        });
    mark.bindPopup(popupText, { closeButton: true });
    allMarkers.push(mark);
}

function drawLine(source: L.LatLng, destination: L.LatLng, popupMsg?: string) {
    const pointList = [source, destination];
    const poliLine = new L.Polyline(pointList, {
        color: "#333333",
        weight: 3,
        opacity: 0.4,
        smoothFactor: 1
    });
    if (popupMsg) {
        poliLine.bindPopup(popupMsg, { closeButton: true });
    }
    allLines.push(poliLine);
}

function getCentralityIndex() {
    const value = $("#centrality-index").val();
    let centralityIndex = "";
    if (value == 1) {
        centralityIndex = "Degree";
    } else if (value == 2) {
        centralityIndex = "Betweeness";
    } else if (value == 3) {
        centralityIndex = "Closeness";
    } else {
        centralityIndex = "Eigenvector";
    }
    return centralityIndex;
}

function clearMap() {
    if (degreelayerGroup.getLayers().length > 0) {
        console.log('Clearing degree');
        baseMap.removeLayer(degreelayerGroup);
    }
    if (betweenesLayerGroup.getLayers().length > 0) {
        console.log('Clearing betweeness');
        baseMap.removeLayer(betweenesLayerGroup);
    }
    if (closenessLayerGroup.getLayers().length > 0) {
        console.log('Clearing closeness');
        baseMap.removeLayer(closenessLayerGroup);
    }
    if (eigenVectorLayerGroup.getLayers().length > 0) {
        console.log('Clearing eigenvector');
        baseMap.removeLayer(eigenVectorLayerGroup);
    }
}

function updateMap() {
    const currentCentrality = getCentralityIndex();
    const urlBase = "http://localhost:5000/map/get/map/" + currentCentrality;
    clearMap();
    $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (data) => {
            allMarkers = [];
            allLines = [];
            markers_list = data;
            markers_list.forEach((m) => {
                const srcGeoreference = new L.LatLng(m.SourceLatitude, m.SourceLongitude);
                const dstGeoreference = new L.LatLng(m.DestLatitude, m.DestLongitude);
                addCircleMarker(m.Source, m.SourceLatitude, m.SourceLongitude, m.SourceColor, m.SourceSize);
                addCircleMarker(m.Destination, m.DestLatitude, m.DestLongitude, m.DestinationColor, m.DestinationSize);
                drawLine(srcGeoreference, dstGeoreference, m.Philosopher + " traveling from " + m.Source + " to " + m.Destination);
            });
            if (currentCentrality == "Degree") {
                if (degreelayerGroup.getLayers().length < 1) {
                    allLines.forEach(line => {
                        degreelayerGroup.addLayer(line);
                    });
                    allMarkers.forEach(marker => {
                        degreelayerGroup.addLayer(marker);
                    });
                }
                degreelayerGroup.addTo(baseMap);
            } else if (currentCentrality == "Betweeness") {
                if (betweenesLayerGroup.getLayers().length < 1) {
                    allLines.forEach(line => {
                        betweenesLayerGroup.addLayer(line);
                    });
                    allMarkers.forEach(marker => {
                        betweenesLayerGroup.addLayer(marker);
                    });
                }
                betweenesLayerGroup.addTo(baseMap);
            } else if (currentCentrality == "Closeness") {
                if (closenessLayerGroup.getLayers().length < 1) {
                    allLines.forEach(line => {
                        closenessLayerGroup.addLayer(line);
                    });
                    allMarkers.forEach(marker => {
                        closenessLayerGroup.addLayer(marker);
                    });
                }
                closenessLayerGroup.addTo(baseMap);
            } else {
                if (eigenVectorLayerGroup.getLayers().length < 1) {
                    allLines.forEach(line => {
                        eigenVectorLayerGroup.addLayer(line);
                    });
                    allMarkers.forEach(marker => {
                        eigenVectorLayerGroup.addLayer(marker);
                    });
                }
                eigenVectorLayerGroup.addTo(baseMap);
            }
        }
    });
}

$(() => {
    baseMap = L.map("map").setView(MAP_CENTER, 5);
    L.tileLayer(MAIN_TILE_LAYER, {
        maxZoom: 19,
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    }).addTo(baseMap);
    updateMap();
    $("#centrality-index").change(
        (event) => {
            updateMap();
            // Put updateGraph();
        });
});
