// in the global namesapce "L"
import * as L from 'leaflet';

declare module 'leaflet' {
    // there is a child namespace "vectorGrid"
    class HtmlLegend extends Control {
        constructor(_map: null, _activeLayers: 0, _alwaysShow: false, options?: any);
        addLegend(options: {name: string, layer: L.Layer, elements: any[]}): void;
    }
    namespace control {
        function htmllegend(options?: any): HtmlLegend;
    }
}
