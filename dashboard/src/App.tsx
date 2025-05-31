// Dashboard/src/App.tsx

import React, { useEffect, useState } from "react";
import { api } from "./api/client";
import PnlChart from "./components/PnlChart";

interface PnlPoint {
  date: string;
  value: number;
}

function App() {
  const [pnlData, setPnlData] = useState<PnlPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPnl = async () => {
      try {
        const response = await api.get<PnlPoint[]>("/pnl");
        setPnlData(response.data);
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    };
    fetchPnl();
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h1>Trading Fund – P&amp;L Chart</h1>
      {loading && <p>Loading P&amp;L…</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && !error && pnlData.length > 0 && <PnlChart data={pnlData} />}
      {!loading && !error && pnlData.length === 0 && <p>No P&amp;L data available.</p>}
    </div>
  );
}

export default App;
