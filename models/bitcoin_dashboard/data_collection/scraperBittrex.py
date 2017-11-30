import sys
sys.path.append("..")

import datetime

from models.bitcoin_dashboard.data_collection.bittrex.bittrex import Bittrex
from cassandra.cluster import Cluster

from models.bitcoin_dashboard.data_collection.Create_CQL import *

"""
NOTE: The pip install of the Bittrex package will not work properly because it is designed for Python2. 
To fix this just copy the Bittrex folder to your lib/python/main_site-packages folder. 
"""

def getBittrexMarketSummary(session=None, CASSANDRA_DB=None):
    bittrex = Bittrex(None, None)
    market_summaries = bittrex.get_market_summaries()
    market_summaries = pd.DataFrame(market_summaries['result'])

    df2cassandra(market_summaries.apply(lambda x: x.astype(str).str.lower()), CASSANDRA_DB, "bittrex_market_summary", session=session)


if __name__ == "__main__":

    CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)

    session = cluster.connect(CASSANDRA_DB)
    bittrex = Bittrex(None, None)
    markets = bittrex.get_markets()
    markets = pd.DataFrame(markets['result'])
    currencies = bittrex.get_currencies()
    currencies = pd.DataFrame(currencies['result'])

    print("Updated Bittrex Data @ " + str(datetime.datetime.now()))
    getBittrexMarketSummary(session=session, CASSANDRA_DB=CASSANDRA_DB)