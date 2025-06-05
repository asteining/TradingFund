# Backtester/strategies/mean_reversion_rsi.py

import backtrader as bt

class EnhancedMeanReversionStrategy(bt.Strategy):
    """Mean-reversion strategy enhanced with RSI and dynamic position sizing."""

    params = dict(
        period=20,       # lookback for moving average/std
        devfactor=2.0,   # z-score threshold
        stake=100,       # base shares per trade
        rsi_period=14,   # RSI calculation period
        rsi_lower=30,    # Oversold threshold
        rsi_upper=70,    # Overbought threshold
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.period)
        self.std = bt.indicators.StandardDeviation(self.data.close, period=self.p.period)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.value_history = []

    def next(self):
        self.value_history.append(self.broker.getvalue())
        z = (self.data.close[0] - self.sma[0]) / self.std[0]
        stake_size = int(self.p.stake * max(1.0, abs(z)))

        if not self.position:
            if z < -self.p.devfactor and self.rsi[0] < self.p.rsi_lower:
                self.buy(size=stake_size)
            elif z > self.p.devfactor and self.rsi[0] > self.p.rsi_upper:
                self.sell(size=stake_size)
        else:
            if (self.position.size > 0 and z >= 0) or (self.position.size < 0 and z <= 0):
                self.close()
