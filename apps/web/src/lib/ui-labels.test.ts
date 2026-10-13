import { describe, expect, it } from "vitest";
import {
  auditActionLabel,
  auditEntityLabel,
  classificationLabel,
  knowledgeStatusLabel,
  knowledgeTypeLabel,
  outcomeLabel,
  permissionLabel,
  roleLabel,
} from "./ui-labels";

describe("plain-language interface labels", () => {
  it("translates internal codes before they reach users", () => {
    expect(classificationLabel("RESTRICTED")).toBe("Terbatas");
    expect(knowledgeStatusLabel("IN_REVIEW")).toBe("Dalam pemeriksaan");
    expect(knowledgeTypeLabel("LESSON_LEARNED")).toBe("Catatan pembelajaran");
    expect(roleLabel("knowledge_coordinator")).toBe("Koordinator pengetahuan");
    expect(permissionLabel("hermes:query")).toBe("Bertanya kepada SAVI AI");
    expect(auditActionLabel("AI_QUERY")).toBe("Bertanya kepada SAVI");
    expect(auditEntityLabel("pending_matter")).toBe("Hal yang perlu ditindaklanjuti");
    expect(outcomeLabel("SUCCESS")).toBe("Berhasil");
  });

  it("uses safe generic labels for unknown internal codes", () => {
    expect(classificationLabel("UNKNOWN")).toBe("Belum ditetapkan");
    expect(permissionLabel("internal:new_permission")).toBe("Kewenangan lainnya");
    expect(auditEntityLabel("new_entity")).toBe("Data SUNOVATE");
  });
});
