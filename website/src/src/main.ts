import { DEVMODE } from "./globals"
import { DATA_SATURATION, fetch_data_saturation, getVectorizedDataSaturation } from "./data_connector"
import $ from 'jquery';
import bb, { line, scatter } from "billboard.js";
import "billboard.js/dist/billboard.css";
import { PCA } from "ml-pca";
import DataTable from 'datatables.net-dt';
import 'datatables.net-dt/css/dataTables.dataTables.min.css';

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
      },

    },
    // legend on the right
    legend: {
      position: "right"
    },
    color: {
      pattern: ["#e74c3c", "#27ae60"]
    }
  });
}


let dataTable: any = null;
let activeFilters = {
  saturation: null,
  task: null,
  access: null,
  global: null
};

function formatDataForDataTable(data_saturation) {
  let tableData = [];
  for (const [task, datasets] of Object.entries(data_saturation)) {
    for (const [dataset, dataset_dict] of Object.entries(datasets)) {
      tableData.push({
        dataset: dataset,
        task: task,
        saturation: dataset_dict["saturation"],
        year: dataset_dict["year"],
        access: dataset_dict["public"] ? "Public" : "Private",
        size: dataset_dict["size"]
      });
    }
  }
  return tableData;
}

function redo_task_saturation(data_saturation) {
  // Format data for DataTable
  const tableData = formatDataForDataTable(data_saturation);

  // Destroy existing DataTable if it exists
  if (dataTable) {
    dataTable.destroy();
  }

  // Initialize DataTable
  dataTable = new DataTable('#saturation_datatable', {
    data: tableData,
    columns: [
      {
        data: 'dataset',
        title: 'Dataset',
        render: function (data, type, row) {
          if (type === 'display') {
            return `<strong>${data}</strong>`;
          }
          return data;
        }
      },
      {
        data: 'task',
        title: 'Task',
        render: function (data, type, row) {
          if (type === 'display') {
            return `<span style="background-color: #ecf0f1; padding: 3px 8px; border-radius: 4px; font-size: 12px;">${data}</span>`;
          }
          return data;
        }
      },
      {
        data: 'saturation',
        title: 'Saturation',
        render: function (data, type, row) {
          if (type === 'display') {
            // Calculate color based on saturation
            let color = '';
            let bgColor = '';
            if (data > 0.9) {
              color = '#e74c3c';
              bgColor = 'rgba(231, 76, 60, 0.1)';
            } else if (data >= 0.7) {
              color = '#f39c12';
              bgColor = 'rgba(243, 156, 18, 0.1)';
            } else {
              color = '#27ae60';
              bgColor = 'rgba(39, 174, 96, 0.1)';
            }

            return `<div style="display: flex; align-items: center; justify-content: center;">
                      <div style="background-color: ${bgColor}; padding: 4px 12px; border-radius: 20px; border: 1px solid ${color};">
                        <span style="color: ${color}; font-weight: 600;">${data.toFixed(2)}</span>
                      </div>
                    </div>`;
          }
          return data;
        }
      },
      {
        data: 'year',
        title: 'Year',
        render: function (data, type, row) {
          if (type === 'display') {
            return `<span style="color: #7f8c8d;">${data}</span>`;
          }
          return data;
        }
      },
      {
        data: 'access',
        title: 'Access',
        render: function (data, type, row) {
          if (type === 'display') {
            return `<span>${data}</span>`;
          }
          return data;
        }
      },
      {
        data: 'size',
        title: 'Size',
        render: function (data, type, row) {
          if (type === 'display') {
            return `<div style="display: flex; align-items: center; justify-content: center;">
                      <div style="background-color: #ecf0f1; padding: 2px 10px; border-radius: 4px;">
                        <span style="font-weight: 500;">${data}</span>
                      </div>
                    </div>`;
          }
          return data;
        }
      }
    ],
    order: [[2, 'desc']], // Sort by saturation descending
    pageLength: 10,
    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]],
    dom: '<"top"f>rt<"bottom-controls"lip><"clear">',
    language: {
      search: "Global filter:"
    },
    initComplete: function () {
      // Add select filters for Task and Access columns
      this.api().columns([1, 4]).every(function () {
        const column = this;
        const columnName = column.index() === 1 ? 'task' : 'access';
        const select = $('<select><option value="">All</option></select>')
          .appendTo($(column.header()))
          .on('change', function () {
            const val = $(this).val();
            column.search(val ? '^' + val + '$' : '', true, false).draw();

            // Update active filters
            if (val) {
              activeFilters[columnName] = val;
            } else {
              activeFilters[columnName] = null;
            }
            updateFilterDisplay();
          })
          .on('click', function (e) {
            e.stopPropagation();
          });

        column.data().unique().sort().each(function (d, j) {
          select.append('<option value="' + d + '">' + d + '</option>');
        });
      });

      // Check if buttons already exist
      if ($('#filter-controls .filter-buttons').length > 0) {
        return; // Buttons already added, don't add them again
      }

      // Move buttons to filter control area
      const filterButtons = $('<div class="filter-buttons"></div>');

      // Create saturation filter buttons
      const saturationButtons = [
        { text: 'High Saturation (>0.9)', class: 'saturation-filter-btn', filter: 'high' },
        { text: 'Medium Saturation (0.7-0.9)', class: 'saturation-filter-btn', filter: 'medium' },
        { text: 'Low Saturation (<0.7)', class: 'saturation-filter-btn', filter: 'low' }
      ];

      saturationButtons.forEach(btn => {
        $(`<button class="filter-btn ${btn.class}" data-filter="${btn.filter}">${btn.text}</button>`)
          .appendTo(filterButtons)
          .on('click', function () {
            $('.saturation-filter-btn').removeClass('active');
            $(this).addClass('active');

            $.fn.dataTable.ext.search.pop();
            if (btn.filter === 'high') {
              $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                return parseFloat(data[2]) > 0.9;
              });
              activeFilters.saturation = 'High (>0.9)';
            } else if (btn.filter === 'medium') {
              $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                const sat = parseFloat(data[2]);
                return sat >= 0.7 && sat <= 0.9;
              });
              activeFilters.saturation = 'Medium (0.7-0.9)';
            } else {
              $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                return parseFloat(data[2]) < 0.7;
              });
              activeFilters.saturation = 'Low (<0.7)';
            }

            updateFilterDisplay();
            dataTable.draw();
          });
      });

      $(`<button class="filter-btn clear-filter-btn">Clear All Filters</button>`)
        .appendTo(filterButtons)
        .on('click', function () {
          $.fn.dataTable.ext.search = [];
          dataTable.search('').columns().search('').draw();
          $('#saturation_datatable thead select').val('');
          $('.saturation-filter-btn').removeClass('active');
          activeFilters = { saturation: null, task: null, access: null, global: null };
          updateFilterDisplay();
        });

      $('#filter-controls').append(filterButtons);

      // Add filter display area
      $('<div id="active-filters" style="display: none;"></div>')
        .insertAfter('#filter-controls');

      // Track global search filter
      $(document).on('keyup', '.dt-search input.dt-input', function () {
        const val = $(this).val() as string;
        if (val && val.trim() !== '') {
          activeFilters.global = val;
        } else {
          activeFilters.global = null;
        }
        updateFilterDisplay();
      });

      // Add placeholder to search input
      $('.dt-search input.dt-input').attr('placeholder', 'Search datasets...');
    }
  });

  // Add click handler for rows
  $('#saturation_datatable tbody').on('click', 'tr', function () {
    const data = dataTable.row(this).data();
    fake_year_saturation(`${data.task} / ${data.dataset}`, data.saturation);

    // Highlight selected row
    $('#saturation_datatable tbody tr').removeClass('selected');
    $(this).addClass('selected');
  });

  // Generate initial PCA visualization
  updatePCAVisualization(data_saturation);

  // Update PCA when DataTable is redrawn (filtered/sorted)
  dataTable.on('draw', function () {
    updatePCAFromDataTable();
  });
}

