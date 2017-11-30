import sys
sys.path.append("..")
from models.bitcoin_dashboard.data_collection.scraperCryptoCoinCharts import *
from models.bitcoin_dashboard.data_collection.scraperCryptoCompare import *
from models.bitcoin_dashboard.data_collection.scraperWorldCoinIndex import *
from models.bitcoin_dashboard.data_collection.scraperBittrex import *
import os, sys
# from daemonize import Daemonize

# Get all the coin names
# query = "SELECT name FROM {}.{};".format(CASSANDRA_DB, "coinlist_cccharts")
#
# rslt = session.execute(query, timeout=None)
# coinlist = rslt._current_rows
# coinlist = coinlist.id.tolist()

def getCoinData():

    CASSANDRA_HOST = ['192.168.0.101', '192.168.0.114', '192.168.0.106']
    CASSANDRA_PORT = 9042
    CASSANDRA_DB = "cryptocoindb2"

    cluster = Cluster(contact_points=CASSANDRA_HOST, port=CASSANDRA_PORT)
    session = cluster.connect(CASSANDRA_DB)

    session.row_factory = pandas_factory
    session.default_fetch_size = None

    # query = "SELECT id FROM {}.{} LIMIT 10000;".format(CASSANDRA_DB, "coinlist_cccharts")
    #
    # rslt = session.execute(query, timeout=None)
    # coinlist = rslt._current_rows
    # coinlist = coinlist.id.tolist()

    while True:
        # log = open('scrapeLog', 'w')
        try:
            # Calculate API calls per hour to keep under 60/hr threshold.
            hourStart = time.time()
            hourStop = hourStart + 3600
            hourCounter = 0

            while time.time() < hourStop:

                # print("Getting Coin Snapshot Data @ " + str(datetime.datetime.now()))
                # for coin in cscoins:
                #     print(coin, end=" ")
                #     getCoinSnapshot(coin)
                #
                #     print("Done!")

                    # time.sleep(5)

                while hourCounter < 60:

                    # TODO: Currently Broken 09-18-2017
                    if hourCounter == 0:
                        coinlist = UpdatetCoinList(session=session, CASSANDRA_DB=CASSANDRA_DB, output=True)
                        # log.write("\nUpdated Coinlist Data @ " + str(datetime.datetime.now()))
                        print("Updated Coinlist Data @ " + str(datetime.datetime.now()))
                        hourCounter += 1


                    # log.write("\nGetting WorldCoinIndex Data @ " + str(datetime.datetime.now()))
                    print("Getting WorldCoinIndex Data @ " + str(datetime.datetime.now()))

                    getWCI(session=session, CASSANDRA_DB=CASSANDRA_DB)

                    coins = coinlist

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

                    tradingPairs = getMultiTradingPairs(session=session, CASSANDRA_DB=CASSANDRA_DB, coins=top20coins,
                                                        output=True)

                    print("Updated Trading Pairs Data @ " + str(datetime.datetime.now()))
                    # log.write("\nUpdated Trading Pairs Data @ " + str(datetime.datetime.now()))
                    # print("There were {} pairs saved.".format(tradingPairs.shape[0]))

                    # if tradingPairs.shape[0] == 10:
                        # print(set(tradingPairs.id))

                    print("Updated Bittrex Data @ " + str(datetime.datetime.now()))
                    # log.write("\nUpdated Bittrex Data @ " + str(datetime.datetime.now()))
                    getBittrexMarketSummary(session=session, CASSANDRA_DB=CASSANDRA_DB)

                    hourCounter += 1
                    time.sleep(60)

                    print("API Calles this hour: {}".format(hourCounter))

            if hourStop - time.time() > 0:
                print("API Calls are used up...Waiting...{} seconds till starting again.".format(hourStop - time.time()))
                # log.write("\nAPI Calls are used up...Waiting...{} seconds till starting again.".format(hourStop - time.time()))
                time.sleep(hourStop - time.time())
        except Exception as e:
            print("There has been an error.. probably exceeded the max calls on the API... waiting 30 mins and trying again.")
            print("Error:", e)
            # log.write("\nThere has been an error.. probably exceeded the max calls on the API... waiting 30 mins and trying again.")
            # log.write("\nError:" + str(e))
            time.sleep(1800)
            getCoinData()

        # log.close()

if __name__ == "__main__":
    # myname = os.path.basename(sys.argv[0])
    # pidfile = '/tmp/%s' % myname  # any name
    # daemon = Daemonize(app=myname, pid=pidfile, action=getCoinData)
    # daemon.start()
    getCoinData()