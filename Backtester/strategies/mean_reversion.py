# Backtester/strategies/mean_reversion.py

import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = dict(
        period=20,      # lookback for moving average / std
        devfactor=2.0,  # z‐score threshold
        stake=100       # shares per trade
    )

    def __init__(self):
        # Standard indicators
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.period)
        self.std = bt.indicators.StandardDeviation(self.data.close, period=self.p.period)

        # List to keep track of portfolio value each bar
        self.value_history = []

    def next(self):
        # 1) Record the portfolio value _before_ making new trades
        self.value_history.append(self.broker.getvalue())

        # 2) Compute z-score
        z = (self.data.close[0] - self.sma[0]) / self.std[0]

        # 3) Entry logic if we're flat
        if not self.position:
            if z > self.p.devfactor:
                # If price is > sma + (devfactor × std), go short
                self.sell(size=self.p.stake)
            elif z < -self.p.devfactor:
                # If price is < sma − (devfactor × std), go long
                self.buy(size=self.p.stake)
        else:
            # 4) Exit when z crosses back through zero
            if (self.position.size > 0 and z >= 0) or (self.position.size < 0 and z <= 0):
                self.close()
