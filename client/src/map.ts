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
let degreelayerGroup = new L.LayerGroup();
let betweenesLayerGroup = new L.LayerGroup();
let closenessLayerGroup = new L.LayerGroup();
let eigenVectorLayerGroup = new L.LayerGroup();
let activeTab = "#map";
let htmlLegend: L.HtmlLegend | undefined = undefined;
let travelersListOptions: string[] = [];
let table1: any;


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

function addCircleMarker(popupText: string, latitude: number, longitude: number, mColor?: string, mSize?: number): L.CircleMarker {
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
            color: mColor,
        });
    mark.bindPopup(popupText, { closeButton: true });
    return mark;
}

function drawLine(source: L.LatLng, destination: L.LatLng, popupMsg?: string): L.Polyline {
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
    return poliLine;
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

function getFilter() {
    const travelersFilter = <HTMLSelectElement>document.getElementById("travelers_filter");
    let values = "";
    if (travelersFilter !== null) {
        const trLen = travelersFilter.options.length;
        for (let i = 0; i < trLen; i++) {
            values += travelersFilter.options[i].value;
            if (i !== (trLen - 1)) {
                values += ";";
            }
        }
    }
    return values;
}

function addFilterOptions() {
    const travelSelect = document.getElementById('traveler');
    if (travelSelect !== null) {
        travelSelect.innerHTML = "";
    }
    const tempTravelers = travelersListOptions.filter((v, i, a) => a.indexOf(v) === i);
    travelersListOptions = tempTravelers;
    travelersListOptions.sort((a, b) => {
        if (a > b) return 1;
        if (a < b) return -1;
        return 0
    });
    travelersListOptions.forEach(option => {
        $("#traveler").append(new Option(option, option));
    });
}

function addFilter() {
    const travelersFilter: HTMLSelectElement = <HTMLSelectElement>document.getElementById("travelers_filter");
    const filterValue = <string>$("#traveler").val();
    if (travelersFilter !== null) {
        const trLen = travelersFilter.options.length;
        let addFilter2Control = true;
        for (let i = 0; i < trLen; i++) {
            if (travelersFilter.options[i].value === filterValue) {
                addFilter2Control = false;
            }
        }
        if (addFilter2Control) {
            $("#travelers_filter").append(new Option(filterValue, filterValue));
        }
    }
}

function clearFilters() {
    const travelersFilter: HTMLSelectElement = <HTMLSelectElement>document.getElementById("travelers_filter");
    travelersFilter.innerHTML = "";
    updateAll();
}

function highlightFeature(e: any, color?: string) {
    var layer = e.target as L.GeoJSON;
    layer.setStyle({
        weight: 8,
        dashArray: '',
        fillOpacity: 1
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

function resetHighlight(e: any) {
    var layer = e.target as L.GeoJSON;
    layer.setStyle({
        weight: 3,
        dashArray: '',
        opacity: 0.5,
    });
}

function zoomToFeature(e: any) {
    baseMap.fitBounds(e.target.getBounds());
    e.target.bringToFront();
}

function onEachFeatureFn(feature: any, layer: L.GeoJSON): any {
    layer.on({
        click: zoomToFeature
    });
    if (feature.geometry.type == "LineString") {
        let strPopUp = (
            feature.properties.name
            + " travels from "
            + feature.properties.travelsFrom
            + " to "
            + feature.properties.travelsTo
        )
        layer.bindPopup(strPopUp)
            .setStyle({
                weight: 3,
                dashArray: '',
                opacity: 0.5,
                color: "#333"
            });
    } else {
        layer.bindTooltip(feature.properties.name);
        layer.bindPopup(feature.properties.name);
    };
}


function clearMap() {
    if (degreelayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(degreelayerGroup);
        degreelayerGroup = new L.LayerGroup();
    }
    if (betweenesLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(betweenesLayerGroup);
        betweenesLayerGroup = new L.LayerGroup();
    }
    if (closenessLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(closenessLayerGroup);
        closenessLayerGroup = new L.LayerGroup();
    }
    if (eigenVectorLayerGroup.getLayers().length > 0) {
        baseMap.removeLayer(eigenVectorLayerGroup);
        eigenVectorLayerGroup = new L.LayerGroup();
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
    let currentFilter = getFilter();
    if (currentFilter === "") {
        currentFilter = "All";
    }
    const urlBase = encodeURI(
        BASE_URL
        + "/map/get/map?centrality="
        + currentCentrality
        + "&min_max="
        + nodeSizes
        + "&filter="
        + currentFilter
    );
    clearMap();
    $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (data) => {
            travelersListOptions = [];
            localMapInfo = data;
            markers_list = localMapInfo.data;
            markers_list.forEach((m) => {
                const metaGeoJSON = JSON.stringify({
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates":
                                    [
                                        [m.SourceLongitude, m.SourceLatitude],
                                        [m.DestLongitude, m.DestLatitude]
                                    ]
                            },
                            "properties": {
                                "type": "edge",
                                "name": m.Philosopher,
                                "travelsFrom": m.Source,
                                "travelsTo": m.Destination,
                                "sourceColor": m.SourceColor,
                                "destinationColor": m.DestinationColor,
                            }
                        },
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [m.SourceLongitude, m.SourceLatitude]
                            },
                            "properties": {
                                "type": "source",
                                "name": m.Source,
                                "color": m.SourceColor,
                                "size": m.SourceSize
                            }
                        },
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [m.DestLongitude, m.DestLatitude]
                            },
                            "properties": {
                                "type": "destination",
                                "name": m.Destination,
                                "color": m.DestinationColor,
                                "size": m.DestinationSize
                            }
                        },
                    ],
                });
                const geoJson = new L.GeoJSON(JSON.parse(metaGeoJSON), {
                    pointToLayer: (feature: any, latlng: L.LatLng) => {
                        let marker: L.CircleMarker;
                        if (feature.properties.type == "source") {
                            marker = addCircleMarker(
                                m.Source,
                                m.SourceLatitude,
                                m.SourceLongitude,
                                m.SourceColor,
                                m.SourceSize
                            );
                        } else {
                            marker = addCircleMarker(
                                m.Destination,
                                m.DestLatitude,
                                m.DestLongitude,
                                m.DestinationColor,
                                m.DestinationSize
                            );
                        }
                        return marker;
                    },
                    onEachFeature: onEachFeatureFn,
                });
                geoJson.bindTooltip(m.Philosopher + " travels from " + m.Source + " to " + m.Destination);
                let featureLayerGroup = new L.FeatureGroup([geoJson]);
                featureLayerGroup.on({
                    mouseover: highlightFeature,
                    mouseout: resetHighlight,
                })
                switch (currentCentrality) {
                    case "Degree":
                        degreelayerGroup.addLayer(featureLayerGroup);
                        break;
                    case "Betweeness":
                        betweenesLayerGroup.addLayer(featureLayerGroup);
                        break;
                    case "Closeness":
                        closenessLayerGroup.addLayer(featureLayerGroup);
                        break;
                    case "Eigenvector":
                        eigenVectorLayerGroup.addLayer(featureLayerGroup);
                        break;
                }
                // addFilterOption(m.Philosopher);
                travelersListOptions.push(m.Philosopher);
            });
            if (currentFilter === "All") {
                addFilterOptions();
            }
            switch (currentCentrality) {
                case "Degree":
                    degreelayerGroup.addTo(baseMap);
                    updateMapLegend("Degree");
                    break;
                case "Betweeness":
                    betweenesLayerGroup.addTo(baseMap);
                    updateMapLegend("Betweeness");
                    break;
                case "Closeness":
                    closenessLayerGroup.addTo(baseMap);
                    updateMapLegend("Closeness");
                    break;
                case "Eigenvector":
                    eigenVectorLayerGroup.addTo(baseMap);
                    updateMapLegend("Eigenvector");
                    break;
            }
        }
    });
}

