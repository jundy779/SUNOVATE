"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TASK_STATUS_LABELS, type TaskStatus } from "@sunovate/shared-types";

export interface StatusCount {
  status: TaskStatus;
  count: number;
}

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  return reduced;
}

/** Horizontal bar chart of tasks per status; a table with the same numbers serves screen readers. */
export function TaskStatusChart({ data }: { data: StatusCount[] }) {
  const reducedMotion = usePrefersReducedMotion();
  const rows = data.map((d) => ({ label: TASK_STATUS_LABELS[d.status], count: d.count }));
  return (
    <figure className="chart">
      <div className="chart-canvas" aria-hidden="true">
        <ResponsiveContainer width="100%" height={Math.max(160, rows.length * 38)}>
          <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 36, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="#D8DDE3" horizontal={false} />
            <XAxis type="number" allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: "#6B7280", fontSize: 11 }} />
            <YAxis type="category" dataKey="label" width={132} axisLine={false} tickLine={false} tick={{ fill: "#0D2E5E", fontSize: 12 }} />
            <Tooltip cursor={{ fill: "#F3F5F7" }} />
            <Bar
              dataKey="count"
              name="Jumlah tugas"
              fill="#0D2E5E"
              barSize={14}
              isAnimationActive={!reducedMotion}
              animationDuration={700}
              animationEasing="ease-out"
            >
              <LabelList dataKey="count" position="right" fill="#0D2E5E" fontSize={12} fontWeight={700} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <figcaption className="sr-only">
        <table>
          <caption>Jumlah tugas per status</caption>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label}>
                <th scope="row">{row.label}</th>
                <td>{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </figcaption>
    </figure>
  );
}
