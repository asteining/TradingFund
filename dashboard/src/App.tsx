// Dashboard/src/App.tsx

import React, { useEffect, useState } from "react";
import { api } from "./api/client";
import PnlChart from "./components/PnlChart";
import { SweepSummaryTable } from "./components/SweepSummaryTable";
import { SeasonalPatternTable } from "./components/SeasonalPatternTable";
import { SpreadMetricsCard } from "./components/SpreadMetricsCard";

interface PnlPoint {
  date: string;
  value: number;
}

function App() {
  const [pnlData, setPnlData] = useState<PnlPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [symbol, setSymbol] = useState("AAPL");
  const [strategy, setStrategy] = useState("mean_reversion");

  useEffect(() => {
    const fetchPnl = async () => {
      setLoading(true);
      try {
        const response = await api.get<PnlPoint[]>(
          `/pnl?symbol=${symbol}&strategy=${strategy}`
        );
        setPnlData(response.data);
        setError(null);
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
        setPnlData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchPnl();
  }, [symbol, strategy]);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>Trading Fund – P&amp;L Chart</h1>
      <div style={{ marginBottom: 20 }}>
        <label>
          Symbol:&nbsp;
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
            <option value="AAPL">AAPL</option>
            <option value="MSFT">MSFT</option>
            <option value="GOOGL">GOOGL</option>
            <option value="BTC-USD">BTC-USD</option>
            <option value="ETH-USD">ETH-USD</option>
          </select>
        </label>
        &nbsp;&nbsp;
        <label>
          Strategy:&nbsp;
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
            <option value="mean_reversion">Mean Reversion</option>
            <option value="enhanced">Enhanced</option>
          </select>
        </label>
      </div>
      <p>
        Showing {symbol} using <em>{strategy}</em> strategy
      </p>
      {loading && <p>Loading P&amp;L…</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && !error && pnlData.length > 0 && <PnlChart data={pnlData} />}
      {!loading && !error && pnlData.length === 0 && (
        <p>No P&amp;L data available.</p>
      )}
      <section>
        <h2>Parameter Sweep Summary</h2>
        <SweepSummaryTable />
      </section>
      <section>
        <h2>Seasonal Patterns</h2>
        <SeasonalPatternTable />
      </section>
      <section>
        <h2>BTC–ETH Spread Metrics</h2>
        <SpreadMetricsCard />
      </section>
    </div>
  );
}

export default App;
