//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready", coin_list);
    var wallet;
    var plotObjs = [];
    var coins = [];
    var coinname;
    var coindata;
    console.log('Coin List:', coin_list);
    console.log('Coin Paths:', coin_paths);
    for(var c=0; c<coin_list.length; c++){
        var dummy_coindata = [{'Timestamp':[], 'PriceData':[]}];
        coinname = coin_list[c];
        coindata = {'CoinPlotData': dummy_coindata,
                           'label': coinname};
        coins[c] = coindata;

    }

    var index;

    //What the data structure needs to look like:
    // {CoinName:
    //      {CoinPlotData:[{Timestamp:123456, PriceData:100332},
    //                     {Timestamp:678901, PriceData:1002},
    //                      ...],
    //       label:'CoinName'}
    // }
    //
    //AJAX Get data stuff
    // I need to make multiple AJAX functions so I can get one for each coin. Myabe use Jinja to template this..
    for(var i=0; i<coin_list.length; i++){

            $.ajax({
                url: coin_paths[i],
                dataType: 'json',
                async: false,
                success: function(data) {
                    console.log('getting coin_data', data.coinname)
                    var coin_data = [];
                    // get the data from the json in a array form called coin_data
                    for (key in data.price_data) {
                        console.log('Putting data at', index, 'for coin ', data.coinname);
                        index = coins.findIndex( x => x.label==data.coinname);
                        coins[index].CoinPlotData.push(data.price_data[key]);
                    };

                }

        });

    }


var minY = d3.min(coins, function(c) { return d3.min(c.CoinPlotData, function(dpd) { return dpd.price_usd; }); });
var maxY = d3.max(coins, function(c) { return d3.max(c.CoinPlotData, function(dpd) { return dpd.price_usd; }); });
var minX = d3.min(coins, function(c) { return d3.min(c.CoinPlotData, function(dpd) { return dpd.timestamp; }); });
var maxX = d3.max(coins, function(c) { return d3.max(c.CoinPlotData, function(dpd) { return dpd.timestamp; }); });

console.log('MinX', minX, 'MinY', minY, 'MaxX', maxX, 'MaxY', maxY);
console.log('With some luck this worked!', coins);




for(var c=0; c<coins.length; c++){
    var label_to_plot = coins[c].label;
    var data_to_plot = [[]];
    for(key in coins[c].CoinPlotData) {
        data_to_plot.push([coins[c].CoinPlotData[key].timestamp,
                          (coins[c].CoinPlotData[key].price_usd)]);
    };
    plotObjs.push({'label': label_to_plot,
                    'data': data_to_plot})
};
console.log('Plot Data', plotObjs);
plot();
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
