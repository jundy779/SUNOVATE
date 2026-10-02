import type { ReactNode } from "react";
import { DEADLINE_LABELS, type DeadlineState } from "@sunovate/shared-types";

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="lede">{description}</p>
      </div>
      {action}
    </header>
  );
}

export type Tone = "neutral" | "success" | "risk" | "warning";

/** Status is always conveyed by text; color only reinforces it. */
export function StatusTag({ children, tone = "neutral" }: { children: ReactNode; tone?: Tone }) {
  return <span className={`status status-${tone}`}>{children}</span>;
}

const DEADLINE_TONES: Record<DeadlineState, Tone> = {
  SAFE: "neutral",
  DUE_SOON: "warning",
  DUE_TODAY: "warning",
  OVERDUE: "risk",
  COMPLETED: "success",
};

export function DeadlineTag({ state }: { state: DeadlineState | null }) {
  if (!state) return <StatusTag>Tanpa tenggat</StatusTag>;
  return <StatusTag tone={DEADLINE_TONES[state]}>{DEADLINE_LABELS[state]}</StatusTag>;
}

export function ClassificationTag({ code }: { code: string }) {
  return <span className="classification">{code}</span>;
}

export function SimulatedLabel() {
  return <span className="data-label">SIMULATED_DATA</span>;
}

export function EmptyState({
  title = "Belum ada data",
  description = "Data akan tampil setelah sumber yang berwenang tersedia.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <section className="empty-state" role="status">
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}

export function Panel({
  title,
  eyebrow,
  action,
  children,
}: {
  title: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="panel" aria-label={title}>
      <div className="section-heading">
        <div>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
