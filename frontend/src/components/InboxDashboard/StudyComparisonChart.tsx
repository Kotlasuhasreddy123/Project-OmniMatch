"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface ComparisonDatum {
  name: string;
  score: number;
}

export default function StudyComparisonChart({
  data,
}: {
  data: ComparisonDatum[];
}) {
  return (
    <div
      className="my-6 h-64 w-full min-w-0"
      aria-label="Study review score comparison; values are listed below"
    >
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <BarChart
          data={data}
          layout="vertical"
          accessibilityLayer
          margin={{ left: 8, right: 18 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            horizontal={false}
            stroke="#e3e9e7"
          />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={115}
            tick={{ fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "#edf4f3" }}
            formatter={(value) => [`${value} / 100`, "Review score"]}
            contentStyle={{ borderRadius: 14, border: "1px solid #e3e9e7" }}
          />
          <Bar
            dataKey="score"
            fill="#087f70"
            radius={[0, 6, 6, 0]}
            maxBarSize={24}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
