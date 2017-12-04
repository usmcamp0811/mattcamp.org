from flask import Flask, Blueprint, render_template, send_from_directory, jsonify
from flask_bootstrap import Bootstrap

import pandas as pd
import sys
sys.path.append("..")

from models.bitcoin_dashboard.data_collection.Create_CQL import *
from models.bitcoin_dashboard.data_analysis.dataRetrieval import *
from models.bitcoin_dashboard.data_analysis.dashboard import *
from datetime import datetime, timedelta
from flask_jsonpify import jsonpify
import json
from flask import Blueprint, render_template, session, request
from flask_socketio import emit
from flask_socketio import SocketIO, emit, join_room, leave_room, \
close_room, rooms, disconnect
from threading import Lock
import datetime
import time


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None
socketio = SocketIO(async_mode=async_mode)


thread = None
thread_lock = Lock()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)

        _time= datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        print('{}: Got Wallet Data'.format(_time))
        coinHistory = getCurrentWalletDF(session=None, db='cryptocoindb2', coin='bitcoin')
        coin_data =coinHistory.groupby(['name', 'CurrentPrice']).sum().reset_index()[
            ['name', 'CurrentPrice', 'CurrentWalletVallue', 'coins_transacted']]
        socketio.emit('my_response',
                      coin_data.to_dict('index')[0],
                      namespace='/coin')


@socketio.on('connect', namespace='/coin')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'name': 'BTC?',
                         'coins_transacted': 0.0,
                         'CurrentWalletVallue': 0.0,
                         'CurrentPrice': 0.0})

@socketio.on('get_balance', namespace='/coin')
def get_coin_price():

    coinHistory = getCurrentWalletDF(session=None, db='cryptocoindb2')
    coin_data = coinHistory.groupby(['name']).sum().reset_index()[
        ['name', 'CurrentPrice', 'CurrentWalletVallue', 'coins_transacted']]
    _time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    total_dollar = round(coin_data['CurrentWalletVallue'].sum(),2)
    money_in = coinHistory.groupby(['name']).sum().reset_index()['USD_In'].sum()
    net_profit = round(total_dollar - money_in, 2)

    print('{}: Got Balance'.format(_time))
    return socketio.emit('my_balance',
                  {'time': _time,
                   'blance_USD': total_dollar,
                   'net': net_profit,
                   },
                  namespace='/coin')
