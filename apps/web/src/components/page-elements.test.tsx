import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeadlineTag, EmptyState, SimulatedLabel } from "./page-elements";

describe("EmptyState", () => {
  it("renders an accessible status with the supplied message", () => {
    render(<EmptyState title="Belum ada hasil" description="Ubah kata pencarian." />);
    expect(screen.getByRole("status")).toHaveTextContent("Belum ada hasil");
    expect(screen.getByRole("status")).toHaveTextContent("Ubah kata pencarian.");
  });
});

describe("DeadlineTag", () => {
  it("conveys the deadline state as text, not color only", () => {
    render(<DeadlineTag state="OVERDUE" />);
    expect(screen.getByText("Terlambat")).toHaveClass("status-risk");
  });

  it("handles records without a due date", () => {
    render(<DeadlineTag state={null} />);
    expect(screen.getByText("Tanpa tenggat")).toBeInTheDocument();
  });
});

describe("SimulatedLabel", () => {
  it("shows a plain-language sample data label", () => {
    render(<SimulatedLabel />);
    expect(screen.getByText("Data contoh")).toBeInTheDocument();
  });
});
