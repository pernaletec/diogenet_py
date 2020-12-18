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
let initDTableEgo: boolean = true;
let table1: any, table2: any, table3: any, table4: any;
let egoFilled: boolean = false;

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

function getEgo(): string {
  let strValue: string = "";
  if ($("#ego-index").val()) {
    strValue = $("#ego-index  option:selected").text();
  }
  return strValue;
}

function getOrder() {
  return $("#order-size").val() as string;
}

function getAlgorithm() {
  //   let strValue: string = "";
  //   if ($("#community-alg-index").val()) {
  //     strValue = $("#community-alg-index  option:selected").text();
  //   }
  return $("#community-alg-index").val();
}

function getPlotType() {
  return $("#community-library-index").val();
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
    type Philosophers = {
      name: string;
    };
    if (!egoFilled) {
      const urlBase = encodeURI(BASE_URL + "/horus/get/ego");
      const egoSelect: HTMLSelectElement = <HTMLSelectElement>(
        document.getElementById("ego-index")
      );
      $.ajax({
        dataType: "text json",
        url: urlBase,
        success: (fullData: Philosophers[]) => {
          for (let i = 0; i < fullData.length; i++) {
            const philosopher = fullData[i];
            $("#ego-index").append(
              new Option(philosopher.name, philosopher.name)
            );
            if (philosopher.name === "Plato") egoSelect.selectedIndex = i;
          }
          egoFilled = true;
        },
      });
    }
  } else {
    $("#ego-div").hide();
  }
}

function showCommunitiesControls(show: boolean) {
  if (show) {
    $("#communities-div").show();
    if (activeMenu === "communities") {
      $("#communities-viz-div").show();
    }
  } else {
    $("#communities-div").hide();
    $("#communities-viz-div").hide();
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
            "&graph_type=local" +
            "&ego=" +
            getEgo() +
            "&order=" +
            getOrder()
        );
      }
      console.log(srcURL);
      targetIFrame.src = srcURL;
      if (srcURL === "")
        alert("Please select at least one relation from Network Ties!");
      break;
    }
    case "communities": {
      currentLayout = "fr";
      const communityCentrality = "communities";
      currentFilter = getCheckedRelations();
      let srcURL: string;
      if (currentFilter === "") {
        srcURL = "";
      } else {
        srcURL = encodeURI(
          BASE_URL +
            "/horus/get/graph?centrality=" +
            communityCentrality +
            "&node_min_max=" +
            nodeSizes +
            "&label_min_max=" +
            labelSizes +
            "&filter=" +
            currentFilter +
            "&layout=" +
            currentLayout +
            "&graph_type=community" +
            "&algorithm=" +
            getAlgorithm() +
            "&plot=" +
            getPlotType()
        );
      }
      console.log(srcURL);
      targetIFrame.src = srcURL;
      if (srcURL === "")
        alert("Please select at least one relation from Network Ties!");
      break;
    }
  }
}

function updateHeatMap(
  targetIFrame: HTMLIFrameElement,
  type: string = "global"
) {
  let srcURL: string = "";
  let currentFilter: string = getCheckedRelations();

  if (currentFilter === "") {
    alert("Please select at least one relation from Network Ties!");
    targetIFrame.src = "";
  } else {
    switch (type) {
      case "global": {
        srcURL = encodeURI(
          BASE_URL + "/horus/get/heatmap?filter=" + currentFilter
        );
        targetIFrame.src = srcURL;
        break;
      }
      case "local": {
        srcURL = encodeURI(
          BASE_URL +
            "/horus/get/heatmap?graph_type=local&filter=" +
            currentFilter +
            "&ego=" +
            getEgo() +
            "&order=" +
            getOrder()
        );
        targetIFrame.src = srcURL;
        break;
      }
      case "communities": {
        srcURL = encodeURI(
          BASE_URL +
            "/horus/get/treemap?filter=" +
            currentFilter +
            "&graph_type=community" +
            "&algorithm=" +
            getAlgorithm()
        );
        targetIFrame.src = srcURL;
        break;
      }
    }
  }
}

