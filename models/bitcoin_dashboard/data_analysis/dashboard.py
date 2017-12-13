import sys
sys.path.append("..")
from models.bitcoin_dashboard.data_analysis.dataRetrieval import *
# from GainsLossPlot import getCurrentWalletDF
from bokeh.plotting import figure
# from bokeh.io import push_notebook, show, output_notebook
from bokeh.palettes import Category20
from bokeh.models import LassoSelectTool, WheelZoomTool, Span, \
    ColumnDataSource, HoverTool, Label

colorDict = {'aragon': '#1f77b4',
             'bitcoin': '#aec7e8',
             'civic': '#ff7f0e',
             'dash': '#ffbb78',
             'eos': '#2ca02c',
             'ethereum': '#98df8a',
             'gnosis': '#d62728',
             'litecoin': '#ff9896',
             'decred': '#1CC726',
	         'omisego': '#77267d',
             'bitcoincash': '#8191A2',
             'monero': '#77d637'}


def dt2ut(dt):
    epoch = pd.to_datetime('1970-01-01')
    return (dt - epoch).total_seconds()

def getAllData(ndays=7, session=None):
    """
    :param ndays: numbers of days back in time from now to get data
    :return:
    """
    if session == None:
        CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
        CASSANDRA_PORT = 9042
        CASSANDRA_DB = "cryptocoindb2"

        cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
        session = cluster.connect(CASSANDRA_DB)
        session.row_factory = pandas_factory
        session.default_fetch_size = None


    coinHistory = getCurrentWalletDF(session=session)

    str_cols = [col for col in coinHistory.columns if coinHistory[col].dtypes == 'O']
    coinHistory[str_cols] = coinHistory[str_cols].apply(lambda x: x.astype(str).str.lower())

    coinHistory['transaction_time'] = pd.to_datetime(coinHistory['transaction_time'])

    coinlist = list2String(set(coinHistory['name']))

    # makes a list of dates from the oldest purchase to todays date
    datelist = datesFromTo(DatesFrom=coinHistory.transaction_date.min())
    datelist = list2String(datelist[-ndays:]) #only get last 7 days
    # random_limit = np.random.randint(1000, size=1)[0]
    where = "date IN ({}) AND name IN ({})".format(datelist, coinlist)
    try:
        where = "date IN ({}) AND name IN ({})".format(datelist, coinlist)
        tblCoins = simpleSelectCQL("worldcoinindex", where=where)
    except:
        print('It likely timed out so lets try again with fewer days...')
        where = "date IN ({}) AND name IN ({})".format(datelist[:int(len(datelist)/2)], coinlist)
        tblCoins = simpleSelectCQL("worldcoinindex", where=where)
    tblCoins['PriceDelta'] = tblCoins.apply(
        lambda row: getMyCoinDeltas(row['name'], row['price_usd'], row['timestamp'], coinHistory), axis=1)

    tblGainLoss = tblCoins.groupby(['timestamp'])['PriceDelta'].sum().reset_index()
    tblDailyGainLoss = tblCoins.groupby(['name', 'date'])['PriceDelta'].sum().reset_index()
    return tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins

def getGainLossData():
    coinHistory = getCurrentWalletDF()
    coinlist = list2String(set(coinHistory['Name']))

    # makes a list of dates from the oldest purchase to todays date
    datelist = datesFromTo(DatesFrom=coinHistory.TransactionDate.min())
    datelist = list2String(datelist)

    where = "date IN ({}) AND name IN ({}) LIMIT 1000".format(datelist, coinlist)
    tblCoins = simpleSelectCQL("worldcoinindex", where=where)
    tblCoins['PriceDelta'] = tblCoins.apply(
        lambda row: getMyCoinDeltas(row['name'], row['price_usd'], row['timestamp'], coinHistory), axis=1)
    tblGainLoss = tblCoins.groupby(['timestamp'])['PriceDelta'].sum().reset_index()
    return tblGainLoss

