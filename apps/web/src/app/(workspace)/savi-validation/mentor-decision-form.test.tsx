import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MentorDecisionForm } from "./mentor-decision-form";

describe("MentorDecisionForm", () => {
  it("keeps mentor preparation answers local and can clear them", () => {
    render(<MentorDecisionForm />);
    const field = screen.getByRole("textbox", {
      name: "Siapa validator substansi untuk setiap topik SUN?",
    });

    fireEvent.change(field, { target: { value: "Ketua tim sesuai topik" } });
    expect(field).toHaveValue("Ketua tim sesuai topik");
    expect(screen.getByLabelText("1 dari 9 pokok keputusan terisi")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Kosongkan isian" }));
    expect(field).toHaveValue("");
    expect(screen.getByLabelText("0 dari 9 pokok keputusan terisi")).toBeInTheDocument();
  });

  it("provides a printable discussion sheet without a submit action", () => {
    const print = vi.spyOn(window, "print").mockImplementation(() => undefined);
    render(<MentorDecisionForm />);

    expect(screen.queryByRole("button", { name: /simpan|setujui|aktifkan/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Cetak lembar" }));
    expect(print).toHaveBeenCalledOnce();
    print.mockRestore();
  });
});
