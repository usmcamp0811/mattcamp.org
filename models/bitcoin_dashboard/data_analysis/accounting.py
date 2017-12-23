from collections import deque
import pandas as pd
import numpy as np
import datetime as dt
from enum import Enum


"""
a module to do FIFO accounting on all transactions. 

Example: .
transaction_history = getCurrentWalletDF(session=session, db='cryptocoindb2')
transaction_history['name'] = transaction_history.name.str.lower()
transaction_history = transaction_history.sort_values('transaction_time', ascending=True)
coins = transaction_history['name'].tolist()

coin_ledgers = dict()
for coin in coins:
    el = []
    coin_transactions = transaction_history[transaction_history['name'] == coin]
    for i in range(coin_transactions.shape[0]):
        datetime = coin_transactions.iloc[i,:]['transaction_time']
        coin_amt = coin_transactions.iloc[i,:]['coins_transacted']
        price = abs(coin_transactions.iloc[i,:]['price_at_transaction'])
        el.append(Trade(datetime, coin_amt, price))

    b = Isin(coin, 1, el)
    coin_ledgers[coin] = FifoAccount(b)
    

"""

class Trade():
    def __init__(self, date: pd.datetime, quantity: np.float32, price: np.float32):
        self.date = date
        self.quantity = quantity
        self.price = price

    def printT(self):
        return print('Quantity: %f, Price: %f' % (self.quantity, self.price))


class Isin():
    def __init__(self, isin, notinalPerQuantity, listOfTrades):
        self._isin = isin
        self._notinalPerQuantity = notinalPerQuantity
        self._listOfTrades = listOfTrades

    def mtm(self, trade):
        return trade.quantity * trade.price * self._notinalPerQuantity

    def __next__(self):
        return self._listOfTrades.__next__()

    def __iter__(self):
        return self._listOfTrades.__iter__()


class transactionAccounting():
    def __init__(self, isin):
        """
        Initiliase with first entry from left
        """
        print('Initialize trade que')
        self._Isin = isin
        self._notinalPerQuantity = isin._notinalPerQuantity
        self._trades = isin._listOfTrades
        t0 = self._trades[0]
        self._avgprice = 0
        self._quantity = 0
        self._pnl = 0
        self._bookvalue = 0

    def printStat(self):
        print('Pos.Quantity: %f, AvgPrice: %f, PnL: %f, Book: %f' % (self._quantity,
                                                                     self._avgprice,
                                                                     self._pnl,
                                                                     self._bookvalue))

    def buy(self, trade):
        raise NotImplementedError

    def sell(self, trade):
        raise NotImplementedError


class FifoAccount(transactionAccounting):
    """
    checkout out this site for an example
    http://accountingexplained.com/financial/inventories/fifo-method
    """

    def __init__(self, trades):
        transactionAccounting.__init__(self, trades)
        self._deque = deque()
        for trade in self._trades:
            if trade.quantity >= 0:
                self.buy(trade)
            else:
                self.sell(trade)

    def buy(self, trade):
        print('Buy trade')
        trade.printT()
        self._deque.append(trade)
        self._bookvalue += self._Isin.mtm(trade)
        self._quantity += trade.quantity
        self._avgprice = self._bookvalue / self._quantity / self._notinalPerQuantity
        self.printStat()

    def sell(self, trade):
        print('***Sell trade')
        trade.printT()
        sellQuant = -trade.quantity
        while (sellQuant > 0):
            lastTrade = self._deque.popleft()
            price = lastTrade.price
            quantity = lastTrade.quantity
            print('Cancel trade:')
            lastTrade.printT()
            if sellQuant >= quantity:
                self._pnl += -(price - trade.price) * quantity * self._notinalPerQuantity
                self._quantity -= quantity
                self._bookvalue -= price * quantity * self._notinalPerQuantity
                sellQuant -= quantity
            else:
                # from IPython.core.debugger import Tracer; Tracer()()
                self._pnl += -(price - trade.price) * sellQuant * self._notinalPerQuantity
                self._quantity -= sellQuant
                self._bookvalue -= price * sellQuant * self._notinalPerQuantity
                lastTrade.quantity -= sellQuant
                self._deque.appendleft(lastTrade)
                sellQuant = 0
            self.printStat()
            assert (self._quantity > 0)
