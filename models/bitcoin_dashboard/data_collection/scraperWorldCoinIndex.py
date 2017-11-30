import sys
sys.path.append("..")
import datetime
import time

import requests
from cassandra.cluster import Cluster

from models.bitcoin_dashboard.data_collection.Create_CQL import *

'''
This is the script to be run as a daemon to scrape bitcoin data and load it into Cassandra
'''

def getWCI(session=None, CASSANDRA_DB=None):

    url = "https://www.worldcoinindex.com/apiservice/json?key=xQaM9kDbRnv2vXqc6hJjFAsV9"
    request = requests.get(url)
    if request.status_code == 200:
        wci = request.json()
        wci = pd.DataFrame(wci['Markets'])
        wci['date'] = pd.to_datetime(wci['Timestamp'], unit='s').dt.date
        wci['date'] = wci['date'].astype(str)
        wci['Timestamp'] = wci['Timestamp'] * 1000

        str_cols = [col for col in wci.columns if wci[col].dtypes == 'O']
        wci[str_cols] = wci[str_cols].apply(lambda x: x.astype(str).str.lower())
        # print(wci.to_string())
        df2cassandra(wci, "cryptocoindb2", "worldcoinindex", session=session)
    else:
        print("None 200 Status Code Returned: {}".format(request.status_code))
        #TODO: Write error logger
        pass



if __name__ == "__main__":

    while True:

        CASSANDRA_HOST = ['192.168.0.106', '192.168.0.101']
        CASSANDRA_DB = "cryptocoindb2"
        cluster = Cluster(CASSANDRA_HOST)

        session = cluster.connect()

        print("Getting WorldCoinIndex Data @ " + str(datetime.datetime.now()))

        getWCI(session=session, CASSANDRA_DB=CASSANDRA_DB)

        print("Done")
        time.sleep(300)
