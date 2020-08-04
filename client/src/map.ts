import "bootstrap";
import $ from "jquery";
import "!style-loader!css-loader!leaflet/dist/leaflet.css"
import * as L from "leaflet";

interface TravelsMapData {
    Source: string,
    Destination: string,
    Philosopher: string,
    SourceLatitude: number,
    SourceLongitude: number,
    DestLatitude: number,
    DestLongitude: number
}

const MAP_CENTER:L.LatLng = new L.LatLng(35.255, 24.92);
const MAIN_TILE_LAYER = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}';


// L.Icon.Default.imagePath = '.';
// L.Icon.Default.mergeOptions({
//     iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
//     iconUrl: require('leaflet/dist/images/marker-icon.png'),
//     shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
// });


$(() => {
    let markers_list: TravelsMapData[];
    const baseMap = L.map("map").setView(MAP_CENTER, 5);
    
    function addCircleMarker(popupText: string, latitude: number, longitude: number, mColor?: string) {
        if (!mColor) {
            mColor = "#959595";
        }
        const mark = L.circleMarker({ lat: latitude, lng: longitude },
            { 
                radius: 10,
                color: mColor
            });
        mark.bindPopup(popupText, { closeButton: true });
        mark.addTo(baseMap);
    }

    function drawLine(source: L.LatLng, destination: L.LatLng, popupMsg?: string) {
        const pointList = [ source, destination ];
        const poliLine = new L.Polyline(pointList, {
            color: '#333333',
            weight: 3,
            opacity: 0.5,
            smoothFactor: 1
        });
        if (popupMsg) {
            poliLine.bindPopup(popupMsg, { closeButton: true });
        }
        poliLine.addTo(baseMap);
    }

    function plotNodes(traveler: string, travelData: TravelsMapData[]) {
        
    }

    L.tileLayer(MAIN_TILE_LAYER, {
        maxZoom: 19,
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    }).addTo(baseMap);

    $.ajax({
        dataType: "json",
        url: "http://localhost:5000/map/get_travels_graph_data",
        success: (data) => {
            markers_list= data;
            markers_list.forEach((m, index) => {
                const srcGeoreference = new L.LatLng(m.SourceLatitude, m.SourceLongitude);
                const dstGeoreference = new L.LatLng(m.DestLatitude, m.DestLongitude);
                addCircleMarker(m.Source, m.SourceLatitude, m.SourceLongitude, "#0099ff");
                addCircleMarker(m.Destination, m.DestLatitude, m.DestLongitude, "#00cc00");
                drawLine(srcGeoreference, dstGeoreference, m.Philosopher + ' traveling from ' + m.Source + ' to ' + m.Destination);
            });
        }
    });
});
