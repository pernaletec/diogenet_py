import "bootstrap";
import "!style-loader!css-loader!@fortawesome/fontawesome-free/css/all.min.css";
import $ from "jquery";
import "jquery-range";
import "!style-loader!css-loader!jquery-range/jquery.range.css";

import { getGraphLayout } from "./graphLibrary";
import { BASE_URL } from "./baseURLS";


function updateGraph() {
    const currentCentrality = "Degree";
    const currentLayout = getGraphLayout();
    const nodeSizes = $(".node-range-slider").val() as string;
    const labelSizes = $(".label-range-slider").val() as string;
    let currentFilter = "All";
    const urlBase = encodeURI(
        BASE_URL +
        "/map/get/graph?centrality=" +
        currentCentrality +
        "&node_min_max=" +
        nodeSizes +
        "&label_min_max=" +
        labelSizes +
        "&filter=" +
        currentFilter + 
        "&layout=" +
        currentLayout
    );
    let graphiFrame = $("#graph-global")[0] as HTMLIFrameElement;
    graphiFrame.src = urlBase;
    console.log(urlBase);
}


$(() => { 
    $(".node-range-slider").jRange({
        from: 1,
        to: 10,
        step: 1,
        scale: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        format: "%s",
        width: 200,
        showLabels: true,
        isRange: true,
        snap: true,
        theme: "theme-blue",
    });
    $(".label-range-slider").jRange({
        from: 1,
        to: 10,
        step: 1,
        scale: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        format: "%s",
        width: 200,
        showLabels: true,
        isRange: true,
        snap: true,
        theme: "theme-blue",
    });
    $("#graph-layout").change((event) => {
        updateGraph();
    });

    updateGraph();
});