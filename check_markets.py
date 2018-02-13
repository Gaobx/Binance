# -*- coding: utf-8 -*-

from binance.client import Client
import config
import re


class CheckMarkets(object):

    def __init__(self):
        self.client = Client(config.api_key, config.api_secret)
        self.gap_coins = []
        # self.coins_pair = self.get_coins()
        self.coins_pair = config.coins_pair_cache
        # self.check_markets()

    # API
    def check_markets(self):
        # self.handle_each_coin()
        self.gap_coins = []
        self.handle_all_coins_onetime()

        # print '\n\n\n' + str(len(self.gap_coins))
        # for coins in self.gap_coins:
        #     print coins

        return self.gap_coins

    # API
    def check_markets_best(self):

        gap_coins = self.check_markets()
        gap_coins.sort(lambda x, y: cmp(x[0], y[0]))
        # print gap_coins[ len(gap_coins) - 1 ]
        # for i in gap_coins:
        #     print i
        # print gap_coins
        return gap_coins[ len(gap_coins) - 1 ]

    def get_coins(self):

        all_tickers = self.client.get_orderbook_tickers()
        coins_btc = []
        coins_eth = []
        coins_bnb = []
        coins_usdt = []
        for coin in all_tickers:
            coin_pair = coin['symbol']
            m = re.search('(.+)BTC', coin_pair)
            if str(m) != 'None':
                coins_btc.append(m.group(1))

            m = re.search('(.+)ETH', coin_pair)
            if str(m) != 'None':
                coins_eth.append(m.group(1))

            m = re.search('(.+)BNB', coin_pair)
            if str(m) != 'None':
                coins_bnb.append(m.group(1))

            m = re.search('(.+)USDT', coin_pair)
            if str(m) != 'None':
                coins_usdt.append(m.group(1))

        coins = {}
        coins['BTC'] = coins_btc
        coins['ETH'] = coins_eth
        coins['BNB'] = coins_bnb
        coins['USDT'] = coins_usdt

        print coins
        print u"获取币种完成"

        return coins

    def handle_each_coin(self):
        pairs = [0, 1, 2]
        for coins_pair in config.work_coins:
            coin0 = coins_pair[0]
            coin1 = coins_pair[1]
            pairs[0] = coin0+coin1
            print pairs[0]
            for coin2 in self.coins_pair[coin0]:
                if coin2 not in self.coins_pair[coin1]:
                    continue
                pairs[1] = coin2 + coin0
                pairs[2] = coin2 + coin1
                self.handle_each_coin_gap(pairs)

    def handle_each_coin_gap(self, pairs):

        prices = self.get_each_coin_pair_tickers(pairs)
        self.calc_price_gap(pairs, prices)

    def get_each_coin_pair_tickers(self, pairs):
        prices = []
        prices.append(self.client.get_orderbook_ticker(symbol=pairs[0]))
        prices.append(self.client.get_orderbook_ticker(symbol=pairs[1]))
        prices.append(self.client.get_orderbook_ticker(symbol=pairs[2]))
        return prices

    def handle_all_coins_onetime(self):
        orderbook_tickers = self.client.get_orderbook_tickers()
        all_coins_pair = {}
        for coin_pair in orderbook_tickers:
            all_coins_pair[coin_pair['symbol']] = coin_pair

        pairs = [0, 1, 2]
        for coins_pair in config.work_coins:
            coin0 = coins_pair[0]
            coin1 = coins_pair[1]
            pairs[0] = coin0 + coin1
            # print pairs[0]
            for coin2 in self.coins_pair[coin0]:
                if coin2 not in self.coins_pair[coin1]:
                    continue
                pairs[1] = coin2 + coin0
                pairs[2] = coin2 + coin1
                self.handle_all_coins_gap_onetime(all_coins_pair, pairs)

    def handle_all_coins_gap_onetime(self, all_coins_pair, pairs):
        prices = []
        prices.append(all_coins_pair[pairs[0]])
        prices.append(all_coins_pair[pairs[1]])
        prices.append(all_coins_pair[pairs[2]])

        self.calc_price_gap(pairs, prices)

    def calc_price_gap(self, pairs, prices):

        # 111111
        pair0_ask_price = float(prices[0]['askPrice'])
        pair1_ask_price = float(prices[1]['askPrice'])
        pair2_bid_price = float(prices[2]['bidPrice'])

        coin0_qty = 1 / pair0_ask_price
        coin2_qty = coin0_qty / pair1_ask_price
        coin1_qty = coin2_qty * pair2_bid_price

        # string = pairs[0] + ' ' + pairs[1] + ' ' + pairs[2] + '\t' + str(coin1_qty)
        # flag = '\t'
        result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if coin1_qty > 1:
            result[2] = pairs[0]
            result[3] = pair0_ask_price
            result[4] = float(prices[0]['askQty'])

            result[5] = pairs[1]
            result[6] = pair1_ask_price
            result[7] = float(prices[1]['askQty'])

            result[8] = pairs[2]
            result[9] = pair2_bid_price
            result[10] = float(prices[2]['bidQty'])

            result[0] = coin1_qty
            result[1] = 0
            self.gap_coins.append(result)
            # flag += 'YES'
            # string += flag
            # self.gap_coins.append(string)
        # print string

        # 2222222
        pair2_ask_price = float(prices[2]['askPrice'])
        pair1_bid_price = float(prices[1]['bidPrice'])
        pair0_bid_price = float(prices[0]['bidPrice'])

        coin2_qty = 1 / pair2_ask_price
        coin0_qty = coin2_qty * pair1_bid_price
        coin1_qty = coin0_qty * pair0_bid_price

        # string = pairs[2] + ' ' + pairs[1] + ' ' + pairs[0] + '\t' + str(coin1_qty)
        # flag = '\t'
        if coin1_qty > 1:
            result[2] = pairs[2]
            result[3] = pair2_ask_price
            result[4] = float(prices[2]['askQty'])

            result[5] = pairs[1]
            result[6] = pair1_bid_price
            result[7] = float(prices[1]['bidQty'])

            result[8] = pairs[0]
            result[9] = pair0_bid_price
            result[10] = float(prices[0]['bidQty'])

            result[0] = coin1_qty
            result[1] = 1
            self.gap_coins.append(result)
            # flag += 'YES'
            # string += flag
            # self.gap_coins.append(string)
        # print string

# result = CheckMarkets().check_markets()
# for i in result:
#     print i
# print ""
# print CheckMarkets().check_markets_best()
#





















            # get account info
            # account_info = client.get_account()
            # print account_info

            # get orderbool ticker
            # orderbook = client.get_orderbook_ticker(symbol = "BNBBTC")
            # print orderbook

            # get all prices
            # all_prices = client.get_all_tickers()
            # print all_prices

            # get recent trades
            # trades = client.get_recent_trades(symbol='BNBBTC')
            # print trades

            # get symbol info
            # info = client.get_symbol_info('BNBBTC')
            # print info

            # get current products
            # products = client.get_products()
            # print products['data'][0]

            # client.ping()
            #
            # time_res = client.get_server_time()
            # print time_res
            #
            # info = client.get_symbol_info('BNBBTC')
            # print info
            #
            # all_orders = client.get_all_orders(symbol='BNBBTC')
            #
            # print all_orders