let pcaChart: any = null;

function updateFilterDisplay() {
  const filterDisplay = $('#active-filters');
  const filters = [];

  if (activeFilters.global) {
    filters.push(`
      <div class="filter-tag">
        <span class="filter-icon">🔍</span>
        <span class="filter-label">Search:</span>
        <span class="filter-value">"${activeFilters.global}"</span>
        <button class="filter-remove" onclick="clearGlobalFilter()">×</button>
      </div>
    `);
  }
  if (activeFilters.saturation) {
    const icon = activeFilters.saturation.includes('High') ? '🔴' :
      activeFilters.saturation.includes('Medium') ? '🟡' : '🟢';
    filters.push(`
      <div class="filter-tag">
        <span class="filter-icon">${icon}</span>
        <span class="filter-label">Saturation:</span>
        <span class="filter-value">${activeFilters.saturation}</span>
        <button class="filter-remove" onclick="clearSaturationFilter()">×</button>
      </div>
    `);
  }
  if (activeFilters.task) {
    filters.push(`
      <div class="filter-tag">
        <span class="filter-icon">📊</span>
        <span class="filter-label">Task:</span>
        <span class="filter-value">${activeFilters.task}</span>
        <button class="filter-remove" onclick="clearTaskFilter()">×</button>
      </div>
    `);
  }
  if (activeFilters.access) {
    const icon = activeFilters.access === 'Public' ? '🌐' : '🔒';
    filters.push(`
      <div class="filter-tag">
        <span class="filter-icon">${icon}</span>
        <span class="filter-label">Access:</span>
        <span class="filter-value">${activeFilters.access}</span>
        <button class="filter-remove" onclick="clearAccessFilter()">×</button>
      </div>
    `);
  }

  if (filters.length > 0) {
    filterDisplay.html(`
      <div class="filters-header">
        <span class="filters-title">Active Filters (${filters.length})</span>
        <button class="clear-all-filters-btn" onclick="clearAllFilters()">Clear All</button>
      </div>
      <div class="filters-list">${filters.join('')}</div>
    `);
    filterDisplay.show();
  } else {
    filterDisplay.hide();
  }
}

