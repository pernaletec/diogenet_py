import "bootstrap";
import "!style-loader!css-loader!@fortawesome/fontawesome-free/css/all.min.css";
import $ from "jquery";
import "jquery-range";
import "!style-loader!css-loader!jquery-range/jquery.range.css";

import { getCentralityIndex, getGraphLayout, getNodesSize, getLabelsSize, debounce } from "./graphLibrary";
import { BASE_URL } from "./baseURLS";


let activeTab = "#global-graph";
let leaveTab = "";
let mainMenuValue = "global";
let table1: any;

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

function updateMetricsTable() {
    type MetricsTableData = {
        City: string;
        Degree: number;
        Betweenness: number;
        Closeness: number;
        Eigenvector: number;
    };
    type DataMapTable = {
        CentralizationDegree: number;
        CentralizationBetweenness: number;
        CentralizationCloseness: number;
        CentralizationEigenvector: number;
        CityData: MetricsTableData[];
    };

    let currentFilter = getCheckedRelations();
    const urlBase = encodeURI(
        BASE_URL + "/map/get/table?filter=" 
        + currentFilter
        + "&type=global"
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
                String(fullData.CentralizationEigenvector),
            ],
        ];
        $("#centralization-table").DataTable({
            data: dataCentral,
            retrieve: true,
            columnDefs: [
                {
                    targets: [1],
                    className: "dt-body-right",
                    render: (data, type, row) => {
                        return Number(data).toLocaleString(undefined, {
                            minimumFractionDigits: 0,
                        });
                    },
                },
                {
                    targets: [2, 3, 4],
                    className: "dt-body-right",
                    render: (data, type, row) => {
                        return Number(data).toLocaleString(undefined, {
                            minimumFractionDigits: 6,
                        });
                    },
                },
            ],
            columns: [
                { title: "" },
                { title: "Degree" },
                { title: "Betweenness" },
                { title: "Closeness" },
                { title: "Eigenvector" },
            ],
            paging: false,
            ordering: false,
            info: false,
            searching: false,
        });
        const data: MetricsTableData[] = fullData.CityData;
        const tableData = data.map((el) => [
            el.City,
            el.Degree,
            el.Betweenness,
            el.Closeness,
            el.Eigenvector,
        ]);
        table1.clear();
        table1.rows.add(tableData);
        table1.draw();
    },
});
  //
}


function updateGraph() {
    let currentCentrality = "";
    if (mainMenuValue.includes("centrality")) {
        currentCentrality = getCentralityIndex();
    } else {
        currentCentrality = "None";
    }
    const currentLayout = getGraphLayout();
    const nodeSizes = getNodesSize();
    const labelSizes = getLabelsSize();
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
    let graphiFrame: HTMLIFrameElement;
    // debugger;
    switch (mainMenuValue) {
        case "global": {
            graphiFrame = $("#graph-global")[0] as HTMLIFrameElement;
            graphiFrame.src = urlBase;
            break;
        }
        case "global+centrality": {
            //debugger;
            graphiFrame = $("#graph-centrality")[0] as HTMLIFrameElement;
            graphiFrame.src = urlBase;
            break;
        }
        case "local": {
            $("#local-btn").removeClass("active");
            break;
        }
        case "local+centrality": {
            $("#local-centrality-btn").removeClass("active");
            break;
        }
        case "communities": {
            $("#communities-btn").removeClass("active");
            break;
        }
        case "communities+treemap": {
            $("#communities-treemap-btn").removeClass("active");
            break;
        }
    }
}

function mainMenu(menuItem: string) {
    // mainMenuValue = menuItem;
    // debugger;
    switch (menuItem) {
        case "global": {
            // Hide global+centrality MenuItem & Tab container
            $("#global-centrality-main-div").hide();
            $("#global-centrality-tab-content").hide();
            // Show lobal MenuItem & Tab container
            $("#global-main-div").show()
            $("#global-tab-content").show();
            // Hide lateral centrality index selector
            $("#centrality-index-div").hide();
            // Set Active menu item
            $("#global-btn").addClass("active");
            $("#graph-tab").trigger('click');
            break;
        }
        case "global+centrality": {
            // Hide global tabitem & Tab container
            $("#global-main-div").hide()
            $("#global-tab-content").hide();
            // show global+centrality MenuItem & Ta container
            $("#global-centrality-main-div").show();
            $("#global-centrality-tab-content").show();
            // Show lateral centrality index selector
            $("#centrality-index-div").show();
            // Set Active menu item
            $("#global-centrality-btn").addClass("active");
            $("#graph-central-tab").trigger('click');
            break;
        }
        case "local": {
            $("#local-btn").addClass("active");
            break;
        }
        case "local+centrality": {
            $("#local-centrality-btn").addClass("active");
            break;
        }
        case "communities": {
            $("#communities-btn").addClass("active");
            break;
        }
        case "communities+treemap": {
            $("#communities-treemap-btn").addClass("active");
            break;
        }
    }
    switch (mainMenuValue) {
        case "global": {
            $("#global-btn").removeClass("active");
            break;
        }
        case "global+centrality": {
            $("#global-centrality-btn").removeClass("active");
            break;
        }
        case "local": {
            $("#local-btn").removeClass("active");
            break;
        }
        case "local+centrality": {
            $("#local-centrality-btn").removeClass("active");
            break;
        }
        case "communities": {
            $("#communities-btn").removeClass("active");
            break;
        }
        case "communities+treemap": {
            $("#communities-treemap-btn").removeClass("active");
            break;
        }
    }
    mainMenuValue = menuItem;
    updateGraph();
}


$(() => { 
      table1 = $("#metrics-table").DataTable({
    columnDefs: [
      {
        targets: [1],
        className: "dt-body-right",
        render: (data, type, row) => {
          return Number(data).toLocaleString(undefined, {
            minimumFractionDigits: 0,
          });
        },
      },
      {
        targets: [2, 3, 4],
        className: "dt-body-right",
        render: (data, type, row) => {
          return Number(data).toLocaleString(undefined, {
            minimumFractionDigits: 6,
          });
        },
      },
    ],
    columns: [
      { title: "City" },
      { title: "Degree" },
      { title: "Betweenness" },
      { title: "Closeness" },
      { title: "Eigenvector" },
    ],
  });

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

    const debouncedUpdateGraph = debounce(updateGraph, 4000);

    $("#graph-layout").change((event) => {
        updateGraph();
    });
    $("input:checkbox[name=edgesFilter]").change((event) => {
        updateGraph();
    });
    $(".node-range-slider").change((event) => {
        debouncedUpdateGraph();
    });
    $(".label-range-slider").change((event) => {
        debouncedUpdateGraph();
    });
    $("#centrality-index").change((event) => {
        updateGraph();
    });

    $("#global-btn").on("click", () => { 
        mainMenu("global");
    });
    $("#global-centrality-btn").on("click", () => { 
        mainMenu("global+centrality");
    });

    $('a[data-toggle="tab"]').on("shown.bs.tab", (e) => {
        const activedTab = <HTMLAnchorElement>e.target;
        const leavedTab = <HTMLAnchorElement>e.relatedTarget;
        activeTab = activedTab.hash;
        leaveTab = leavedTab.hash;
    });
    mainMenu("global"); 
});