from backtrader import Cerebro
from strategies.mean_reversion import MeanReversionStrategy

def run_backtest(data_path, cash=100_000):
    cerebro = Cerebro()
    cerebro.broker.setcash(cash)
    cerebro.addstrategy(MeanReversionStrategy)
    cerebro.adddata(backtrader.feeds.YahooFinanceCSVData(dataname=data_path))
    print('Starting Portfolio Value:', cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value:', cerebro.broker.getvalue())
    cerebro.plot()

if __name__ == '__main__':
    run_backtest('data/AAPL.csv')
