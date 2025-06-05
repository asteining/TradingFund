"""Live trading integration using ib_insync.

This script connects to Interactive Brokers and implements a very simple
mean-reversion strategy based on the existing Backtester logic.  It fetches
historical data to seed the indicators and then reacts to live price updates.

It is intentionally minimal and meant as a starting point.  Run in paper
trading first!  Requires ib_insync and access to the IB Gateway or TWS.
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from ib_insync import IB, Stock, util, MarketOrder
from dotenv import load_dotenv

# Reuse the mean reversion parameters from the backtester
from Backtester.strategies.mean_reversion import MeanReversionStrategy


class LiveMeanReversionTrader:
    """Connects to IB and trades a single stock live."""

    def __init__(self, symbol: str, cash: float = 100_000.0):
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
        self.host = os.getenv("IB_HOST", "127.0.0.1")
        self.port = int(os.getenv("IB_PORT", 7497))
        self.client_id = int(os.getenv("IB_CLIENT_ID", 1))

        self.symbol = symbol.upper()
        self.cash = cash

        self.ib = IB()
        self.contract = Stock(self.symbol, "SMART", "USD")

        # Strategy parameters match MeanReversionStrategy defaults
        self.period = MeanReversionStrategy.params.period
        self.devfactor = MeanReversionStrategy.params.devfactor
        self.stake = MeanReversionStrategy.params.stake

        self.prices: List[float] = []
        self.position = 0

    def connect(self):
        self.ib.connect(self.host, self.port, clientId=self.client_id)
        print(f"Connected to IB at {self.host}:{self.port} (clientId={self.client_id})")

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

    def fetch_history(self):
        """Seed our price series with the last `period` days of closes."""
        bars = self.ib.reqHistoricalData(
            self.contract,
            endDateTime="",
            durationStr=f"{self.period} D",
            barSizeSetting="1 day",
            whatToShow="ADJUSTED_LAST",
            useRTH=True,
            formatDate=1,
        )
        df = util.df(bars)
        self.prices = df["close"].tolist()
        print(f"Loaded {len(self.prices)} historical closes for {self.symbol}")

    def compute_z(self, price: float) -> float:
        window = self.prices[-self.period :]
        sma = np.mean(window)
        std = np.std(window)
        if std == 0:
            return 0.0
        return (price - sma) / std

    async def run(self):
        self.connect()
        self.fetch_history()

        ticker = self.ib.reqMktData(self.contract, snapshot=False)

        try:
            while True:
                await self.ib.sleep(1)
                if ticker.last is None:
                    continue
                price = ticker.last
                self.prices.append(price)
                z = self.compute_z(price)

                if self.position == 0:
                    if z > self.devfactor:
                        order = MarketOrder("SELL", self.stake)
                        trade = self.ib.placeOrder(self.contract, order)
                        self.position -= self.stake
                        print(f"{datetime.now()}: SELL {self.stake} @ {price:.2f} (z={z:.2f})")
                        await trade.completed
                    elif z < -self.devfactor:
                        order = MarketOrder("BUY", self.stake)
                        trade = self.ib.placeOrder(self.contract, order)
                        self.position += self.stake
                        print(f"{datetime.now()}: BUY  {self.stake} @ {price:.2f} (z={z:.2f})")
                        await trade.completed
                else:
                    if (self.position > 0 and z >= 0) or (self.position < 0 and z <= 0):
                        side = "SELL" if self.position > 0 else "BUY"
                        order = MarketOrder(side, abs(self.position))
                        trade = self.ib.placeOrder(self.contract, order)
                        print(f"{datetime.now()}: CLOSE {self.position} @ {price:.2f} (z={z:.2f})")
                        self.position = 0
                        await trade.completed
        finally:
            self.disconnect()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trader.py SYMBOL")
        sys.exit(1)
    symbol = sys.argv[1]
    trader = LiveMeanReversionTrader(symbol)
    asyncio.run(trader.run())
