//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready", data_path);

    //AJAX Get data stuff
    // I need to make multiple AJAX functions so I can get one for each coin. Myabe use Jinja to template this..

    var plot_data = {"X":[],"Y":[]};

    $.ajax({
      url: data_path,
      dataType: 'json',
      async: false,
  success: function(data) {
    plot_data = data
  }
});


var yaxis = {"Min":d3.min(plot_data, function(d) { return d.Y; }),
             "Max":d3.max(plot_data, function(d) { return d.Y; })};
var xaxis = {"Min":d3.min(plot_data, function(d) { return d.X; }),
             "Max":d3.max(plot_data, function(d) { return d.X; })};

var data_to_plot = [[]];

for(key in plot_data)
    data_to_plot.push([plot_data[key].X, plot_data[key].Y]);


//    actual plot stuff
plot()
function plot() {

    var options = {
        series: {
            lines: {
                show: true
            },
            points: {
                show: true
            }
        },
        grid: {
            hoverable: true //IMPORTANT! this is needed for tooltip to work
        },
        yaxis: {
            min: (yaxis.Min) - (50), // Just giving some room above and below the sinwave
            max: (yaxis.Max) + (50)
        },
        xaxis: {
            min: xaxis.Min,
            max: xaxis.Max
        },
        tooltip: true,
        tooltipOpts: {
            content: "'%s' of %x.1 is %y.4",
        }
    };
    var plotObj = $.plot($("#flot-line-chart"), [{
            data: data_to_plot,
            label: "A sinwave made in Python."
        }],
        options);
}
});