function updateMetricsTable() {
    type MetricsTableData = {
        City: string,
        Degree: number,
        Betweenness: number,
        Closeness: number,
        Eigenvector: number
    };
    type DataMapTable = {
        CentralizationDegree: number,
        CentralizationBetweenness: number,
        CentralizationCloseness: number,
        CentralizationEigenvector: number,
        CityData: MetricsTableData[]
    }

    let currentFilter = getFilter();
    if (currentFilter === "") {
        currentFilter = "All";
    }
    const urlBase = encodeURI(
        BASE_URL
        + "/map/get/table?filter="
        + currentFilter
    );

    $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (fullData: DataMapTable) => {
            const dataCentral = [
                [
                    "Graph",
                    String(fullData.CentralizationDegree),
                    String(fullData.CentralizationBetweenness),
                    String(fullData.CentralizationCloseness),
                    String(fullData.CentralizationEigenvector)
                ],
            ]
            $("#centralization-table").DataTable({
                data: dataCentral,
                retrieve: true,
                columns: [
                    { title: "" },
                    { title: "Degree" },
                    { title: "Betweenness" },
                    { title: "Closeness" },
                    { title: "Eigenvector" },
                ],
                "paging": false,
                "ordering": false,
                "info": false,
                "searching": false
            });
            const data: MetricsTableData[] = fullData.CityData;
            const tableData = data.map(el => [el.City, el.Degree, el.Betweenness, el.Closeness, el.Eigenvector]);
            table1.clear();
            table1.rows.add(tableData);
            table1.draw();
        }
    });
    //
}

function updateGraph() {
    const currentCentrality = getCentralityIndex();
    const nodeSizes = $(".node-range-slider").val() as string;
    const labelSizes = $(".label-range-slider").val() as string;
    let currentFilter = getFilter();
    if (currentFilter === "") {
        currentFilter = "All";
    }
    const urlBase = encodeURI(
        BASE_URL
        + "/map/get/graph?centrality="
        + currentCentrality
        + "&min_max="
        + nodeSizes
        + "&filter="
        + currentFilter
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
    clearFilters();
    table1 = $("#metrics-table").DataTable({
        columns: [
            { title: "City" },
            { title: "Degree" },
            { title: "Betweenness" },
            { title: "Closeness" },
            { title: "Eigenvector" },
        ]
    });
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

    const debouncedUpdateAll = debounce(updateAll, 4000);
    $("#filter_add").click((e) => {
        addFilter();
        debouncedUpdateAll()
    });
    $("#filter_clear").click((e) => {
        clearFilters();
    });
    $('a[data-toggle="tab"]').on('shown.bs.tab', (e) => {
        const activedTab = <HTMLAnchorElement>e.target;
        const leavedTab = <HTMLAnchorElement>e.relatedTarget;
        activeTab = activedTab.hash;
        updateAll();
    })
});
