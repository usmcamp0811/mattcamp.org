//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready", data_path);

    //AJAX Get data stuff
    // I need to make multiple AJAX functions so I can get one for each coin. Myabe use Jinja to template this..

    var plot_data1;
    var plot_data2;

    $.ajax({
      url: data_path2a,
      dataType: 'json',
      async: false,
  success: function(data) {
    plot_data1 = data
  }
});

    $.ajax({
      url: data_path2b,
      dataType: 'json',
      async: false,
  success: function(data) {
    plot_data2 = data
  }
});

console.log('This is what it looks like from Ajax:', plot_data1);
var both_data = [plot_data1,plot_data2];

var minY = d3.min(both_data, function(pd) { return d3.min(pd.DataTest, function(dt) { return dt.Y; }); });
var maxY = d3.max(both_data, function(pd) { return d3.max(pd.DataTest, function(dt) { return dt.Y; }); });
var minX = d3.min(both_data, function(pd) { return d3.min(pd.DataTest, function(dt) { return dt.X; }); });
var maxX = d3.max(both_data, function(pd) { return d3.max(pd.DataTest, function(dt) { return dt.X; }); });
console.log(both_data.DataTest);

var data_to_plot1 = [[]];
var data_to_plot2 = [[]];

for(key in plot_data1.DataTest)
    data_to_plot1.push([plot_data1.DataTest[key].X, plot_data1.DataTest[key].Y]);

for(key in plot_data2.DataTest)
    data_to_plot2.push([plot_data2.DataTest[key].X, plot_data2.DataTest[key].Y]);


console.log('MinX', minX, 'MinY', minY, 'MaxX', maxX, 'MaxY', maxY);

console.log(both_data);
//    actual plot stuff

var plotObs = [{
            data: data_to_plot1,
            label: plot_data1.label,
            color: 'blue'
        },
        {
            data: data_to_plot2,
            label: plot_data2.label,
            color: 'red'
        }];
console.log('I need my other thing to look like this!', plotObs);
plot2()
function plot2() {

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
            min: (minY) - (50), // Just giving some room above and below the sinwave
            max: (maxY) + (50)
        },
        xaxis: {
            min: minX,
            max: maxX
        },
        tooltip: true,
        tooltipOpts: {
            content: "'%s' of %x.1 is %y.4",
        }
    };
    var plotObj2 = $.plot($("#flot-line-chart2"), plotObs, options);
    }
});



