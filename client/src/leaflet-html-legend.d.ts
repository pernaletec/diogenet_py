// in the global namesapce "L"
import * as L from 'leaflet';

declare module 'leaflet' {
    // there is a child namespace "vectorGrid"
    class HtmlLegend extends Control {
        constructor(_map: null, _activeLayers: 0, _alwaysShow: false, options?: any);
    }
    class
        L.control.htmllegend()
}

