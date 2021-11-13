from t_nachine.backtester import Strategy
from t_nachine.candlesticks import Candle
from t_nachine.indicators import rsi
from t_nachine.patterns import BullBearPattern
from t_nachine.risk import RiskManger
from t_nachine.strategies.utils import add_attrs, get_candles

WAIT = 1
RISK_PER_TRADE = 0.01
RISK_TO_REWARD = 2.0
RSI_THRESH = 10


class ExtremeRSI(Strategy):
    def init(self):
        self.rsi = self.I(rsi, self.data, n=2)
        self.rsi_thresh = RSI_THRESH
        self.wait = WAIT
        self.risk_to_reward = RISK_TO_REWARD
        self.risk_per_trade = RISK_PER_TRADE
        self.risk_manager = RiskManger(
            risk_to_reward=self.risk_to_reward, risk_per_trade=self.risk_per_trade
        )

    def cancel(
        self,
    ) -> None:
        """
        wait until <self.wait> days then cancel order if not executed
        """
        for order in self.orders:
            if (
                not order.is_contingent
                and len(self.data) - order.placed_bar >= self.wait
            ):
                order.cancel()

    def buy_signal(self, candle0: Candle, candle1: Candle) -> bool:
        """
        buy signal

        Args:
            candle0 (Candle): [description]
            candle1 ([type]): [description]

        Returns:
            bool: is buy signal triggered
        """

        rsi_below_10 = self.rsi[-2] < self.rsi_thresh
        is_bull_bear = BullBearPattern(candle=candle0, pre_candle=candle1)

        return all([rsi_below_10, is_bull_bear])

    def next(self):
        # cancel pending orders
        self.cancel()

        # add attributes
        for trade in self.trades:
            add_attrs(
                trade=trade,
                high=self.data.High[-1],
                low=self.data.Low[-1],
                volume=self.data.Volume[-1],
            )

        try:
            candle0, candle1 = get_candles(self.data, days=2)
            if self.buy_signal(candle0, candle1):

                # entries and exits and number of shares
                stop = self.risk_manager.entry_price(candle0.high)
                limit = self.risk_manager.entry_price(candle0.high, limit=2)
                sl = self.risk_manager.stop_loss(candle1.low)
                tp = self.risk_manager.target(stop, sl)
                size = self.risk_manager.shares(self.equity, stop, sl)

                order = self.buy(stop=stop, limit=limit, sl=sl, tp=tp, size=size)
                setattr(order, "placed_time", self.data.index[-1])
                setattr(order, "placed_bar", len(self.data))

        except IndexError:
            pass
