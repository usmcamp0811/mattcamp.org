from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View
import pandas as pd
import sys
sys.path.append("..")
import flask
from flask import request, Blueprint
import pip
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from models.bitcoin_dashboard.data_collection.Create_CQL import *
from models.bitcoin_dashboard.data_analysis.dataRetrieval import *
from models.bitcoin_dashboard.data_analysis.dashboard import *
from bokeh.layouts import layout
from bokeh.embed import components

bitcoin_project = Blueprint('bitcoin_project',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='')

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