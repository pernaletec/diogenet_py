import "bootstrap";
import "!style-loader!css-loader!@fortawesome/fontawesome-free/css/all.min.css";
import $ from "jquery";

export const VIRIDIS_COLORMAP = [
    { r: 68, g: 1, b: 84 },
    { r: 72, g: 40, b: 120 },
    { r: 62, g: 74, b: 137 },
    { r: 49, g: 104, b: 142 },
    { r: 38, g: 130, b: 142 },
    { r: 31, g: 158, b: 137 },
    { r: 53, g: 183, b: 121 },
    { r: 109, g: 205, b: 89 },
    { r: 180, g: 222, b: 44 },
    { r: 253, g: 231, b: 37 },
];

export function componentToHex(c: number) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

export function rgbToHex(r: number, g: number, b: number) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

export function interpolateValue(
    minVal: number,
    maxVal: number,
    value: number
    ): string {
    return (((maxVal - minVal) / 10) * value).toFixed(2);
}

export function getCentralityIndex() {
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

export function getGraphLayout() {
    const value = $("#graph-layout").val();
    let layout = null;
    if (value) {
        layout = value;
    }
    return layout;
}

export function debounce<Params extends any[]>(
    func: (...args: Params) => any,
    timeout: number
): (...args: Params) => void {
    let timer: NodeJS.Timeout;
    return (...args: Params) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func(...args);
        }, timeout);
    };
}