import { describe, expect, it } from "vitest";
import { isBlockedShortcut, isUuid } from "./secure-documents";

const key = (k: string, mods: Partial<{ ctrlKey: boolean; metaKey: boolean; shiftKey: boolean }> = {}) => ({
  key: k,
  ctrlKey: false,
  metaKey: false,
  shiftKey: false,
  ...mods,
});

describe("secure document helpers", () => {
  it("accepts only UUIDs as document ids", () => {
    expect(isUuid("6f1d3c52-5d0a-5a2f-9f53-2b7a1c0e8d44")).toBe(true);
    expect(isUuid("../../etc/passwd")).toBe(false);
    expect(isUuid("123")).toBe(false);
  });

  it("blocks save, print, copy, source, and developer-tool shortcuts", () => {
    expect(isBlockedShortcut(key("s", { ctrlKey: true }))).toBe(true);
    expect(isBlockedShortcut(key("p", { metaKey: true }))).toBe(true);
    expect(isBlockedShortcut(key("c", { ctrlKey: true }))).toBe(true);
    expect(isBlockedShortcut(key("I", { ctrlKey: true, shiftKey: true }))).toBe(true);
    expect(isBlockedShortcut(key("F12"))).toBe(true);
    expect(isBlockedShortcut(key("PrintScreen"))).toBe(true);
  });

  it("leaves ordinary navigation keys alone", () => {
    expect(isBlockedShortcut(key("ArrowRight"))).toBe(false);
    expect(isBlockedShortcut(key("s"))).toBe(false);
    expect(isBlockedShortcut(key("Tab", { shiftKey: true }))).toBe(false);
  });
});
