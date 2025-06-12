import React, { useEffect, useState } from "react";
import Card from "react-bootstrap/Card";
import { api } from "../api/client";

export interface SpreadMetrics {
  symbol1: string;
  symbol2: string;
  total_return: number;
  sharpe: number;
  max_drawdown: number;
}

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

const SpreadMetricsCard: React.FC = () => {
  const [metrics, setMetrics] = useState<SpreadMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get<SpreadMetrics>("/spread_metrics");
        setMetrics(response.data);
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
      }
    };
    fetchMetrics();
  }, []);

  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  if (!metrics) {
    return <p>Loading metrics...</p>;
  }

  return (
    <Card style={{ maxWidth: 400 }}>
      <Card.Body>
        <Card.Title>
          Spread Metrics {metrics.symbol1}/{metrics.symbol2}
        </Card.Title>
        <Card.Text>
          <strong>Total Return:</strong> {formatPercent(metrics.total_return)}
          <br />
          <strong>Sharpe Ratio:</strong> {metrics.sharpe.toFixed(2)}
          <br />
          <strong>Max Drawdown:</strong> {formatPercent(metrics.max_drawdown)}
        </Card.Text>
      </Card.Body>
    </Card>
  );
};

export default SpreadMetricsCard;
