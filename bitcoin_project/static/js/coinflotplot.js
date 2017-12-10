//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready", coin_list);
    var wallet = [];
    //AJAX Get data stuff
    // I need to make multiple AJAX functions so I can get one for each coin. Myabe use Jinja to template this..
    for(var i=0; i<coin_list.length; i++){
        console.log(coin_list[i]);
            $.ajax({
              url: coin_list[i],
              dataType: 'json',
              async: false,
          success: function(data) {
            wallet.push(data)
          }
        });
    }





console.log(wallet);


var minY = d3.min(wallet, function(w) { return d3.min(w.price_data, function(p) { return p.price_usd; }); });
var maxY = d3.max(wallet, function(w) { return d3.max(w.price_data, function(p) { return p.price_usd; }); });
var minX = d3.min(wallet, function(w) { return d3.min(w.price_data, function(p) { return p.timestamp; }); });
var maxX = d3.max(wallet, function(w) { return d3.max(w.price_data, function(p) { return p.timestamp; }); });



var plotObjs = [];

// take N coins in list wallet and turn them in to things that flot plot can plot.
for(var i=0;  i<wallet.length; i++) {
    //create variables for the plot object
    var coin_plotobj = {};
    var coin_data = [[]];
    coin_plotobj['label'] = wallet[i].coinname;
    // coin_plotobj['color'] = 'blue';
    var current_coin = wallet[i];
    // convert the price data into a multidimensional array
    for (key in current_coin.price_data) {
        coin_data.push([current_coin.price_data[key].timestamp, current_coin.price_data[key].price_usd]);
        coin_plotobj['data'] =coin_data;
    };
    //add object to the things to plot
    plotObjs.push(coin_plotobj);
};



console.log('OUTSIDE LOOP', plotObjs);

console.log('MinX', minX, 'MinY', minY, 'MaxX', maxX, 'MaxY', maxY);


//    actual plot stuff
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
            min: (minY),
            max: (maxY)
        },
        xaxis: {
            mode: "time",
            TickSize: [2, "hour"],
            min: minX,
            max: maxX,
        },
        tooltip: true,
        tooltipOpts: {
            content: "'%s' of %x is %y.4",
        }
    };
    var plotObj2 = $.plot($("#flot-line-chart"), plotObjs, options);
    }
});