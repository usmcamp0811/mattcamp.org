from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap

import pandas as pd
import sys
sys.path.append("..")
import flask
from flask import request, Blueprint, url_for
import pip
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from models.bitcoin_dashboard.data_collection.Create_CQL import *
from models.bitcoin_dashboard.data_analysis.dataRetrieval import *
from models.bitcoin_dashboard.data_analysis.dashboard import *
from bokeh.layouts import layout
from bokeh.embed import components
from datetime import datetime, timedelta
from flask_jsonpify import jsonpify
import json
from flask_socketio import emit
from bitcoin_project.api import socketio

bitcoin_project = Blueprint('bitcoin_project',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='')

@bitcoin_project.route('/bitcoin_project/<path:filename>')
def base_static(filename):
    return send_from_directory(bitcoin_project.root_path + '/../bitcoin_project/static', filename)

@bitcoin_project.route('/projects/bitcoin_dashboard')
def dashboard():

    CASSANDRA_HOST = ['192.168.0.101', '192.168.0.106']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)

    session.row_factory = pandas_factory
    session.default_fetch_size = None

    ndays = request.args.get('ndays', default = 7, type = int)
    print(ndays)
    tblGainLoss, tblDailyGainLoss, coinHistory, tblCoins = getAllData(ndays, session=session)
    # tblGainLoss, tblCoins, coinHistory = getSomeValueFromA_Database()
    # Grab the inputs arguments from the URL
    # args = flask.request.args
    l = layout([[[[GainLossPlot(tblGainLoss)], [MarketPlot(tblCoins, coinHistory)]], WalletPlot(coinHistory)]],
               repsonsive=True)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(l)

    html = flask.render_template(
        'old_dashboard.html',
        title="BitCoin Dashboard",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        active_page='projects',
        footer='false'
    )
    return encode_utf8(html)

@bitcoin_project.route('/projects/api/coins_price_usd/<coinname>/FROM<dateFrom>TO<dateTo>')
def coin_price(coinname, dateFrom, dateTo):
    """
    Gets the price of a coin over a span of time.
    :return:
    """
    print(dateFrom)
    dt_today = datetime.today()
    dt_yesterday = datetime.today() - timedelta(days=1)
    # coinname = request.args.get('coinname', default='bitcoin', type=str)
    # dateTo = request.args.get('dateTo', default=dt_today.strftime('%Y-%m-%d'), type=str)
    # dateFrom = request.args.get('dateFrom', default=dt_yesterday.strftime('%Y-%m-%d'), type=str)

    coinPrices = getCoinPrices(coinname=coinname, dateFrom=dateFrom, dateTo=dateTo, session=None, debug=True)
    print('Coin: {} From: {} To: {}'.format(coinname, dateFrom, dateTo))
    coinPrices['timestamp'] = coinPrices['timestamp'].astype(np.int64)// 10**6
    coinPrices = coinPrices.sort_values('timestamp')
    coinPrices = coinPrices.to_dict(orient='records')
    data = jsonify(price_data=coinPrices, coinname=coinname)
    return data

def chunks(iterable, chunk_size):
  i = 0;
  while i < len(iterable):
    yield iterable[i:i+chunk_size]
    i += chunk_size

@bitcoin_project.route('/projects/coin_explorer')
def coin_explorer():
    current_wallet = getCurrentWalletDF(session=None, db='cryptocoindb2', coin=None)
    dates_list = datesFromTo(DatesFrom='2017-12-07', DatesTo='2017-12-10')
    chunks = np.array_split(dates_list, len(dates_list)//2)
    coinsowned = set(current_wallet.name)
    coinsowned = list(set([coin.lower() for coin in coinsowned]))
    coin_list = []
    for chunk in chunks:
        for coin in coinsowned:
            coin_list.append('/projects/api/coins_price_usd/{}/FROM{}TO{}'.format(coin.lower(), chunk[0], chunk[1]))

    html = render_template('coin_explorer.html',
                           coin_list=coinsowned,
                           coin_paths=coin_list,
                           active_page='projects')
    return html

@bitcoin_project.route('/projects/api/current_price/')
def coin_api():
    """
    An api for getting my current coin data
    :return:
    """

    html = render_template('coin_socket.html', async_mode=socketio.async_mode)
    return html

# @bitcoin_project.route('/projects/api/<coin_name>')
# def coin_price_history(coin_name):
