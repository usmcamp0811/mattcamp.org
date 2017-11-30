import sys
sys.path.append("..")
import datetime
# from tqdm import tqdm
import time

import pandas as pd
import requests
from cassandra.cluster import Cluster

from models.bitcoin_dashboard.data_collection.Create_CQL import *


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def UpdatetCoinList(session=None, CASSANDRA_DB=None, output=False):
    #TODO: Find another source.. this API is currently donw.. 09-18-2017
    request = requests.get('http://api.cryptocoincharts.info/listCoins')
    if request.status_code == 200:
        coinlist = request.json()
        coinlist = pd.DataFrame(coinlist)
        coinlist['price_btc'] = pd.to_numeric(coinlist['price_btc'], errors='coerce')
        coinlist['volume_btc'] = pd.to_numeric(coinlist['volume_btc'], errors='coerce')
        # fixing DOGE coins leading space problem..
        coinlist['id'] = coinlist['id'].str.lstrip()
        coinlist['name'] = coinlist['name'].str.lstrip()
        t = time.time()
        timestamp = pd.Series([t for x in range(coinlist.shape[0])])
        coinlist['timestamp'] = timestamp
        coinlist['date'] = pd.to_datetime(coinlist['timestamp'], unit='s').dt.date
        coinlist['date'] = coinlist['date'].astype(str)
        # some reason they have a blank id in the first record! argh!!
        str_cols = [col for col in coinlist.columns if coinlist[col].dtypes == 'O']
        coinlist[str_cols] = coinlist[str_cols].apply(lambda x: x.astype(str).str.lower())

        df2cassandra(coinlist, CASSANDRA_DB, "coinlist_cccharts", session=session)
        if output:
            return coinlist.sort_values('volume_btc', ascending=False)
        print(coinlist['id'])
    else:
        #TODO: Write error logger
        print("None 200 Status Code Returned: {}".format(request.status_code))
        print("Getting Coinlist from Local DB...")

        session.row_factory = pandas_factory
        session.default_fetch_size = None

        query = "SELECT * FROM {}.{} LIMIT 10000;".format(CASSANDRA_DB, "coinlist_cccharts")

        rslt = session.execute(query, timeout=None)
        coinlist = rslt._current_rows
        if output:
            return coinlist.sort_values('volume_btc', ascending=False)


def getMultiTradingPairs(session=None, CASSANDRA_DB=None, coins=None, output=False):
    post_fields = {'pairs': coins}
    request = requests.post("http://api.cryptocoincharts.info/tradingPairs/", data=post_fields)
    if request.status_code == 200:
        tradingPairs = pd.DataFrame(request.json())
        t = time.time()
        timestamp = pd.Series([t for x in range(tradingPairs.shape[0])])
        tradingPairs['timestamp'] = timestamp
        tfcoins = [x.split('/') for x in tradingPairs['id'].tolist()]
        coin1 = []
        coin2 = []
        for x in tfcoins:
            coin1.append(x[0])
            coin2.append(x[1])

        tradingPairs['coin1a'] = coin1
        tradingPairs['coin2a'] = coin2
        tradingPairs['date'] = pd.to_datetime(tradingPairs['timestamp'], unit='s').dt.date
        tradingPairs['date'] = tradingPairs['date'].astype(str)
        tradingPairs['timestamp'] = tradingPairs['timestamp'].astype(int) * 1000
        tradingPairs['price'] = tradingPairs['price'].astype(float)
        tradingPairs['price_before_24h'] = tradingPairs['price_before_24h'].astype(float)
        tradingPairs['volume_btc'] = tradingPairs['volume_btc'].astype(float)
        tradingPairs['volume_first'] = tradingPairs['volume_first'].astype(float)
        tradingPairs['volume_second'] = tradingPairs['volume_second'].astype(float)

        str_cols = [col for col in tradingPairs.columns if tradingPairs[col].dtypes == 'O']
        tradingPairs[str_cols] = tradingPairs[str_cols].apply(lambda x: x.astype(str).str.lower())

        df2cassandra(tradingPairs, CASSANDRA_DB, "traiding_pairs", session=session)
        if output:
            return tradingPairs
    else:
        #TODO: Write error logger
        print("None 200 Status Code Returned: {}".format(request.status_code))
        pass


if __name__ == "__main__":

    CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb2"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)

    session.row_factory = pandas_factory
    session.default_fetch_size = None

    while True:

        # Calculate API calls per hour to keep under 60/hr threshold.
        hourStart = time.time()
        hourStop = hourStart + 3600
        hourCounter = 0

        while time.time() < hourStop:

            coinlist = UpdatetCoinList(session=session, CASSANDRA_DB=CASSANDRA_DB, output=True)
            print("Updated Coinlist Data @ " + str(datetime.datetime.now()))
            hourCounter += 1
            # time.sleep(75)

            while hourCounter < 60:

                coins = coinlist.id.tolist()

                coin_pairs = []
                tcoins = []
                for tcoin in coins:
                    if len(tcoin) < 1:
                        pass
                    else:
                        tcoins.append(tcoin)
                        for fcoin in coinlist.id.tolist()[1:20]:
                            if fcoin in tcoins:
                                pass
                            coin_pairs.append(fcoin + "_" + tcoin.lstrip())
                top20coins = ",".join(coin_pairs)

                tradingPairs = getMultiTradingPairs(session=session, CASSANDRA_DB=CASSANDRA_DB, coins=top20coins, output=True)

                print("Updated Trading Pairs Data @ " + str(datetime.datetime.now()))
                print("There were {} pairs saved.".format(tradingPairs.shape[0]))
                if tradingPairs.shape[0] == 10:
                    print(set(tradingPairs.id))
                hourCounter += 1
                time.sleep(75)

                print("API Calles this hour: {}".format(hourCounter))

        if hourStop-time.time() > 0:
            print("API Calls are used up...Waiting...{} seconds till starting again.".format(hourStop-time.time()))
            time.sleep(hourStop-time.time())


