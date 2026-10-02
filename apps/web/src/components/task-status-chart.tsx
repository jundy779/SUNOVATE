"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TASK_STATUS_LABELS, type TaskStatus } from "@sunovate/shared-types";

export interface StatusCount {
  status: TaskStatus;
  count: number;
}

/** Horizontal bar chart of tasks per status; a table with the same numbers serves screen readers. */
export function TaskStatusChart({ data }: { data: StatusCount[] }) {
  const rows = data.map((d) => ({ label: TASK_STATUS_LABELS[d.status], count: d.count }));
  return (
    <figure className="chart">
      <div className="chart-canvas" aria-hidden="true">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={rows} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
            <CartesianGrid stroke="#D8DDE3" horizontal={false} />
            <XAxis type="number" allowDecimals={false} tick={{ fill: "#6B7280", fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="label"
              width={128}
              tick={{ fill: "#091F42", fontSize: 12 }}
            />
            <Tooltip cursor={{ fill: "#F7F8FA" }} />
            <Bar dataKey="count" name="Jumlah tugas" fill="#0D2E5E" barSize={16} />
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
