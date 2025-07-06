import { DEVMODE } from "./globals"
import { DATA_SATURATION, getVectorizedDataSaturation } from "./data_connector"
import $ from 'jquery';
import bb, { line, scatter } from "billboard.js";
import "billboard.js/dist/billboard.css";
import { PCA } from "ml-pca";

function fake_year_saturation(title: string, saturation: number) {
  let data_x = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
  // generate fake data from 0.1 to saturattion. it should be the same length as data_y and monotonous increasing
  let data_y_human = data_x.map(x => Math.random() * saturation * 80 + 20)
  data_y_human.sort((a, b) => a - b);
  let data_y_metrics = data_y_human.map(y => y + (Math.random() - 0.5) * 10);

  let _ = bb.generate({
    bindto: "#year_chart_container",
    data: {
      type: line(),
      x: "x",
      xFormat: "%Y",
      columns: [
        ["x", ...data_x],
        ["Human evaluation", ...data_y_human],
        ["Automated Metrics", ...data_y_metrics]
      ],
    },
    axis: {
      x: {},
      y: {
        label: "Performance (%)",
        tick: {
          format: function (d: number) { return d.toFixed(0); },
          // ticks
          values: [0, 20, 40, 60, 80, 100]
        },
        min: 0,
        max: 100,
      }
    },
    // legend on the right
    legend: {
      position: "right"
    },
  });
}


function redo_task_saturation(data_saturation) {
  $("#task_saturation").empty(); // clear existing table content
  for (const [task, datasets] of Object.entries(data_saturation)) {
    // create row element based on task and datasets
    const row = $("<tr></tr>");
    row.append($("<td></td>").text(task));
    for (const [dataset, dataset_dict] of Object.entries(datasets)) {
      let alpha = Math.floor((dataset_dict["saturation"] - 0.3) * 0.9 * 255).toString(16).padStart(2, '0')
      let color = "#304050" + alpha
      const cell = $(`<td style="background-color: ${color}"></td>`).text(
        `${dataset} ${dataset_dict["saturation"].toFixed(2)}`
      );
      row.append(cell);
      cell.on("click", function () {
        fake_year_saturation(`${task} / ${dataset}`, dataset_dict["saturation"])
      })
    }
    // append row to table
    $("#task_saturation").append(row);
  }

  let data_saturation_vec = getVectorizedDataSaturation(data_saturation);
  const pca = new PCA(data_saturation_vec.map(d => d.vector));
  let data_saturation_new = pca.predict(data_saturation_vec.map(d => d.vector)).to2DArray();

  let _ = bb.generate({
    bindto: "#cluster_chart_container",
    data: {
      type: scatter(),
      xs: {
        dataset: "dataset_x",
      },
      columns: [
        // take first two dimensions
        ["dataset_x", ...data_saturation_new.map(d => d[0])],
        ["dataset", ...data_saturation_new.map(d => d[2])],
      ],
      // labels: false,
    },
    tooltip: {
      show: false  // <--- disables hover tooltips
    },
    axis: {
      x: {
        label: "Dimension 1",
        tick: {
          values: [],
        },
      },
      y: {
        label: "Dimension 2",
        tick: {
          values: [],
        },
      }
    },
    legend: {
      position: "right"
    }
  });

  // TODO: add labels with dataset name
  // TODO: add on-click action
  // TODO: add mouse-over action
  data_saturation_vec.map((d, i) => {
    // this is hijacking the structure of billboard.js
    let el = $(`#cluster_chart_container .bb-shape-${i}`)
    // el is of type <circle> and doesn't have "on" by default
  })
}

let saturation_when_1 = "average_model";
let saturation_when_2 = "hum";

function refresh_saturation_when() {
  $("#img_saturation_when").attr("src", `figures/mock_performance_${saturation_when_1}_${saturation_when_2}.svg`);

  // clone DATA_SATURATION
  let data_saturation = JSON.parse(JSON.stringify(DATA_SATURATION));
  // modify in place
  for (const [task, datasets] of Object.entries(data_saturation)) {
    for (const [dataset, dataset_dic] of Object.entries(datasets)) {
      let rand = Math.random() * 0.2 + 0.9;
      datasets[dataset]["saturation"] = Math.min(1.0, datasets[dataset]["saturation"] * rand)
    }
  }

  redo_task_saturation(data_saturation);
}

$("#select_saturation_when_1").on("change", function () {
  saturation_when_1 = $(this).val() as string;
  refresh_saturation_when();
})

$("#select_saturation_when_2").on("change", function () {
  saturation_when_2 = $(this).val() as string;
  refresh_saturation_when();
})

$("#select_saturation_when_1").trigger("change");
$("#select_saturation_when_2").trigger("change");