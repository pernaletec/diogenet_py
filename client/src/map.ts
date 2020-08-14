/// <reference path="jquery-range.d.ts"/>
/// <reference path="leaflet-html-legend.d.ts"/>
import "bootstrap";
import $ from "jquery";
import "jquery-range";
import "!style-loader!css-loader!jquery-range/jquery.range.css"
import "datatables.net";
import "datatables.net-dt"
import "!style-loader!css-loader!datatables.net-dt/css/jquery.dataTables.min.css"
import * as L from "leaflet";
import "leaflet-html-legend"
import "!style-loader!css-loader!leaflet/dist/leaflet.css"
import "!style-loader!css-loader!leaflet-html-legend/dist/L.Control.HtmlLegend.css"

// const BASE_URL = "http://54.202.119.187:5000"
const BASE_URL = "http://localhost:5000"


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
interface AllMapData {
    min: number,
    max: number,
    data: TravelsMapData[]
}

const MAP_CENTER: L.LatLng = new L.LatLng(35.255, 24.92);
const MAIN_TILE_LAYER = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}";

const VIRIDIS_COLORMAP = [
    { r: 68, g: 1, b: 84 },
    { r: 72, g: 40, b: 120 },
    { r: 62, g: 74, b: 137 },
    { r: 49, g: 104, b: 142 },
    { r: 38, g: 130, b: 142 },
    { r: 31, g: 158, b: 137 },
    { r: 53, g: 183, b: 121 },
    { r: 109, g: 205, b: 89 },
    { r: 180, g: 222, b: 44 },
    { r: 253, g: 231, b: 37 }
];

let localMapInfo: AllMapData;
let markers_list: TravelsMapData[];
let baseMap: L.Map;
let allMarkers: L.CircleMarker[] = [];
let allLines: L.Polyline[] = [];
let dataTableInitialized = false;
let degreelayerGroup = new L.LayerGroup();
let betweenesLayerGroup = new L.LayerGroup();
let closenessLayerGroup = new L.LayerGroup();
let eigenVectorLayerGroup = new L.LayerGroup();
let activeTab = "#map";
let htmlLegend: L.HtmlLegend | undefined = undefined;

function componentToHex(c: number) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
};

function rgbToHex(r: number, g: number, b: number) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
};

function interpolateValue(minVal: number, maxVal: number, value: number): string {
    return (((maxVal - minVal) / 10) * value).toFixed(2);
}

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
        baseMap.removeLayer(degreelayerGroup);
    }
    if (betweenesLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(betweenesLayerGroup);
    }
    if (closenessLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(closenessLayerGroup);
    }
    if (eigenVectorLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(eigenVectorLayerGroup);
    }
}

function updateMapLegend(title: string) {
    if (htmlLegend != undefined) {
        baseMap.removeControl(htmlLegend);
    }
    type LegendHTMLElement = {
        label: string,
        html: string,
        style: { [key: string]: string }
    };
    let legendElements: LegendHTMLElement[] = [];

    for (let i = 0; i < 10; i++) {
        legendElements.push({
            label: interpolateValue(localMapInfo.min, localMapInfo.max, (i + 1)),
            html: '',
            style: {
                'background-color': rgbToHex(VIRIDIS_COLORMAP[i].r, VIRIDIS_COLORMAP[i].g, VIRIDIS_COLORMAP[i].b),
                'width': '15px',
                'height': '10px'
            }
        });
    }
    htmlLegend = L.control.htmllegend({
        position: 'bottomright',
        legends: [{
            name: title,
            elements: legendElements
        }],
        collapseSimple: true,
        detectStretched: false,
        collapsedOnInit: false,
        defaultOpacity: 0.7,
        disableVisibilityControls: true,
    });
    baseMap.addControl(htmlLegend);
}

