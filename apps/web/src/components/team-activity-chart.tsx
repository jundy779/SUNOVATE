"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const rows = [
  { day: "Sen", selesai: 2, proses: 4, tindakLanjut: 3, terlambat: 0 },
  { day: "Sel", selesai: 2, proses: 5, tindakLanjut: 4, terlambat: 1 },
  { day: "Rab", selesai: 3, proses: 5, tindakLanjut: 3, terlambat: 0 },
  { day: "Kam", selesai: 3, proses: 4, tindakLanjut: 4, terlambat: 1 },
  { day: "Jum", selesai: 3, proses: 3, tindakLanjut: 4, terlambat: 0 },
];

export function TeamActivityChart() {
  return (
    <figure className="activity-chart">
      <div className="activity-chart-canvas" aria-hidden="true">
        <ResponsiveContainer width="100%" height={238}>
          <BarChart data={rows} margin={{ top: 12, right: 8, bottom: 0, left: -18 }}>
            <CartesianGrid stroke="#D8DDE3" vertical={false} />
            <XAxis dataKey="day" tick={{ fill: "#6B7280", fontSize: 11 }} axisLine={{ stroke: "#D8DDE3" }} tickLine={false} />
            <YAxis allowDecimals={false} tick={{ fill: "#6B7280", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip cursor={{ fill: "#F3F5F7" }} />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
            <Bar dataKey="proses" name="Dalam proses" stackId="a" fill="#0D2E5E" isAnimationActive={false} />
            <Bar dataKey="tindakLanjut" name="Perlu tindak lanjut" stackId="a" fill="#C9A227" isAnimationActive={false} />
            <Bar dataKey="selesai" name="Selesai" stackId="a" fill="#2E8B57" isAnimationActive={false} />
            <Bar dataKey="terlambat" name="Terlambat" stackId="a" fill="#B22222" isAnimationActive={false} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <figcaption className="sr-only">Aktivitas tim simulasi pada hari Senin sampai Jumat, dibagi berdasarkan status.</figcaption>
    </figure>
  );
}