function updatePCAFromDataTable() {
  // Get currently visible rows from DataTable
  const visibleData = dataTable.rows({ search: 'applied' }).data().toArray();

  // Reconstruct data_saturation structure from visible rows
  const filteredDataSaturation = {};
  visibleData.forEach(row => {
    if (!filteredDataSaturation[row.task]) {
      filteredDataSaturation[row.task] = {};
    }
    filteredDataSaturation[row.task][row.dataset] = {
      saturation: row.saturation,
      year: row.year,
      public: row.access === "Public",
      size: row.size
    };
  });

  updatePCAVisualization(filteredDataSaturation);
}

function updatePCAVisualization(data_saturation) {
  let data_saturation_vec = getVectorizedDataSaturation(data_saturation);

  // Need at least 2 data points for PCA
  if (data_saturation_vec.length < 2) {
    $('#cluster_chart_container').html('<p style="text-align: center; color: #666;">Not enough data points for PCA visualization (need at least 2)</p>');
    return;
  }

  const pca = new PCA(data_saturation_vec.map(d => d.vector));
  let data_saturation_new = pca.predict(data_saturation_vec.map(d => d.vector)).to2DArray();

  // Destroy existing chart if it exists
  if (pcaChart) {
    pcaChart.destroy();
  }

  pcaChart = bb.generate({
    bindto: "#cluster_chart_container",
    size: {
      width: 750,
    },
    data: {
      type: scatter(),
      xs: {
        dataset: "dataset_x",
      },
      columns: [
        // take first two dimensions
        ["dataset_x", ...data_saturation_new.map(d => d[0])],
        ["dataset", ...data_saturation_new.map(d => d[1])],
      ],
      onclick: function (d) {
        const data_point = data_saturation_vec[d.index];
        fake_year_saturation(`${data_point.task} / ${data_point.name}`, data_point.saturation)
      },
    },
    tooltip: {
      contents: function (d) {
        const data_point = data_saturation_vec[d[0].index];
        return `<span class="pca_tooltip">${data_point.task} / ${data_point.name}<span>`;
      }
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
    color: {
      pattern: ["#e74c3c"]
    },
    legend: {
      // position: "right"
      show: false,
    },
    title: {
      text: `PCA Visualization (${data_saturation_vec.length} datasets)`
    }
  })
}

let saturation_when_1 = "average_model";
let saturation_when_2 = "hum";

function refresh_saturation_when() {
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
  // Add visual feedback
  $('.saturation-definition').css('background-color', '#e3f2fd');
  setTimeout(() => {
    $('.saturation-definition').css('background-color', 'white');
  }, 300);
})

$("#select_saturation_when_2").on("change", function () {
  saturation_when_2 = $(this).val() as string;
  refresh_saturation_when();
  // Add visual feedback
  $('.saturation-definition').css('background-color', '#e3f2fd');
  setTimeout(() => {
    $('.saturation-definition').css('background-color', 'white');
  }, 300);
})

async function main() {
    const loader = document.getElementById('loader');
    const content = document.getElementById('content');

    // Show loader and hide content
    loader.style.display = 'block';
    content.style.display = 'none';

    await fetch_data_saturation();

    // Hide loader and show content
    loader.style.display = 'none';
    content.style.display = 'block';

    $("#select_saturation_when_1").trigger("change");
    $("#select_saturation_when_2").trigger("change");
}

main();

// Global filter clear functions
(window as any).clearGlobalFilter = function () {
  $('.dt-search input.dt-input').val('').trigger('keyup');
  dataTable.search('').draw();
};

(window as any).clearSaturationFilter = function () {
  $('.saturation-filter-btn').removeClass('active');
  $.fn.dataTable.ext.search = [];
  activeFilters.saturation = null;
  updateFilterDisplay();
  dataTable.draw();
};

(window as any).clearTaskFilter = function () {
  $('#saturation_datatable thead select').eq(0).val('').trigger('change');
};

(window as any).clearAccessFilter = function () {
  $('#saturation_datatable thead select').eq(1).val('').trigger('change');
};

(window as any).clearAllFilters = function () {
  $('.clear-filter-btn').click();
};