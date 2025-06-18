import { DEVMODE } from "./globals"

let saturation_when_1 = "average_model";
let saturation_when_2 = "hum";

function refresh_saturation_when() { 
  $("#img_saturation_when").attr("src", `figures/mock_performance_${saturation_when_1}_${saturation_when_2}.svg`);
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