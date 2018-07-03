
var chart_length = 50;

function weather_addpoint(series,point){
  var chart = $('#w-chart').highcharts();
  var length = chart.series[series].data.length;
  chart.series[series].addPoint(point,true,length > chart_length);
}

function control_addpoint(series,point){
  var chart = $('#c-chart').highcharts();
  var length = chart.series[series].data.length;
  chart.series[series].addPoint(point,true,length > chart_length);
}

function output_addpoint(series, point){
  var chart = $('#o-chart').highcharts();
  var length = chart.series[series].data.length;
  chart.series[series].addPoint(point,true,length > chart_length);
}

Highcharts.chart('w-chart', {
    chart: {
        zoomType: 'xy'
    },
    title: {
        text: null
    },
    subtitle: {
        text: null
    },
    credits: {
      enabled: false
    },
    plotOptions: {
       line: {
         marker: {
           enabled: false
         }
       }
    },
    xAxis: [{
        crosshair: true,
        labels: {
          style: {
            fontSize: '8px'
          }
        }
    }],
    yAxis: [{ // Primary yAxis
        gridLineWidth: 2,
        //1.12,1.552
        min: 1.1, max: 1.6,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#8A8AD6',
                fontSize: '8px'
            }
        },
        visible: true
    }, { // Secondary yAxis
        gridLineWidth: 0,
        min: 0, max: 360,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#EEB058',
                fontSize: '8px'
            }
        },
        visible: true
    }, { // Tertiary yAxis
        gridLineWidth: 0,
        min: 0, max: 30,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[1]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#FE6672',
                fontSize: '8px'
            }
        },
        visible: true,
        opposite:true
    }],
    tooltip: {
        shared: true,
        valueDecimals: 2
    },
    legend: {
        itemStyle: {
          //fontWeight: 'bold',
          fontSize: '8px'
        },
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'top',
        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
    },
    series: [{
        name: 'Air Density',
        type: 'line',
        color: '#8A8AD6',
        data: [],
        yAxis: 0,
        tooltip: {
            valueSuffix: ' kg/m^3'
        }
    },{
        name: 'Wind Direction',
        type: 'line',
        color: '#EEB058',
        data: [],
        yAxis: 1,
        tooltip: {
            valueSuffix: ' Degrees'
        }
    }, {
        name: 'Wind Speed',
        type: 'line',
        color: '#FE6672',
        data: [],
        yAxis: 2,
        tooltip: {
            valueSuffix: ' m/s'
        }
    }]
});


Highcharts.chart('c-chart', {
    chart: {
        zoomType: 'xy'
    },
    title: {
        text: null
    },
    subtitle: {
        text: null
    },
    credits: {
      enabled: false
    },
    plotOptions: {
       line: {
         marker: {
           enabled: false
         }
       }
    },
    xAxis: [{
        crosshair: true,
        labels: {
          style: {
            fontSize: '8px'
          }
        }
    }],
    yAxis: [{ // Primary yAxis
        gridLineWidth: 2,
        min: 0, max: 360,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#FE6672',
                fontSize: '8px'
            }
        },
        visible: true
    }, { // Secondary yAxis
        gridLineWidth: 0,
        min: -5, max: 6,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#00BBDE',
                fontSize: '8px'
            }
        },
        visible: true
    }],
    tooltip: {
        shared: true,
        valueDecimals: 2
    },
    legend: {
        itemStyle: {
          //fontWeight: 'bold',
          fontSize: '8px'
        },
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'top',
        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
    },
    series: [{
        name: 'Turbine Yaw',
        type: 'line',
        color: '#FE6672',
        data: [],
        yAxis: 0,
        tooltip: {
            valueSuffix: ' Degrees'
        }
    },{
        name: 'Blade Pitch',
        type: 'line',
        color: '#00BBDE',
        data: [],
        yAxis: 1,
        tooltip: {
            valueSuffix: ' Degrees'
        }
    }]
});



Highcharts.chart('o-chart', {
    chart: {
        zoomType: 'xy'
    },
    title: {
        text: null
    },
    subtitle: {
        text: null
    },
    credits: {
      enabled: false
    },
    plotOptions: {
       line: {
         marker: {
           enabled: false
         }
       }
    },
    xAxis: [{
        crosshair: true,
        labels: {
          style: {
            fontSize: '8px'
          }
        }
    }],
    yAxis: [{ // Primary yAxis
        type: 'logarithmic',
        //minorTickInterval: 0.1,
        gridLineWidth: 2,
        min: 1, max: 10000000,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            //format: '{value}',
            style: {
                color: '#57B566',
                fontSize: '8px'
            }
        },
        visible: true
    }, { // Secondary yAxis
        gridLineWidth: 0,
        min: 0, max: 24,
        title: {
            text: null,
            style: {
                color: Highcharts.getOptions().colors[0]
            }
        },
        labels: {
            format: '{value}',
            style: {
                color: '#87E096',
                fontSize: '8px'
            }
        },
        visible: true
    }],
    tooltip: {
        shared: true,
        valueDecimals: 2
    },
    legend: {
        itemStyle: {
          //fontWeight: 'bold',
          fontSize: '8px'
        },
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'top',
        backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
    },
    series: [{
        name: 'Power',
        type: 'line',
        color: '#57B566',
        data: [],
        pointStart: 1,
        yAxis: 0,
        tooltip: {
            valueSuffix: ' Watts'
        }
    },{
        name: 'RPM',
        type: 'line',
        color: '#87E096',
        data: [],
        yAxis: 1,
        tooltip: {
            valueSuffix: ' RPM'
        }
    }]
});
