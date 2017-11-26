//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready");
    var x = [];
    $.ajax({
      url: data_path,
      dataType: 'json',
      async: false,
  success: function(data) {
    x = data

  }
});
    plot();
    console.log(x);
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
                min: 0,
                max: 60
            },
            xaxis: {
                min: 0,
                max: 1024
            },
            tooltip: true,
            tooltipOpts: {
                content: "'%s' of %x.1 is %y.4",
            }
        };
        var plotObj = $.plot($("#flot-line-chart"), [{
                data: x,
                label: "Some sin wave made in Python."
            }],
            options);
    }
});