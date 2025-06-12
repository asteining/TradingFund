import React, { useEffect, useState } from "react";
// Use a standard HTML table; no react-bootstrap dependency
import { api } from "../api/client";

export interface WeekStat {
  weekday: string;
  avg_return: number;
  t_stat: number;
}

const SeasonalPatternTable: React.FC = () => {
  const [stats, setStats] = useState<WeekStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get<WeekStat[]>("/seasonal_stats");
        setStats(response.data);
        setError(null);
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <p>Loading seasonal stats…</p>;
  }
  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th>Weekday</th>
          <th>Avg Return</th>
          <th>t-Statistic</th>
        </tr>
      </thead>
      <tbody>
        {stats.map((stat) => (
          <tr key={stat.weekday}>
            <td>{stat.weekday}</td>
            <td>{(stat.avg_return * 100).toFixed(2)}%</td>
            <td>{stat.t_stat.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default SeasonalPatternTable;
