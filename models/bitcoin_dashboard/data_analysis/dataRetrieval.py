import sys
sys.path.append("..")
import pandas as pd
import numpy as np
from cassandra.query import SimpleStatement
from cassandra.cluster import Cluster
from models.bitcoin_dashboard.data_collection.Create_CQL import *
import time
from datetime import datetime, timedelta
import time

def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
CASSANDRA_PORT = 9042
CASSANDRA_DB = "cryptocoindb2"

cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
session = cluster.connect(CASSANDRA_DB)
session.row_factory = pandas_factory
session.default_fetch_size = None

def getCoinPrices(coinname=None, dateFrom=None, dateTo=None, session=None, debug=False):
    """
    Function to return a single coins prices between a set of dates.
    :param coinname: String value of the coin name in the format of WCI's API
    :param dateFrom: string date in the format 2017-08-01
    :param dateTo: string date in the format 2017-08-01
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

    if dateTo == None:
        dates = datesFromTo(DatesFrom=dateFrom, DatesTo=datetime.today())
    else:
        dates = datesFromTo(DatesFrom=dateFrom, DatesTo=dateTo)

    dates = list2String(dates)
    CASSANDRA_DB = "cryptocoindb2"
    CASSANDRA_TABLE = "worldcoinindex"

    qryCoins = """SELECT price_usd, timestamp FROM  {}.{} 
                  WHERE date in ({})
                  AND name = '{}';""".format(CASSANDRA_DB,CASSANDRA_TABLE, dates, coinname)

    if debug:
        print(qryCoins)
    rslt = session.execute(qryCoins, timeout=None)
    tblCoinPrices = rslt._current_rows
    return tblCoinPrices


def getUSDPriceWCI(coinname=None, date=None):
    """
    Gets the average pricer of a coin on a given date.
    Used to get purchase price of my intiial coins I bought prior to be tracking that metric.
    :param coinname: String value of the coin name in the format of WCI's API
    :param date: string date in the format 2017-08-01
    :return: a list to be made into columns of a dataframe with the appropriate data
    """
    purchaseDate = date
    date = date
    coinname = coinname.lower()
    CASSANDRA_DB = "cryptocoindb2"
    CASSANDRA_TABLE = "worldcoinindex"
    qryCoins = """SELECT price_usd, timestamp FROM  {}.{} 
                  WHERE date = '{}'
                  AND name = '{}';""".format(CASSANDRA_DB,CASSANDRA_TABLE, date, coinname)

    rslt = session.execute(qryCoins, timeout=None)
    tblCoins = rslt._current_rows
    if date == datetime.now().strftime('%Y-%m-%d'):
        print("Can't get a price for this coin.")
        return coinname, -999
    if tblCoins.shape[0] == 0:
        nextDay = date
        nextDay = datetime.strptime(nextDay, '%Y-%m-%d').date()+timedelta(days=1)
        nextDay = nextDay.strftime('%Y-%m-%d')
        return getUSDPriceWCI(coinname=coinname, date=nextDay)
    return [coinname, date, tblCoins.price_usd.mean()]

def getBitCoinPriceCC(coinname=None, date=None):
    # DEPRECATE WARNING: Will remove in the future at some time.. think this is a bad function.. maybe?
    # needs better documentation at the very least!
    date = date
    coinname = coinname.lower()
    CASSANDRA_DB = "cryptocoindb2"
    CASSANDRA_TABLE = "coinlist_cccharts"
    qryCoins = """SELECT price_btc, timestamp FROM  {}.{} 
                  WHERE date = '{}'
                  AND id = '{}';""".format(CASSANDRA_DB,CASSANDRA_TABLE, date, coinname)
    rslt = session.execute(qryCoins, timeout=None)
    tblCoins = rslt._current_rows
    if date == datetime.now().strftime('%Y-%m-%d'):
        print(date)
        print("Can't get a price for this coin.")
        return coinname, -999
    if tblCoins.shape[0] == 0:
        nextDay = date
        nextDay = datetime.strptime(nextDay, '%Y-%m-%d').date()+timedelta(days=1)
        nextDay = nextDay.strftime('%Y-%m-%d')
        return getBitCoinPriceCC(coinname=coinname, date=nextDay)
    return [coinname, tblCoins.price_btc.mean(), date]

def getMyCoinDeltas(strName=None, floatPriceNow=None, dateTime=None, dfCoinHistory=None):
    """
    Gets the difference in price between when the coin was purchased and the market prices at a point in time.
    Then it calculates the weighted values for the individual coin if theres mutlitple purchases on different days
    FIFO
    :param strName: String value in the format of WCI' API
    :param floatPriceNow: Float value for the point in time being evaluated
    :param dfCoinHistory: My DF of coin purchases
    :return:
    """
    #TODO: Ensure this can handle if/when I sell bitcoins/altcoins

    dfTransactions = dfCoinHistory[dfCoinHistory['name'] == strName.lower()] # fileters out just that coins data
    if dfTransactions.shape[0] == 0:
        print('You do not own that coin.')
        return None
    else:
        coinValue = 0.0
        for purchasePrice, purchaseAmt, purchaseTime in zip(dfTransactions.price_at_transaction, dfTransactions.coins_transacted, dfTransactions.transaction_time):
            if purchaseTime < dateTime:
                priceDelta = floatPriceNow - purchasePrice
                coinValue += priceDelta * purchaseAmt

        return coinValue

def getCurrentPrice(strName=None):
    strName = strName.lower()
    # shitty hack to fix LiteCoin's case change in the data... I need to migrate the data to another table with all lower case
    strCurrentDate = datetime.utcnow().strftime('%Y-%m-%d')
    CASSANDRA_DB = "cryptocoindb2"
    CASSANDRA_TABLE = "worldcoinindex"
    qryCoins = """SELECT * 
                  FROM {}.{}
                  WHERE date='{}' AND name='{}' LIMIT 1;""".format(CASSANDRA_DB, CASSANDRA_TABLE, strCurrentDate, strName)

    # print(qryCoins)
    rslt = session.execute(qryCoins, timeout=None)
    tblCoins = rslt._current_rows
    # print(tblCoins.shape[0])
    if tblCoins.shape[0] != 1:
        print('getCurrentPrice({}): Error'.format(strName))
        print('Either more than one record was returned or we could not find that coin in the DB.')
        return 0
    else:
        price = tblCoins['price_usd'].loc[0]
        return price

def simpleSelectCQL(CASSANDRA_TABLE, CASSANDRA_DB=CASSANDRA_DB,fields='*', where=None, limit=None):
    """
    A function to make writting CQL SELECT statments more Pythonic
    :param CASSANDRA_TABLE: String value, The table where the data is located
    :param CASSANDRA_DB: String value, The Keyspace
    :param fields: String value containing comma sperated field names
    :param where: String value containing the criteria for a where statement
    :param limit: String or Int value containing the limit number
            ALSO put ALLOW FILTERING at end in String format if needed
            Example: limit='10 ALLOW FILTERING'
    :return: Pandas DataFrame containing queried results
    """
    if where != None:
        WHERE = 'WHERE '
    else:
        WHERE = ''
        where = ''

    if limit != None:
        LIMIT = 'LIMIT '
    else:
        LIMIT = ''
        limit = ''

    query = """SELECT {} FROM  {}.{} 
                  {}{}
                  {}{};""".format(fields, CASSANDRA_DB, CASSANDRA_TABLE, WHERE, where, LIMIT, limit)
    try:
        rslt = session.execute(query, timeout=None)
        table = rslt._current_rows
        return table
    except Exception as e:
        print(query)
        print('\n\n', e)
        raise IOError

def list2String(list):
    return "'"+"', '".join(list)+"'"

def datesFromTo(DatesFrom=None, DatesTo=datetime.today()):
    """
    Provides a date range for filtering coin queries
    :param DatesFrom: String  Datetime value, of the oldest date to get records in format 2017-09-20
    :param DatesTo: String or Datetime value of the most recent record to get in format 2017-09-20
    :return: list of dates between the given periods.
    """
    if type(DatesTo) != datetime:
        DatesTo = datetime.strptime(DatesTo, '%Y-%m-%d')
    if type(DatesFrom) != datetime:
        DatesFrom = datetime.strptime(DatesFrom, '%Y-%m-%d')
    datelist = []
    timeDelta = DatesFrom - DatesTo
    for i in range(abs(timeDelta.days) + 1):
        date = DatesFrom  + timedelta(days=i)
        datelist.append(date.strftime('%Y-%m-%d'))
    return datelist

def getCurrentWalletDF(session=None, db='cryptocoindb2', coin=None):
    """
    Function get all the transaction history for a given coin or all coins owned. Then it gets the current price and
    calculates the ROI etc..
    :param session: the Cassandra Session
    :param db: the DB the data is in..
    :param coin: the coin name if none it will get all
    :return: a dataframe with coin data
    """

    if session == None:
        CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
        CASSANDRA_PORT = 9042

        cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
        session = cluster.connect(db)
        session.row_factory = pandas_factory
        session.default_fetch_size = None

    if coin:
        coinHistory = "SELECT * FROM {}.transactions WHERE name='{}' ALLOW FILTERING;".format(db,coin) # I know I should restructure the table but its not gonna be big.. yet.. sorry future self
    else:
        coinHistory = "SELECT * FROM {}.transactions;".format(db)
    rslt = session.execute(coinHistory, timeout=None)
    coinHistory = rslt._current_rows

    coinHistory['USD_In'] = coinHistory['price_at_transaction'] * coinHistory['coins_transacted'] #wallet value at purchase
    coinHistory['CurrentPrice'] = coinHistory.apply(lambda row: getCurrentPrice(row['name']), axis=1)
    coinHistory['CurrentWalletVallue'] = coinHistory['CurrentPrice'] * coinHistory['coins_transacted']
    # my times are in -5 GMT/ CST time so just adjusting to put all in a common timezone. really should just make everything UTC but ehh.. later
    coinHistory['transaction_time'] = pd.to_datetime(coinHistory['transaction_time']) + pd.Timedelta('6 hours')

    return coinHistory

# def getPriceDelta(strName=None, floatPriceNow=None, dateTime=None, floatLastPrice=None):

# TODO: Create function/query to get data faster.
"""
Maybe only get data for every hour back N days that way the number of records queried is several magnitudes less. 
Then create a function to stream the data in between the hours till some percentage is filled in. 
This could help with load speeds
"""


if __name__ == "__main__":

    print(getCurrentPrice(strName='bitcoin'))