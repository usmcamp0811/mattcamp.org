import sys
sys.path.append("..")
import datetime
# from tqdm import tqdm
import time

import pandas as pd
import requests
from cassandra.cluster import Cluster

from data_collection.Create_CQL import *


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

def updateCoinList():
    CASSANDRA_HOST = ['192.168.0.101']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)

    coinlist = "https://www.cryptocompare.com/api/data/coinlist/"
    r = requests.get(coinlist).json()
    coinlist = pd.DataFrame(r["Data"]).T
    coinlist.FullyPremined = pd.to_numeric(coinlist.FullyPremined, errors='coerce')
    coinlist.Id = pd.to_numeric(coinlist.Id, errors='coerce')
    coinlist.PreMinedValue = pd.to_numeric(coinlist.PreMinedValue, errors='coerce')
    coinlist.SortOrder = pd.to_numeric(coinlist.SortOrder, errors='coerce')
    coinlist.Id = pd.to_numeric(coinlist.Id, errors='coerce')
    coinlist.TotalCoinSupply = pd.to_numeric(coinlist.TotalCoinSupply, errors='coerce')
    coinlist.TotalCoinsFreeFloat = pd.to_numeric(coinlist.TotalCoinsFreeFloat, errors='coerce')
    coinlist.TotalCoinsMined = pd.to_numeric(coinlist.TotalCoinsMined, errors='coerce')
    df2cassandra(coinlist, CASSANDRA_DB, "coinlist", session=session)
    print("Done.")


def getCoinPrices(coins, currency="USD"):
    '''
    :param coins: a list of coins to get prices for
    :param currency: a string representing the currency to compare all coins to
    '''

    stop = 20
    # print("Starting", end="")
    for start in tqdm(range(0, len(coins), 20)):
        stop = start + 20
        coin = ','.join(coins[start:stop])
        url = "https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}".format(currency, coin)
        r = requests.get(url).json()
        t = time.time()
        price = pd.Series(r).tolist()
        timestamp = pd.Series([t for x in range(len(r))])
        coin = pd.Series(r).index
        curr = pd.Series([currency for x in range(len(r))])
        dfPrice = pd.DataFrame({'Coin': coin, 'Price': price, 'Timestamp': timestamp, 'Currency': curr})
        df2cassandra(dfPrice, CASSANDRA_DB, "tblprice", session=session)
        time.sleep(100)
        # print(">", end="")
    print("||Done...")

def getCoinSnapshot(coin):
    try:
        if coin == "BTC":
            coin2 = "USD"
        else:
            coin2 = "USD"
        url = "https://www.cryptocompare.com/api/data/coinsnapshot/?fsym={}&tsym={}".format(coin,coin2)
        r = requests.get(url).json()
        t = time.time()
        Exchanges = pd.DataFrame(r['Data']['Exchanges'])
        AggregatedData = pd.DataFrame(r['Data']['AggregatedData'], index=[0])
        timestamp = pd.Series([t for x in range(Exchanges.shape[0])])
        Exchanges['TIMESTAMP'] = timestamp
        AggregatedData['TIMESTAMP'] = t
        AggregatedData['Algorithm'] = r['Data']['Algorithm']
        AggregatedData['ProofType'] = r['Data']['ProofType']
        AggregatedData['BlockNumber'] = r['Data']['BlockNumber']
        AggregatedData['NetHashesPerSecond'] = r['Data']['NetHashesPerSecond']
        AggregatedData['TotalCoinsMined'] = r['Data']['TotalCoinsMined']
        AggregatedData['BlockReward'] = r['Data']['BlockReward']

        df2cassandra(Exchanges, CASSANDRA_DB, "exchanges", session=session)
        df2cassandra(AggregatedData, CASSANDRA_DB, "aggregated_data", session=session)

    except:
        print("Error! Saving to Log Table...", end=" ")
        error_log = pd.DataFrame({'Message': r['Message'],
              'Response': r['Response'],
              'Type': r['Type'],
              'Timestamp': t,
              'Coin': coin},
             index=[0])
        df2cassandra(error_log, CASSANDRA_DB, "snapshot_error_log", session=session)





if __name__ == "__main__":

    CASSANDRA_HOST = ['192.168.0.106']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb"
    CASSANDRA_TABLE = "coinlist"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)

    session.row_factory = pandas_factory
    session.default_fetch_size = None

    # Get all the coin names
    query = "SELECT name FROM {}.{};".format(CASSANDRA_DB, CASSANDRA_TABLE)

    rslt = session.execute(query, timeout=None)
    coins = rslt._current_rows
    coins = coins.name.tolist()

    while True:
        print("Getting Coin Snapshot Data @ " + str(datetime.datetime.now()))
        for coin in coins:
            print(coin, end=" ")
            getCoinSnapshot(coin)

            print("Done!")
            time.sleep(10)
