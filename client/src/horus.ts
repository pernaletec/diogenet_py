/// <reference path="jquery-range.d.ts"/>
import "bootstrap";
import "!style-loader!css-loader!@fortawesome/fontawesome-free/css/all.min.css";
import $ from "jquery";
import "jquery-range";
import "!style-loader!css-loader!jquery-range/jquery.range.css";
import "datatables.net";
import "datatables.net-dt";
import "!style-loader!css-loader!datatables.net-dt/css/jquery.dataTables.min.css";

import {
  getCentralityIndex,
  getGraphLayout,
  getNodesSize,
  getLabelsSize,
  debounce,
} from "./graphLibrary";
import { BASE_URL } from "./baseURLS";

type MenuItem = {
  name: string;
  tabs: string[];
};

let activeMenu = "";
let activeTab = "";
let leavedTab = "";
let initDTable: boolean = true;
let table1: any, table2: any;

const menuItemsIds: MenuItem[] = [
  { name: "global", tabs: ["global-graph"] },
  {
    name: "global-centrality",
    tabs: [
      "global-central-graph",
      "global-heatmap-graph",
      "global-metrics-graph",
    ],
  },
  { name: "local", tabs: ["local-graph"] },
  {
    name: "local-centrality",
    tabs: ["local-central-graph", "local-heatmap-graph", "local-metrics-graph"],
  },
  { name: "communities", tabs: ["communities-graph"] },
  { name: "communities-treemap", tabs: ["communities-treemap-graph"] },
];

function getCheckedRelations(): string {
  const checkedCheckboxes = $("input:checkbox[name=edgesFilter]:checked");
  let filter = "";

  checkedCheckboxes.each((nCheckBox) => {
    let cBoxElem = <HTMLInputElement>checkedCheckboxes[nCheckBox];
    if (filter.length > 1) {
      filter += ";";
    }
    filter += cBoxElem.value;
  });
  return filter;
}

function showAppearenceControls(show: boolean) {
  if (show) {
    $("#appareance-size-div").show();
  } else {
    $("#appareance-size-div").hide();
  }
}

function showLayoutControl(show: boolean) {
  if (show) {
    $("#graph-layout-control").show();
  } else {
    $("#graph-layout-control").hide();
  }
}

function showDegreeControl(show: boolean) {
  if (show) {
    $("#centrality-index-div").show();
  } else {
    $("#centrality-index-div").hide();
  }
}

function showOrderControl(show: boolean) {
  if (show) {
    $("#ego-div").show();
  } else {
    $("#ego-div").hide();
  }
}

function setActiveMenuItem(item: string) {
  menuItemsIds.forEach((mItem) => {
    const objectName = "#" + mItem.name + "-btn";
    if (item === mItem.name) {
      $(objectName).addClass("active");
    } else {
      $(objectName).removeClass("active");
    }
  });
}

function setActiveLayout(item: string) {
  menuItemsIds.forEach((mItem) => {
    const divObjectName = "#" + mItem.name + "-main-div";
    const tabObjectName = "#" + mItem.name + "-tab-content";
    if (item === mItem.name) {
      $(divObjectName).show();
      $(tabObjectName).show();
    } else {
      $(divObjectName).hide();
      $(tabObjectName).hide();
    }
  });
}

