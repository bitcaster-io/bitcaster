var color = Chart.helpers.color;

var commonConfig = {
    type: 'line',
    adapters: {
        date: {
            timezone: 'Europe/Rome'
        }
    },
    data: {
        datasets: [{
            label: 'Occurences',
            backgroundColor: color(window.chartColors.yellow).alpha(0.5).rgbString(),
            borderColor: window.chartColors.yellow,
            data: [],
            yAxisID: 'O',
        },
            {
                label: 'Notifications',
                backgroundColor: color(window.chartColors.green).alpha(0.5).rgbString(),
                borderColor: window.chartColors.green,
                data: [],
                yAxisID: 'N',
            },
            {
                label: 'Errors',
                backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
                borderColor: window.chartColors.red,
                data: [],
            }]
    },
    options: {
        scales: {
            xAxes: [{
                type: 'time',
                time: {
                    parser: function (dt) {
                        return moment(dt).local()
                    },
                    displayFormats: {
                        day: 'HH:mm',
                        hour: 'HH:mm',
                        minute: 'HH:mm',
                    }
                },
                distribution: 'series',
                ticks: {
                    autoSkip: true
                }
            }],
            yAxes: [{
                id: 'O',
                type: 'linear',
                ticks: {
                    min: 0
                },
                position: 'left',
                beginAtZero: true,
            },
                {
                    id: 'N',
                    type: 'linear',
                    ticks: {
                        min: 0
                    },
                    position: 'right',
                    beginAtZero: true,
                }]
        },
        tooltips: {
            intersect: false,
            mode: 'index',
            callbacks: {
                label: function (tooltipItem, myData) {
                    var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                    if (label) {
                        label += ': ';
                    }
                    label += parseFloat(tooltipItem.value).toFixed(2);
                    return label;
                }
            }
        }
    }
};
var get = function (url) {
    return $.get(url).promise();
};
var updateChart = function (chart, urls) {
    $.when(get(urls[0]), get(urls[1]), get(urls[2])).done(function (d1, d2, d3) {
        chart.config.data.datasets[0].data = d1[0];
        chart.config.data.datasets[1].data = d2[0];
        chart.config.data.datasets[2].data = d3[0];
        chart.update();
        setTimeout(updateChart, 60000);
    });
};