def GainLossPlot(tblGainLoss):
    tblGainLoss['strDate'] = tblGainLoss['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    tblGainLoss['pp_PriceDelta'] = tblGainLoss['PriceDelta'].round(2).astype(str)
    gain_source = ColumnDataSource(tblGainLoss[tblGainLoss['PriceDelta'] < 0])
    loss_source = ColumnDataSource(tblGainLoss[tblGainLoss['PriceDelta'] >= 0])
    gnl_source = ColumnDataSource(tblGainLoss)

    hover = HoverTool(
        tooltips=[
            ( 'Date:',   '@strDate'            ),
            ( 'Net Gain/Loss:',  '$@pp_PriceDelta' ), # use @{ } for field names with spaces
        ],

        formatters={
            'Date:'      : 'datetime',
        },

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline',
        names=['line', 'buy']
    )


    tools = [hover, WheelZoomTool(), 'box_zoom', 'pan', LassoSelectTool()]
    gain_loss_plot = figure(x_axis_type="datetime", title="Net Performance Accross All Owned CryptoCurrencies",
                            y_range=(0, 6000), plot_width=1000, plot_height=400, tools=tools)

    gain_loss_plot.grid.grid_line_alpha=0.2
    gain_loss_plot.xaxis.axis_label = 'Date'
    gain_loss_plot.yaxis.axis_label = 'Net Gain/Loss (USD)'
    gain_loss_plot.line('timestamp', 'PriceDelta', color='darkgrey', alpha=0.3, name="line", source=gnl_source)
    gain_loss_plot.circle('timestamp', 'PriceDelta', size=4, legend='Gains',
              color='black', alpha=0.6, source=loss_source)
    gain_loss_plot.circle('timestamp', 'PriceDelta', size=4, legend='Losses',
              color='darkred', alpha=0.6, source=gain_source)
    zero= Span(location=0,dimension='width', line_color='grey',
                                line_dash='solid', line_width=0.5, name='buy')


    gain_loss_plot.add_layout(zero)
    gain_loss_plot.legend.location = "top_left"
    return gain_loss_plot

def MarketPlot(tblCoins, coinHistory):
    hover2 = HoverTool(
        tooltips=[
            ( 'Coin:',  '@name' ),
            ( 'Date:',   '@strDate'            ),
            ( 'Price:',  '$@strPrice_USD' ), # use @{ } for field names with spaces
        ],

        formatters={
            'Date:'      : 'datetime',
        },
    )

    tools = [hover2, WheelZoomTool(), 'box_zoom', 'pan', LassoSelectTool()]

    market_plot = figure(x_axis_type="datetime", title="Performance of the Coins I Own", plot_width=1000, plot_height=400,
                         y_range=(0, 22000), tools=tools)
    market_plot.grid.grid_line_alpha=0.2
    market_plot.xaxis.axis_label = "Date"
    market_plot.yaxis.axis_label = "Price (USD)"

    coins = list(set(coinHistory.name))
    numCoins = len(coins)

    tblCoins = tblCoins.sort_values('timestamp')
    tblCoins['strDate'] = tblCoins['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    tblCoins['strPrice_USD'] = tblCoins['price_usd'].round(2).astype(str)

    datasourceCoins = dict()
    for i, coin in zip(range(numCoins), coins):
        datasourceCoins[i] = ColumnDataSource(tblCoins[tblCoins['name'] == coin])
        market_plot.line('timestamp', 'price_usd', color=colorDict[coin], alpha=1, legend=coin, source=datasourceCoins[i])

    dates = list(set(coinHistory['transaction_time']))

    Purchase = dict()
    for d in dates:

        Purchase[d] = Span(location=dt2ut(d)*1000,
                                dimension='height', line_color='green',
                                line_dash='dashed', line_width=1)
        market_plot.add_layout(Purchase[d])

    market_plot.legend.location ="top_center"
    market_plot.legend.orientation = "horizontal"



    return market_plot

def WalletPlot(coinHistory):
    coinHistory['PercentCoin'] = coinHistory['coins_transacted'] / coinHistory['coins_transacted'].sum()
    coinHistory['PercentUSD_Purchase'] = coinHistory['price_at_transaction'] /  coinHistory['price_at_transaction'].sum()
    coinHistory['PercentUSD_Current'] = coinHistory['CurrentPrice'] /  coinHistory['CurrentPrice'].sum()
    coinHistory['NetGainLoss'] = coinHistory['CurrentWalletVallue'] - coinHistory['USD_In']


    currentValue = coinHistory.sort_values('NetGainLoss').groupby('name').sum()
    coinName = []
    coinPriceStart = []
    coinPriceStop = []
    coinNet = []
    coinCurrent = []
    colors = []
    amount = []
    previousCoin = 0

    coins = list(set(coinHistory.name))
    numCoins = len(coins)
    for coin, price, net, amt, color in zip(currentValue.index,
                                           currentValue.CurrentWalletVallue,
                                           currentValue.NetGainLoss,
                                           currentValue.coins_transacted,
                                           Category20[numCoins]):
        coinName.append(coin)
        coinPriceStart.append(previousCoin)
        coinPriceStop.append(previousCoin+price)
        colors.append(color)
        coinNet.append(net)
        amount.append(amt)
        coinCurrent.append(price)
        previousCoin += price

    percent_gainloss = []


    colors = [] # yea i know I'll fix it
    for c in coinName:
        colors.append(colorDict[c])

    # do some rounding and convert to string to make things look better.
    pp_coinCurrent = [str(float("{:.2f}".format(X))) for X in coinCurrent]
    pp_coinNet = [str(float("{:.2f}".format(X))) for X in coinNet]
    pp_amount = [str(float("{:.5f}".format(X))) for X in amount]

    totalDollars = { 'Coin': coinName,
                     'PriceStart': coinPriceStart,
                     'PriceStop': coinPriceStop,
                     'Color': colors,
                     'Net': coinNet,
                     'Amount': amount,
                     'Current': coinCurrent,
                     'pp_Net': pp_coinNet,
                     'pp_Amount': pp_amount,
                     'pp_Current': pp_coinCurrent,
                     'Position': [0 for x in range(len(coinName))]}

    hover = HoverTool(
        tooltips=[
            ( 'Coin:',   '@Coin'            ),
            ( 'Amount Owned:', '@pp_Amount'),
            ( 'Current Value (USD):',   '$@pp_Current'            ),
            ( 'Net Gain/Loss:',  '$@pp_Net' )
        ],
    )
    source = ColumnDataSource(data=totalDollars)

    total_balance = int(coinHistory['CurrentWalletVallue'].sum())
    coinBar = figure(plot_width=200, plot_height=800, tools=[hover], y_range=(0, total_balance + 500),toolbar_location=None)


    coinBar.vbar(x='Position', width=0.5, bottom='PriceStart',
           top='PriceStop', color='Color', source=source)
    money_invested = Span(location=coinHistory['USD_In'].sum(),
         dimension='width', line_color='black',
         line_dash='dashed', line_width=3)

    money_inValue = '$' + str(float("{:.2f}".format(coinHistory['USD_In'].sum())))
    cValue = '$' + str(float("{:.2f}".format(coinHistory['CurrentWalletVallue'].sum())))

    # money_inValueText = Label(x=0.25, y=coinHistory['USD_In'].sum() , x_units='screen', text=money_inValue, render_mode='css',
    #   border_line_color='black', border_line_alpha=0.0,
    #   background_fill_color='white', background_fill_alpha=0.0)

    currentValueText = Label(x=50, y=coinHistory['CurrentWalletVallue'].sum() , x_units='screen', text=cValue, render_mode='css',
      border_line_color='black', border_line_alpha=0.0,
      background_fill_color='white', background_fill_alpha=0.0)

    coinBar.add_layout(money_invested)
    coinBar.add_layout(currentValueText)
    # coinBar.add_layout(money_inValueText)
    coinBar.xaxis.visible = False
    coinBar.yaxis.visible = False
    coinBar.xgrid.grid_line_color = None
    coinBar.ygrid.grid_line_color = None

    return coinBar


if __name__ == "__main__":
    def pandas_factory(colnames, rows):
        return pd.DataFrame(rows, columns=colnames)


    CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb2"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)
    session.row_factory = pandas_factory
    session.default_fetch_size = None

    tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins = getAllData(1, session)
    print(tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins)