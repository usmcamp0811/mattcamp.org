//Flot Line Chart from JSON servred by Flask
$(document).ready(function() {
    console.log("document ready", coin_list);
    var wallet;
    var plotObjs = [];
    var coins = {};
    var coinname;
    for(var c=0; c<coin_list.length; c++){
        coins[coin_list[c]] = [[]];
    }

    //AJAX Get data stuff
    // I need to make multiple AJAX functions so I can get one for each coin. Myabe use Jinja to template this..
    for(var i=0; i<coin_list.length; i++){
        // var minY = d3.min(wallet, function(w) { return d3.min(w.price_data, function(p) { return p.price_usd; }); });
        // var maxY = d3.max(wallet, function(w) { return d3.max(w.price_data, function(p) { return p.price_usd; }); });
        // var minX = d3.min(wallet, function(w) { return d3.min(w.price_data, function(p) { return p.timestamp; }); });
        // var maxX = d3.max(wallet, function(w) { return d3.max(w.price_data, function(p) { return p.timestamp; }); });


            $.ajax({
                url: coin_paths[i],
                dataType: 'json',
                async: false,
                success: function(data) {

                    var coin_data = [[]];
                    // get the data from the json in a array form called coin_data
                    for (key in data.price_data) {
                        coin_data.push([data.price_data[key].timestamp, data.price_data[key].price_usd]);
                    };
                    // save coin data to an object with a key of the name
                    coins[data.coinname].push(coin_data);
                    // wallet[data.coinname].push(data);
                }

        });

    }


console.log(coins);


function onDataReceived() {

        console.log('THIS IS THE WALLET', wallet);
        // console.log(wallet.length);
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
                coin_plotobj['data'] = coin_data;
            };
            //add object to the things to plot
            // console.log('COIN OBJ:', coin_plotobj.data, coin_plotobj.label);

        };
            // console.log('A LABEL?', coin_plotobj['label']);
            plotObjs.push(coin_plotobj);
            console.log('Things to plot now:', plotObjs);
        plot()

    }

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