function updateMetricsTable(tables = "global") {
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
    if (tables === "global") {
      table1.clear();
      table1.draw();
      table2.clear();
      table2.draw();
    } else {
      table3.clear();
      table3.draw();
      table4.clear();
      table4.draw();
    }
    alert("Please select at least one relation from Network Ties!");
  } else {
    console.log("******************************** entrando a datatable 3 y 4");
    const urlBase = encodeURI(
      BASE_URL +
        "/map/get/table?filter=" +
        currentFilter +
        "&type=" +
        tables +
        "&ego=" +
        getEgo() +
        "&order=" +
        getOrder()
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

        const data: MetricsTableData[] = fullData.CityData;
        const tableData = data.map((el) => [
          el.City,
          el.Degree,
          el.Betweenness,
          el.Closeness,
          el.Eigenvector,
        ]);

        if (tables == "global") {
          table2.clear();
          table2.rows.add(dataCentral);
          table2.draw();
          table1.clear();
          table1.rows.add(tableData);
          table1.draw();
        } else {
          table4.clear();
          table4.rows.add(dataCentral);
          table4.draw();
          table3.clear();
          table3.rows.add(tableData);
          table3.draw();
        }
      },
    });
  }
  //
}

function updateTab() {
  switch (activeTab) {
    case "global-graph": {
      $("#global-graph a").trigger("click");
      updateGraph($("#graph-global")[0] as HTMLIFrameElement);
      break;
    }
    case "global-central-graph": {
      $("#global-central-graph a").trigger("click");
      updateGraph(
        $("#graph-centrality")[0] as HTMLIFrameElement,
        "global",
        true
      );
      break;
    }
    case "global-heatmap-graph": {
      $("#global-heatmap-graph a").trigger("click");
      const iFrameSrc = $("#graph-heatmap-centrality")[0] as HTMLIFrameElement;
      iFrameSrc.src = "";
      updateHeatMap(
        $("#graph-heatmap-centrality")[0] as HTMLIFrameElement,
        "global"
      );
      break;
    }
    case "global-metrics-graph": {
      $("#global-metrics-graph a").trigger("click");
      updateMetricsTable();
      break;
    }
    case "local-graph": {
      $("#local-graph").find("a").trigger("click");
      updateGraph($("#graph-local")[0] as HTMLIFrameElement, "local");
      break;
    }
    case "local-central-graph": {
      console.log("Updating tab local+centrality+tab");
      $("#local-central-graph").find("a").trigger("click");
      $("#local-central-graph").click();
      updateGraph(
        $("#graph-local-centrality")[0] as HTMLIFrameElement,
        "local",
        true
      );
      break;
    }
    case "local-heatmap-graph": {
      $("#local-heatmap-graph a").trigger("click");
      const iFrameSrc = $("#heatmap-local-centrality")[0] as HTMLIFrameElement;
      iFrameSrc.src = "";
      updateHeatMap(
        $("#heatmap-local-centrality")[0] as HTMLIFrameElement,
        "local"
      );
      break;
    }
    case "local-metrics-graph": {
      $("#local-metrics-graph a").trigger("click");
      updateMetricsTable("local");
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
      updateHeatMap(
        $("#graph-treemap-communities")[0] as HTMLIFrameElement,
        "communities"
      );
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
        showCommunitiesControls(false);
        break;
      }
      case "global-centrality": {
        activeMenu = "global-centrality";
        if (selectedTab === "global-central-graph") {
          showLayoutControl(true);
          showDegreeControl(true);
          showOrderControl(false);
          showAppearenceControls(true);
          showCommunitiesControls(false);
        } else {
          showLayoutControl(false);
          showDegreeControl(false);
          showOrderControl(false);
          showAppearenceControls(false);
          showCommunitiesControls(false);
          if (selectedTab === "global-metrics-graph" && initDTable) {
            initDataTable("global");
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
        showCommunitiesControls(false);
        break;
      }
      case "local-centrality": {
        activeMenu = "local-centrality";
        if (selectedTab === "local-central-graph") {
          showLayoutControl(true);
          showDegreeControl(true);
          showOrderControl(true);
          showAppearenceControls(true);
          showCommunitiesControls(false);
        } else {
          showLayoutControl(false);
          showDegreeControl(false);
          showOrderControl(true);
          showAppearenceControls(false);
          showCommunitiesControls(false);
          if (selectedTab === "local-metrics-graph" && initDTableEgo) {
            console.log("initial table LOCALLLLLL");
            console.log("initial table");
            initDataTable("local");
          }
        }
        break;
      }
      case "communities": {
        activeMenu = "communities";
        showLayoutControl(false);
        showDegreeControl(false);
        showOrderControl(false);
        showAppearenceControls(true);
        showCommunitiesControls(true);
        break;
      }
      case "communities-treemap": {
        activeMenu = "communities-treemap";
        showLayoutControl(false);
        showDegreeControl(false);
        showOrderControl(false);
        showAppearenceControls(false);
        showCommunitiesControls(true);
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
      const tabName = "#" + tab2Click;
      $(tabName + " a").trigger("click");
      console.log("Tabname: " + tabName);
      console.log("selectedTab: " + selectedTab);
      console.log("activeTab: " + activeTab);
      activeTab = selectedTab;
    }
    mustUpdateTab = true;
  }
  if (mustUpdateTab || selectedTab !== activeTab) {
    updateTab();
  }
}

function initDataTable(dtType: string = "global") {
  if (dtType === "global") {
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
  } else {
    table3 = $("#local-metrics-table").DataTable({
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
    table4 = $("#local-centralization-table").DataTable({
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
    initDTableEgo = false;
  }
}

function initRangeSlider(
  classname: string,
  range_min: string = "1",
  range_max: string = "10",
  step: string = "1"
) {
  let scale, isRange;
  if (range_max == "10") {
    scale = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    isRange = true;
  } else {
    scale = [1, 2, 3, 4];
    isRange = false;
  }

  $("." + classname).jRange({
    from: range_min,
    to: range_max,
    step: step,
    scale: scale,
    format: "%s",
    width: 200,
    showLabels: true,
    isRange: isRange,
    snap: true,
    theme: "theme-blue",
  });
}

const debouncedUpdateGraph = debounce(updateGraph, 4000);

$(() => {
  document.getElementsByTagName("html")[0].style.height = "100%";
  document.getElementsByTagName("body")[0].style.height = "100%";
  initRangeSlider("node-range-slider");
  initRangeSlider("label-range-slider");
  initRangeSlider("order-range-slider", "1", "4", "1");
  $("#ego-order-div .pointer.low").hide();

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
  $(".order-range-slider").on("change", (event) => {
    updateTab();
  });

  $("#ego-index").on("change", (event) => {
    updateTab();
  });

  $("#community-alg-index").on("change", (event) => {
    updateTab();
  });

  $("#community-library-index").on("change", (event) => {
    updateTab();
  });

  $("#global-btn").on("click", () => {
    drawScreen("global", "global-graph");
  });
  $("#global-centrality-btn").on("click", () => {
    drawScreen("global-centrality", "global-central-graph");
  });
  $("#local-btn").on("click", () => {
    drawScreen("local", "local-graph");
  });
  $("#local-centrality-btn").on("click", () => {
    drawScreen("local-centrality", "local-central-graph");
  });
  $("#communities-btn").on("click", () => {
    drawScreen("communities", "communities-graph");
  });
  $("#communities-treemap-btn").on("click", () => {
    drawScreen("communities-treemap", "communities-treemap-graph");
  });

  $('a[data-toggle="tab"]').on("shown.bs.tab", (e) => {
    const activedTab = <HTMLAnchorElement>e.target;
    //const leavedTab = <HTMLAnchorElement>e.relatedTarget;
    const clickedTab = activedTab.hash.substring(1);
    console.log("Fired drawScreen(" + activeMenu + "," + clickedTab + ")");
    drawScreen(activeMenu, clickedTab);
  });

  drawScreen("global", "global-graph");
});
