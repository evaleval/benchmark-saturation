import { DEVMODE } from "./globals"
import { DATA_SATURATION } from "./data_connector"
import $ from 'jquery';
import bb, { line } from "billboard.js";
import "billboard.js/dist/billboard.css";

function fake_graph(title: string, saturation: number) {
  let data_x = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
  // generate fake data from 0.1 to saturattion. it should be the same length as data_y and monotonous increasing
  let data_y_human = data_x.map(x => Math.random() * saturation * 100)
  data_y_human.sort((a, b) => a - b);
  // add some random noise to the data_y_top
  let data_y_metrics = data_y_human.map(y => y + (Math.random() - 0.5) * 10);

  var chart = bb.generate({
    bindto: "#chart_container",
    data: {
      type: line(),
      x: "x",
      xFormat: "%Y", // specify the format of the x data
      // precision of y axis is 2 decimal places
      columns: [
        ["x", ...data_x],
        ["Human evaluation", ...data_y_human],
        ["Automated Metrics", ...data_y_metrics]
      ],
    },
    axis: {
      x: {
        // label: "Year",
        // type: "category"
      },
      y: {
        label: "Performance (%)",
        tick: {
          format: function (d) { return d.toFixed(2); }
        },
        // span 0 to 100
        min: 0,
        max: 100,
      }
    },
  });
}


function redo_task_saturation(task_saturation) {
  $("#task_saturation").empty(); // clear existing table content
  for (const [task, datasets] of Object.entries(task_saturation)) {
    // create row element based on task and datasets
    const row = $("<tr></tr>");
    row.append($("<td></td>").text(task));
    for (const [dataset, saturation] of Object.entries(datasets)) {
      let alpha = Math.floor((saturation - 0.3) * 0.9 * 255).toString(16).padStart(2, '0')
      let color = "#304050" + alpha
      const cell = $(`<td style="background-color: ${color}"></td>`).text(
        `${dataset} ${saturation.toFixed(2)}`
      );
      row.append(cell);
      cell.on("click", function () {
        fake_graph(`${task} / ${dataset}`, saturation)
      })
    }
    // append row to table
    $("#task_saturation").append(row);
  }

}

// redo_task_saturation(DATA_SATURATION);

let saturation_when_1 = "average_model";
let saturation_when_2 = "hum";

function refresh_saturation_when() {
  $("#img_saturation_when").attr("src", `figures/mock_performance_${saturation_when_1}_${saturation_when_2}.svg`);

  // clone TASK_SATURATION
  let task_saturation = JSON.parse(JSON.stringify(DATA_SATURATION));
  // modify in place
  for (const [task, datasets] of Object.entries(task_saturation)) {
    for (const [dataset, saturation] of Object.entries(datasets)) {
      let rand = Math.random() * 0.2 + 0.9; // random number between 0.9 and 1.1
      datasets[dataset] = Math.min(1.0, datasets[dataset] * rand)
    }
  }

  redo_task_saturation(task_saturation);
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