import "bootstrap";
import "!style-loader!css-loader!@fortawesome/fontawesome-free/css/all.min.css";
import $ from "jquery";
import "jquery-range";
import "!style-loader!css-loader!jquery-range/jquery.range.css";

import { getGraphLayout, debounce } from "./graphLibrary";
import { BASE_URL } from "./baseURLS";


function getCheckedRelations() {
    const checkedCheckboxes = $("input:checkbox[name=edgesFilter]:checked");
    let filter = "";

    checkedCheckboxes.each(nCheckBox => { 
        let cBoxElem = <HTMLInputElement>checkedCheckboxes[nCheckBox];
        if (filter.length > 1) { filter += ";"; };
        filter += cBoxElem.value;
    });

    return filter;
}

function updateGraph() {
    const currentCentrality = "Degree";
    const currentLayout = getGraphLayout();
    const nodeSizes = $(".node-range-slider").val() as string;
    const labelSizes = $(".label-range-slider").val() as string;
    let currentFilter = getCheckedRelations();
    const urlBase = encodeURI(
        BASE_URL +
        "/horus/get/graph?centrality=" +
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
    $("input:checkbox[name=edgesFilter]").change((event) => {
        updateGraph();
    });

    const debouncedUpdateGraph = debounce(updateGraph, 4000);
    $(".node-range-slider").change((event) => {
        debouncedUpdateGraph();
    });
    $(".label-range-slider").change((event) => {
        debouncedUpdateGraph();
    });

    updateGraph();
});