function updateMap() {
    const currentCentrality = getCentralityIndex();
    const nodeSizes = $(".node-range-slider").val() as string;
    const urlBase = (
        BASE_URL
        + "/map/get/map/"
        + currentCentrality
        + "/"
        + nodeSizes
    );
    clearMap();
    $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (data) => {
            allMarkers = [];
            allLines = [];
            localMapInfo = data;
            markers_list = localMapInfo.data;
            markers_list.forEach((m) => {
                const srcGeoreference = new L.LatLng(m.SourceLatitude, m.SourceLongitude);
                const dstGeoreference = new L.LatLng(m.DestLatitude, m.DestLongitude);
                addCircleMarker(m.Source, m.SourceLatitude, m.SourceLongitude, m.SourceColor, m.SourceSize);
                addCircleMarker(m.Destination, m.DestLatitude, m.DestLongitude, m.DestinationColor, m.DestinationSize);
                drawLine(srcGeoreference, dstGeoreference, m.Philosopher + " traveling from " + m.Source + " to " + m.Destination);
            });
            if (currentCentrality == "Degree") {
                allLines.forEach(line => {
                    degreelayerGroup.addLayer(line);
                });
                allMarkers.forEach(marker => {
                    degreelayerGroup.addLayer(marker);
                });
                degreelayerGroup.addTo(baseMap);
                updateMapLegend("Degree");
            } else if (currentCentrality == "Betweeness") {
                allLines.forEach(line => {
                    betweenesLayerGroup.addLayer(line);
                });
                allMarkers.forEach(marker => {
                    betweenesLayerGroup.addLayer(marker);
                });
                betweenesLayerGroup.addTo(baseMap);
                updateMapLegend("Betweeness");
            } else if (currentCentrality == "Closeness") {
                allLines.forEach(line => {
                    closenessLayerGroup.addLayer(line);
                });
                allMarkers.forEach(marker => {
                    closenessLayerGroup.addLayer(marker);
                });
                closenessLayerGroup.addTo(baseMap);
                updateMapLegend("Closeness");
            } else {
                allLines.forEach(line => {
                    eigenVectorLayerGroup.addLayer(line);
                });
                allMarkers.forEach(marker => {
                    eigenVectorLayerGroup.addLayer(marker);
                });
                eigenVectorLayerGroup.addTo(baseMap);
                updateMapLegend("Eigenvector");
            }
        }
    });
}

function updateMetricsTable() {
    type MeticsTableData = {
        City: string,
        Degree: number,
        Betweenness: number,
        Closeness: number,
        Eigenvector: number
    };
    const currentPhilosopher = "All";
    const urlBase = (
        BASE_URL
        + "/map/get/table/"
        + currentPhilosopher
    );
    $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (data: MeticsTableData[]) => {
            const tableData = data.map(el => [el.City, el.Degree, el.Betweenness, el.Closeness, el.Eigenvector]);
            $("#metrics-table").DataTable({
                data: tableData,
                retrieve: true,
                columns: [
                    { title: "City" },
                    { title: "Degree" },
                    { title: "Betweenness" },
                    { title: "Closeness" },
                    { title: "Eigenvector" },
                ]
            });
        }
    });
    //
}

function updateGraph() {
    const currentCentrality = getCentralityIndex();
    const nodeSizes = $(".node-range-slider").val() as string;
    const labelSizes = $(".label-range-slider").val() as string;
    const urlBase = (
        BASE_URL
        + "/map/get/graph/"
        + currentCentrality
        + "/"
        + nodeSizes
    );
    let graphiFrame = $("#map-graph")[0] as HTMLIFrameElement;
    graphiFrame.src = urlBase;
}

function debounce<Params extends any[]>(
    func: (...args: Params) => any,
    timeout: number,
): (...args: Params) => void {
    let timer: NodeJS.Timeout
    return (...args: Params) => {
        clearTimeout(timer)
        timer = setTimeout(() => {
            func(...args)
        }, timeout)
    }
}

function updateAll() {
    switch (activeTab) {
        case "#map":
            $("#appareance-label").show();
            $("#node-size-div").show();
            $("#label-size-div").hide();
            updateMap();
            break;
        case "#metrics":
            $("#appareance-label").hide();
            $("#node-size-div").hide();
            $("#label-size-div").hide();
            updateMetricsTable();
            break;
        case "#graph":
            $("#appareance-label").show();
            $("#node-size-div").show();
            $("#label-size-div").show();
            updateGraph();
            break;
    }
}

$(() => {
    // Setup multirange slider
    $(".node-range-slider").jRange({
        from: 1,
        to: 10,
        step: 1,
        scale: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        format: '%s',
        width: 200,
        showLabels: true,
        isRange: true,
        snap: true,
        theme: "theme-blue"
    });
    $(".label-range-slider").jRange({
        from: 1,
        to: 10,
        step: 1,
        scale: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        format: '%s',
        width: 200,
        showLabels: true,
        isRange: true,
        snap: true,
        theme: "theme-blue"
    });
    baseMap = L.map("map").setView(MAP_CENTER, 5);
    L.tileLayer(MAIN_TILE_LAYER, {
        maxZoom: 19,
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    }).addTo(baseMap);
    activeTab = "#map";
    updateAll();

    $("#centrality-index").change(
        (event) => {
            updateAll();
        });
    const debouncedUpdateGraph = debounce(updateAll, 4000);
    $(".node-range-slider").change((event) => {
        debouncedUpdateGraph();
    });
    $('a[data-toggle="tab"]').on('shown.bs.tab', (e) => {
        const activedTab = <HTMLAnchorElement>e.target;
        const leavedTab = <HTMLAnchorElement>e.relatedTarget;
        activeTab = activedTab.hash;
        updateAll();
    })
});
