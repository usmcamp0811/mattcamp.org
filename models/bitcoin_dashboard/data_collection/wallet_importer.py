import pandas as pd
import os
from datetime import datetime

def import_exodus_wallet(exodus_wallet_dir=None):
    """
    Imports the csv files exported from Exodus wallet
    :param exodus_wallet_dir: directory that exodus wallets were exported
    :return: dataframe in a common format
    """
    exodus_wallets = [x for x in os.listdir(exodus_wallet_dir) if x.endswith(".csv")]

    exodus_wallet = pd.DataFrame()
    # load all wallet csvs
    for wallet in exodus_wallets:
        df = pd.read_csv(os.path.join(exodus_wallet_dir, wallet))
        exodus_wallet = exodus_wallet.append(df, ignore_index=True)

    # fix the formating
    exodus_wallet['DATE'] = [datetime.strptime(t,'%a %b %d %Y %H:%M:%S GMT%z (%Z)') for t in exodus_wallet['DATE']]
    exodus_wallet['DATE'] = exodus_wallet['DATE'].astype('datetime64[ns]')
    exodus_wallet['COINAMOUNT'], exodus_wallet['AMOUNT_COIN'] = exodus_wallet['COINAMOUNT'].str.split(' ', 1).str
    exodus_wallet['COINAMOUNT'] = exodus_wallet['COINAMOUNT'].astype(float)
    exodus_wallet['BALANCE'], exodus_wallet['BALANCE_COIN'] = exodus_wallet['BALANCE'].str.split(' ', 1).str
    exodus_wallet['BALANCE'] = exodus_wallet['BALANCE'].astype(float)
    exodus_wallet['FEE'], exodus_wallet['FEE_COIN'] = exodus_wallet['FEE'].str.split(' ', 1).str
    exodus_wallet['FEE'] = exodus_wallet['FEE'].astype(float)

    # rename columns to common names
    exodus_wallet.columns = ['TXID',
                             'TXURL',
                             'Timestamp',
                             'COINAMOUNT',
                             'COIN_TransferFee',
                             'Balance',
                             'EXCHANGE',
                             'Notes',
                             'AMOUNT_COIN',
                             'BALANCE_COIN',
                             'FEE_COIN']
    exodus_wallet['WalletName'] = 'Exodus'


    return exodus_wallet


def import_coinbase_wallet(coinbase_wallet_dir=None):

    coinbase_wallets = [x for x in os.listdir(coinbase_wallet_dir) if x.endswith(".csv")]

    coinbase_wallet = pd.DataFrame()

    for wallet in coinbase_wallets:
        df = pd.read_csv(os.path.join(coinbase_wallet_dir, wallet),skiprows=4)
        coinbase_wallet = coinbase_wallet.append(df, ignore_index=True)

    coinbase_wallet['Timestamp'] = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S %z') for t in coinbase_wallet['Timestamp']]
    coinbase_wallet['Timestamp'] = coinbase_wallet['Timestamp'].astype('datetime64[ns]')
    # rename columns to common names

    coinbase_wallet.columns = ['Timestamp',
                                 'Balance',
                                 'COINAMOUNT',
                                 'AMOUNT_COIN',
                                 'Cbase_To',
                                 'Notes',
                                 'InstantlyExchanged',
                                 'TransferTotal',
                                 'TransferTotalCurrency',
                                 'TransferFee',
                                 'TransferFeeCurrency',
                                 'TransferPaymentMethod',
                                 'TransferID',
                                 'OrderPrice',
                                 'OrderCurrency',
                                 'OrderBTC',
                                 'OrderTrackingCode',
                                 'OrderCustomParameter',
                                 'OrderPaidOut',
                                 'RecurringPaymentID',
                                 'CoinbaseID',
                                 'TXID']

    coinbase_wallet['TransferTotal_USD'] = coinbase_wallet['TransferTotal']
    coinbase_wallet['TransferTotal'] = coinbase_wallet['TransferTotal']
    coinbase_wallet['COIN_PRICE_AT_TRANSACTION'] = coinbase_wallet['TransferTotal_USD'] / coinbase_wallet['COINAMOUNT']
    coinbase_wallet['COIN_TransferFee'] = coinbase_wallet['TransferFee'] / coinbase_wallet['COIN_PRICE_AT_TRANSACTION']
    coinbase_wallet['WalletName'] = 'Coinbase'
    coinbase_wallet['COIN_TransferFee'] = coinbase_wallet['COIN_TransferFee'] * -1
    coinbase_wallet['TXID'] = coinbase_wallet['TXID'].fillna(coinbase_wallet['CoinbaseID'])

    return coinbase_wallet

def import_jaxx_wallet(jaxx_wallet_csv=None):

    jaxx_wallet = pd.read_csv(jaxx_wallet_csv)
    jaxx_wallet['DATE'] = [datetime.strptime(t,'%a %b %d %Y %H:%M:%S GMT %z (%Z)') for t in jaxx_wallet['DATE']]
    jaxx_wallet['DATE'] = jaxx_wallet['DATE'].astype('datetime64[ns]')
    # jaxx_wallet['FEE'], jaxx_wallet['FEE_COIN'] = jaxx_wallet['FEE'].str.split(' ', 1).str
    # jaxx_wallet['FEE'] = jaxx_wallet['FEE'].astype(float)
    jaxx_wallet['COINAMOUNT'], jaxx_wallet['AMOUNT_COIN'] = jaxx_wallet['COINAMOUNT'].str.split(' ', 1).str
    jaxx_wallet['COINAMOUNT'] = jaxx_wallet['COINAMOUNT'].astype(float)
    jaxx_wallet['WalletName'] = 'Jaxx'

    jaxx_wallet.columns = ['TXID',
                             'TXURL',
                             'Timestamp',
                             'COINAMOUNT',
                             'COIN_TransferFee',
                             # 'FEE_COIN',
                             'AMOUNT_COIN',
                             'WalletName']

    return jaxx_wallet

def combine_wallets(wallet_list=[]):
    # NOTE: All times have already been converted to UTC
    return pd.concat(wallet_list, axis=0,ignore_index=True)



if __name__ == "__main__":
    exodus_wallet_dir = './exodus-exports'
    coinbase_wallet_dir = './coinbase_history'
    jaxx_wallet_csv = '/home/mcamp/PythonProjects/BitCoinDashboard/data_collection/Jaxx_transaction_history.csv'
    exodus_wallet = import_exodus_wallet(exodus_wallet_dir=exodus_wallet_dir)
    coinbase_wallet = import_coinbase_wallet(coinbase_wallet_dir=coinbase_wallet_dir)
    jaxx_wallet = import_jaxx_wallet(jaxx_wallet_csv=jaxx_wallet_csv)

    wallet_list = [coinbase_wallet, exodus_wallet, jaxx_wallet]
    print(combine_wallets(wallet_list=wallet_list))