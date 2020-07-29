import "bootstrap";
import $ from "jquery";
import "!style-loader!css-loader!leaflet/dist/leaflet.css"
import * as L from "leaflet";

const MAP_CENTER:L.LatLng = new L.LatLng(51.505, -0.09);
const MAIN_TILE_LAYER = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

// L.Icon.Default.imagePath = '.';
// L.Icon.Default.mergeOptions({
//     iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
//     iconUrl: require('leaflet/dist/images/marker-icon.png'),
//     shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
// });

$(() => {
    const baseMap = L.map("map").setView(MAP_CENTER, 13);

    L.tileLayer(MAIN_TILE_LAYER, {
        attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
    }).addTo(baseMap);
});
