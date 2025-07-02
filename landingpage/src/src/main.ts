import { DEVMODE } from "./globals"


$("#task_saturation")

let TASKS_SATURATION = {
  "Translation": {
    "WMT20": 0.9,
    "WMT21": 0.85,
    "WMT22": 0.8,
    "WMT23": 0.8,
    "WMT24": 0.77,
  },
  "Summarization": {
    "SummEval": 1.0,
    "MyEval": 0.7,
    "BookSum": 1.0,
    "ScisummNet": 0.95,
    "LongSum": 0.3,
  },
  "Open-Ended": {
    "HellaSwag": 0.6,
    "OpenBookQA": 0.45,
    "ARC": 0.6,
    "MMLU": 0.85,
    "Winogrande": 0.9,
  },
  "Closed-Ended": {
    "TriviaQA": 1.0,
    "NaturalQuest.": 0.99,
    "HotpotQA": 1.0,
    "WebQuestions": 0.99,
    "SearchQA": 0.99,
  },
  "Reasoning": {
    "ARC": 0.6,
    "HellaSwag": 0.6,
    "OpenBookQA": 0.45,
    "MMLU": 0.85,
    "Winogrande": 0.9,
  },
  "Retrieval": {
    "MS MARCO": 0.95,
    "TREC": 0.9,
    "NQ": 0.99,
    "HotpotQA": 1.0,
    "TriviaQA": 1.0,
  },
  "Classification": {
    "AG News": 0.95,
    "SST-2": 0.9,
    "IMDB": 0.85,
    "Yelp": 0.8,
    "TREC": 0.9,
  },
  "Generation": {
    "WikiText-2": 0.9,
    "LAMBADA": 0.85,
    "Text8": 0.8,
    "PTB": 0.75,
    "Penn Treebank": 0.7,
  },
  "Vision": {
    "ImageNet": 0.95,
    "CIFAR-10": 0.9,
    "CIFAR-100": 0.85,
    "MNIST": 0.8,
    "FashionMNIST": 0.75,
  },
  "Audio": {
    "LibriSpeech": 0.95,
    "CommonVoice": 0.9,
    "VoxCeleb": 0.85,
    "Urban8K": 0.8,
    "ESC-50": 0.75,
  },
  "Multimodal": {
    "VQA": 0.9,
    "MS COCO": 0.85,
    "Flickr30k": 0.8,
    "Visual Genome": 0.75,
    "CLEVR": 0.7,
  },
  "Time Series": {
    "UCR Archive": 0.95,
    "ECG5000": 0.9,
    "ElectricDevices": 0.85,
    "FaceDetection": 0.8,
    "GesturePhase": 0.75,
  },
  "Graph": {
    "Cora": 0.9,
    "Citeseer": 0.85,
    "Pubmed": 0.8,
    "Reddit": 0.75,
    "Amazon": 0.7,
  },
  "Tabular": {
    "Adult": 0.95,
    "IncomeCens": 0.9,
    "Card Fraud": 0.85,
    "Titanic": 0.8,
    "House Prices": 0.75,
  }
}

function fake_graph(title: string, saturation: number) {
  var options = {
    animationEnabled: true,
    theme: "light2",
    backgroundColor: "transparent",
    // width
    width: 800,
    title:{
      text: title,
    },
    axisX:{
      valueFormatString: "YYYY"
    },
    axisY: {
      title: "Performance",
      minimum: 0.30
    },
    toolTip:{
      shared:true
    },  
    legend:{
      cursor:"pointer",
      verticalAlign: "bottom",
      horizontalAlign: "left",
      dockInsidePlotArea: true,
    },
    data: [{
      type: "line",
      showInLegend: true,
      name: "Best Model Performance",
      markerType: "square",
      xValueFormatString: "YYYY",
      color: "#F08080",
      yValueFormatString: "#,##",
      dataPoints: [
        { x: new Date(2011, 1, 1), y: 0.63 },
        { x: new Date(2012, 1, 1), y: 0.69 },
        { x: new Date(2013, 1, 1), y: 0.70 },
        { x: new Date(2014, 1, 1), y: 0.70 },
        { x: new Date(2015, 1, 1), y: 0.71 },
        { x: new Date(2016, 1, 1), y: 0.72 },
        { x: new Date(2017, 1, 1), y: 0.73 },
        { x: new Date(2018, 1, 1), y: 0.83 },
        { x: new Date(2019, 1, 1), y: 0.84 },
        { x: new Date(2020, 1, 1), y: 0.85 },
        { x: new Date(2021, 1, 1), y: 0.86 },
        { x: new Date(2022, 1, 1), y: 0.88 },
        { x: new Date(2023, 1, 1), y: 0.87 },
        { x: new Date(2024, 1, 1), y: 0.86 },
        { x: new Date(2025, 1, 1), y: 0.89 },
      ]
    },
    {
      type: "line",
      showInLegend: true,
      name: "Avg Performance",
      lineDashType: "dash",
      yValueFormatString: "#,##",
      dataPoints: [
        { x: new Date(2011, 1, 1), y: 0.53 },
        { x: new Date(2012, 1, 1), y: 0.54 },
        { x: new Date(2013, 1, 1), y: 0.55 },
        { x: new Date(2014, 1, 1), y: 0.56 },
        { x: new Date(2015, 1, 1), y: 0.56 },
        { x: new Date(2016, 1, 1), y: 0.57 },
        { x: new Date(2017, 1, 1), y: 0.575 },
        { x: new Date(2018, 1, 1), y: 0.57 },
        { x: new Date(2019, 1, 1), y: 0.69 },
        { x: new Date(2020, 1, 1), y: 0.65 },
        { x: new Date(2021, 1, 1), y: 0.66 },
        { x: new Date(2022, 1, 1), y: 0.63 },
        { x: new Date(2023, 1, 1), y: 0.67 },
        { x: new Date(2024, 1, 1), y: 0.66 },
        { x: new Date(2025, 1, 1), y: 0.66 },
      ]
    }]
  };
  // @ts-ignore
  $("#chart_container").CanvasJSChart(options);
  $("#chart_container").css("height", "400px");
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

redo_task_saturation(TASKS_SATURATION);

let saturation_when_1 = "average_model";
let saturation_when_2 = "hum";

function refresh_saturation_when() { 
  $("#img_saturation_when").attr("src", `figures/mock_performance_${saturation_when_1}_${saturation_when_2}.svg`);

  // clone TASK_SATURATION
  let task_saturation = JSON.parse(JSON.stringify(TASKS_SATURATION));
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