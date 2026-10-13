/**
 * Domain enumerations shared by the web app and API contracts.
 * Must stay in sync with apps/api (sunovate_api.db.models and modules).
 */

export const DATA_LABEL = "SIMULATED_DATA" as const;

export const CLASSIFICATIONS = ["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"] as const;
export type ClassificationCode = (typeof CLASSIFICATIONS)[number];

export const TEAM_CODES = ["PPSUN", "AKPSUN", "PSUN", "PPPSUN", "DHTV", "SUN_TEMATIK"] as const;
export type TeamCode = (typeof TEAM_CODES)[number];

export const KNOWLEDGE_STATUSES = [
  "DRAFT",
  "IN_REVIEW",
  "PUBLISHED",
  "SUPERSEDED",
  "ARCHIVED",
] as const;
export type KnowledgeStatus = (typeof KNOWLEDGE_STATUSES)[number];

export const TASK_STATUSES = [
  "NOT_STARTED",
  "IN_PROGRESS",
  "WAITING_INTERNAL",
  "WAITING_EXTERNAL",
  "ON_HOLD",
  "COMPLETED",
  "CANCELLED",
] as const;
export type TaskStatus = (typeof TASK_STATUSES)[number];

export const DEADLINE_STATES = ["SAFE", "DUE_SOON", "DUE_TODAY", "OVERDUE", "COMPLETED"] as const;
export type DeadlineState = (typeof DEADLINE_STATES)[number];

export const HERMES_DECISIONS = [
  "ANSWERED",
  "INSUFFICIENT_EVIDENCE",
  "REFUSED_OUT_OF_SCOPE",
  "REFUSED_GENERAL_CODING",
  "REFUSED_POLICY",
  "REQUIRES_HUMAN_APPROVAL",
  "BLOCKED_BY_OUTPUT_GUARD",
] as const;
export type HermesDecision = (typeof HERMES_DECISIONS)[number];

/** Indonesian UI labels. */
export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  NOT_STARTED: "Belum dimulai",
  IN_PROGRESS: "Berjalan",
  WAITING_INTERNAL: "Menunggu internal",
  WAITING_EXTERNAL: "Menunggu eksternal",
  ON_HOLD: "Ditunda",
  COMPLETED: "Selesai",
  CANCELLED: "Dibatalkan",
};

export const DEADLINE_LABELS: Record<DeadlineState, string> = {
  SAFE: "Aman",
  DUE_SOON: "Jatuh tempo dekat",
  DUE_TODAY: "Jatuh tempo hari ini",
  OVERDUE: "Terlambat",
  COMPLETED: "Selesai",
};

export const HERMES_DECISION_LABELS: Record<HermesDecision, string> = {
  ANSWERED: "Dijawab dengan sumber",
  INSUFFICIENT_EVIDENCE: "Bukti tidak cukup",
  REFUSED_OUT_OF_SCOPE: "Di luar domain SUN",
  REFUSED_GENERAL_CODING: "Bukan layanan pemrograman",
  REFUSED_POLICY: "Tidak dapat dijawab sesuai ketentuan",
  REQUIRES_HUMAN_APPROVAL: "Perlu persetujuan manusia",
  BLOCKED_BY_OUTPUT_GUARD: "Jawaban belum dapat ditampilkan",
};
