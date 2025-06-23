// Dashboard/src/components/SweepSummaryTable.tsx

import React, { useEffect, useState } from "react";
// Using a regular HTML table instead of react-bootstrap to avoid external dependencies
import axios from "axios";

export interface SweepRow {
  period: number;
  devfactor: number;
  stake: number;
  total_return: number;
  sharpe: number;
  max_drawdown: number;
}

interface Props {
  symbol: string;
}

const SweepSummaryTable: React.FC<Props> = (props) => {
  const [rows, setRows] = useState<SweepRow[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get<SweepRow[]>(`/sweep_summary?symbol=${props.symbol}`);
        setRows(response.data);
      } catch (err) {
        console.error("Failed to fetch sweep summary", err);
      }
    };

    fetchData();
  }, []);

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th>Period</th>
          <th>DevFactor</th>
          <th>Stake</th>
          <th>Total Return</th>
          <th>Sharpe</th>
          <th>Max Drawdown</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr key={idx}>
            <td>{row.period}</td>
            <td>{row.devfactor}</td>
            <td>{row.stake}</td>
            <td>{(row.total_return * 100).toFixed(2)}%</td>
            <td>{row.sharpe}</td>
            <td>{(row.max_drawdown * 100).toFixed(2)}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default SweepSummaryTable;
