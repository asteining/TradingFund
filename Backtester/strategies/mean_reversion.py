import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = dict(period=20, devfactor=2.0)
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.period)
        self.std = bt.indicators.StandardDeviation(self.data.close, period=self.p.period)
    def next(self):
        z = (self.data.close[0] - self.sma[0]) / self.std[0]
        if z > self.p.devfactor:
            self.sell(size=100)
        elif z < -self.p.devfactor:
            self.buy(size=100)
