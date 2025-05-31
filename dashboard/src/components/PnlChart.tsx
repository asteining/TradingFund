// Dashboard/src/components/PnlChart.tsx

import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface PnlPoint {
  date: string;
  value: number;
}

interface PnlChartProps {
  data: PnlPoint[];
}

const PnlChart: React.FC<PnlChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={(tick) => tick.slice(5)} />
        <YAxis domain={["auto", "auto"]} />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#3366cc" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PnlChart;
