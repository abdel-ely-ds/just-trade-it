class Candle:
    def __init__(self, open_, high, low, close):
        self._open = open_
        self._high = high
        self._low = low
        self._close = close
        self.check_prices()

    def check_prices(self):
        if (
            self._open > self._high
            or self._open < self._low
            or self._close > self._high
            or self._close < self._low
        ):
            raise ValueError("open and close prices have to be between low and high")
        elif (
            self._low > self._open or self._low > self._close or self._low > self._high
        ):
            raise ValueError("low has to be the smallest price")

    def __len__(self):
        return self._high - self._low

    def __repr__(self):
        return "<Candle OHLC {} {} {} {} >".format(
            round(self._open, 2),
            round(self._high, 2),
            round(self._low, 2),
            round(self._close, 2),
        )

    def bull(self):
        return True if self._open < self._close else False

    def bear(self):
        return True if self._open > self._close else False

    def bull_pin(self, ratio=2 / 3):
        low_to_body = min(self._close, self._open) - self._low
        return True if low_to_body >= ratio * self.__len__() else False

    def bear_pin(self, ratio=2 / 3):
        high_to_body = self._high - max(self._open, self._close)
        return True if high_to_body >= ratio * self.__len__() else False

    def above_support(self, support_value):
        return min(self.open, self.close) > support_value

    @property
    def open(self):
        return self._open

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close

    @open.setter
    def open(self, open_price):
        if any([open_price > self._high, open_price < self._low]):
            raise ValueError("open price hase to be between low and high")
        self._open = open_price

    @high.setter
    def high(self, high_price):
        if any(
            [high_price < self._open, high_price < self._close, high_price < self._low]
        ):
            raise ValueError("high price has to be bigger than other prices")
        self._high = high_price

    @low.setter
    def low(self, low_price):
        if any(
            [low_price > self._open, low_price > self._close, low_price > self._high]
        ):
            raise ValueError("low price has to be smalller than other prices")
        self._low = low_price

    @close.setter
    def close(self, close_price):
        if any([close_price > self._high, close_price < self._low]):
            raise ValueError("close price hase to be between low and high")
        self._close = close_price
