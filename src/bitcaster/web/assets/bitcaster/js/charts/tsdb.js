import Chart from 'chart.js';

var color = Chart.helpers.color;

var chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

var tsConfig = {
    type: 'line',
    adapters: {
        date: {
            timezone: 'Europe/Rome'
        }
    },
    data: {
        datasets: [{
            label: 'Occurences',
            backgroundColor: color(chartColors.yellow).alpha(0.5).rgbString(),
            borderColor: chartColors.yellow,
            data: [],
            yAxisID: 'O',
        },
            {
                label: 'Notifications',
                backgroundColor: color(chartColors.green).alpha(0.5).rgbString(),
                borderColor: chartColors.green,
                data: [],
                yAxisID: 'N',
            },
            {
                label: 'Errors',
                backgroundColor: color(chartColors.red).alpha(0.5).rgbString(),
                borderColor: chartColors.red,
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

var bufferConfig = {
    type: 'horizontalBar',
    options: {
        aspectRatio: 3,
        responsive: true,
        legend: {
            display: false
         },
        scales: {
            xAxes: [{
                type: 'linear', ticks: {
                    min: 0
                }
            }], yAxes: []
        }
    },
    data: {
        labels: ['--'],
        datasets: [{
            backgroundColor: color(chartColors.red).alpha(0.5).rgbString(),
            // borderColor: chartColors.red,
            // borderWidth: 1,
            data: []
        }]
    }
};
var get = function (url) {
    return $.get(url).promise();
};

function updateChart(chart, urls) {
    $.when(get(urls[0]), get(urls[1]), get(urls[2])).done(function (d1, d2, d3) {
        chart.config.data.datasets[0].data = d1[0];
        chart.config.data.datasets[1].data = d2[0];
        chart.config.data.datasets[2].data = d3[0];
        chart.update();
        setTimeout(updateChart.bind(null, chart, urls), 60000);
    });
}
function updateQueue(chart, url) {
    $.when(get(url)).done(function (d1) {
        chart.config.data.datasets[0].data = [d1.value];
        chart.update();
        setTimeout(updateQueue.bind(null, chart, url), 60000);
    });
}
export function setupMainChart(id, urls) {
    var ctx = document.getElementById('ts').getContext('2d');
    var config = $.extend(true, {}, tsConfig);
    var chart = new Chart(ctx, config);
    updateChart(chart, urls);

}

export function setupOccurenceQueueChart(id, url) {
    var ctx = document.getElementById(id).getContext('2d');
    var config = $.extend(true, {}, bufferConfig);
    config.data.labels = ['Events'];
    config.data.datasets[0].backgroundColor = color(chartColors.yellow).alpha(0.5).rgbString();
    var chart1 = new Chart(ctx, config);
    updateQueue(chart1, url);
}

export function setupNotificationQueueChart(id, url) {
    var ctx = document.getElementById(id).getContext('2d');
    var config = $.extend(true, {}, bufferConfig);
    config.data.labels = ['Notifications'];
    config.data.datasets[0].backgroundColor = color(chartColors.green).alpha(0.5).rgbString();
    var chart1 = new Chart(ctx, config);
    updateQueue(chart1, url);

}

export {Chart}