function updateGraph(
  targetIFrame: HTMLIFrameElement,
  type: string = "global",
  showCentrality: boolean = false
) {
  const currentCentrality: string = showCentrality
    ? getCentralityIndex()
    : "None";
  let currentLayout: string = "";
  let currentFilter: string = "";
  const nodeSizes = getNodesSize();
  const labelSizes = getLabelsSize();

  switch (type) {
    case "global": {
      currentLayout = getGraphLayout();
      currentFilter = getCheckedRelations();
      let srcURL: string;
      if (currentFilter === "") {
        srcURL = "";
      } else {
        srcURL = encodeURI(
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
      }
      targetIFrame.src = srcURL;
      if (srcURL === "")
        alert("Please select at least one relation from Network Ties!");
      break;
    }
    case "local": {
      break;
    }
    case "communities": {
      break;
    }
  }
}

function updateHeatMap(
  targetIFrame: HTMLIFrameElement,
  type: string = "global"
) {
  let currentFilter: string = "";

  switch (type) {
    case "global": {
      currentFilter = getCheckedRelations();
      let srcURL: string;
      if (currentFilter === "") {
        srcURL = "";
      } else {
        srcURL = encodeURI(
          BASE_URL + "/horus/get/heatmap?filter=" + currentFilter
        );
      }
      targetIFrame.src = srcURL;
      if (srcURL === "")
        alert("Please select at least one relation from Network Ties!");
      break;
    }
    case "local": {
      break;
    }
    case "communities": {
      break;
    }
  }
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
  if (currentFilter === "") {
    table1.clear();
    table1.draw();
    table2.clear();
    table2.draw();
    alert("Please select at least one relation from Network Ties!");
  } else {
    const urlBase = encodeURI(
      BASE_URL + "/map/get/table?filter=" + currentFilter + "&type=global"
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
        table2.clear();
        table2.rows.add(dataCentral);
        table2.draw();
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
  }
  //
}

function updateTab() {
  switch (activeTab) {
    case "global-graph": {
      $("#global-graph").addClass("active");
      updateGraph($("#graph-global")[0] as HTMLIFrameElement);
      break;
    }
    case "global-central-graph": {
      $("#global-central-graph").addClass("active");
      $("#global-central-graph").addClass("show");
      updateGraph(
        $("#graph-centrality")[0] as HTMLIFrameElement,
        "global",
        true
      );
      break;
    }
    case "global-heatmap-graph": {
      //   $("#global-heatmap-graph").addClass("active");
      //   $("#global-heatmap-graph").addClass("show");
      const iFrameSrc = $("#graph-heatmap-centrality")[0] as HTMLIFrameElement;
      iFrameSrc.src = "";
      updateHeatMap(
        $("#graph-heatmap-centrality")[0] as HTMLIFrameElement,
        "global",
        true
      );
      break;
    }
    case "global-metrics-graph": {
      updateMetricsTable();
      break;
    }
    case "local-graph": {
      break;
    }
    case "local-central-graph": {
      updateGraph(
        $("#graph-local-centrality")[0] as HTMLIFrameElement,
        "local"
      );
      break;
    }
    case "local-heatmap-graph": {
      break;
    }
    case "local-metrics-graph": {
      break;
    }
    case "communities-graph": {
      updateGraph(
        $("#graph-communities")[0] as HTMLIFrameElement,
        "communities"
      );
      break;
    }
    case "communities-treemap-graph": {
      break;
    }
  }
}

function drawScreen(selectedMenu: string, selectedTab: string) {
  let mustUpdateTab: boolean = false;
  if (selectedMenu !== activeMenu || selectedTab !== activeTab) {
    switch (selectedMenu) {
      case "global": {
        activeMenu = "global";
        showLayoutControl(true);
        showDegreeControl(false);
        showOrderControl(false);
        showAppearenceControls(true);
        break;
      }
      case "global-centrality": {
        activeMenu = "global-centrality";
        if (selectedTab === "global-central-graph") {
          showLayoutControl(true);
          showDegreeControl(true);
          showOrderControl(false);
          showAppearenceControls(true);
        } else {
          showLayoutControl(false);
          showDegreeControl(false);
          showOrderControl(false);
          showAppearenceControls(false);
          if (selectedTab === "global-metrics-graph" && initDTable) {
            console.log("initial table");
            initDataTable();
          }
        }
        break;
      }
      case "local": {
        activeMenu = "local";
        showLayoutControl(false);
        showDegreeControl(false);
        showOrderControl(true);
        showAppearenceControls(true);
        break;
      }
      case "local-centrality": {
        activeMenu = "local-centrality";
        showLayoutControl(false);
        showDegreeControl(true);
        showOrderControl(true);
        showAppearenceControls(true);
        break;
      }
    }
    // Set active menu
    setActiveMenuItem(activeMenu);
    // Update Layout
    setActiveLayout(activeMenu);
    let activeMenuItem = menuItemsIds.find((item) => item.name === activeMenu);
    if (activeMenuItem) {
      let tab2Click = activeMenuItem.tabs[0];
      console.log("Trigging click on tab " + tab2Click);
      const tabName = "#" + tab2Click;
      $(tabName).trigger("click");
      activeTab = selectedTab;
    }
    mustUpdateTab = true;
  }
  if (mustUpdateTab || selectedTab !== activeTab) {
    updateTab();
  }
}

function initDataTable() {
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
      { title: "Philosopher" },
      { title: "Degree" },
      { title: "Betweenness" },
      { title: "Closeness" },
      { title: "Eigenvector" },
    ],
  });
  table2 = $("#centralization-table").DataTable({
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
  initDTable = false;
}

function initRangeSlider(classname: string) {
  $("." + classname).jRange({
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
}

const debouncedUpdateGraph = debounce(updateGraph, 4000);

$(() => {
  initRangeSlider("node-range-slider");
  initRangeSlider("label-range-slider");

  $("#graph-layout").on("change", (event) => {
    updateTab();
  });
  $("input:checkbox[name=edgesFilter]").on("change", (event) => {
    updateTab();
  });
  $(".node-range-slider").on("change", (event) => {
    updateTab();
  });
  $(".label-range-slider").on("change", (event) => {
    updateTab();
  });
  $("#centrality-index").on("change", (event) => {
    updateTab();
  });

  $("#global-btn").on("click", () => {
    drawScreen("global", "global-graph");
  });
  $("#global-centrality-btn").on("click", () => {
    drawScreen("global-centrality", "global-central-graph");
  });

  $('a[data-toggle="tab"]').on("shown.bs.tab", (e) => {
    const activedTab = <HTMLAnchorElement>e.target;
    //const leavedTab = <HTMLAnchorElement>e.relatedTarget;
    const clickedTab = activedTab.hash.substring(1);
    console.log("Click on: " + clickedTab);
    drawScreen(activeMenu, clickedTab);
  });

  drawScreen("global", "global-graph");
});
