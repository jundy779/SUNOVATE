/**
 * API contracts for /api/v1, maintained manually alongside the FastAPI OpenAPI schema
 * (docs/07-api/openapi-guidelines.md). Request schemas mirror backend validation.
 */
import { z } from "zod";
import type {
  ClassificationCode,
  DeadlineState,
  HermesDecision,
  KnowledgeStatus,
  TaskStatus,
} from "@sunovate/shared-types";

export interface PageMeta {
  dataLabel: "SIMULATED_DATA";
  page?: number;
  pageSize?: number;
  total?: number;
  totalPages?: number;
  [key: string]: unknown;
}

export interface Envelope<T> {
  data: T;
  meta: PageMeta;
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details: unknown;
  requestId: string;
}

export interface Principal {
  id: string;
  email: string;
  displayName: string;
  roles: string[];
  permissions: string[];
  teams: { id: string; code: string }[];
  allTeams: boolean;
  clearanceCode: ClassificationCode;
}

export interface KnowledgeEntry {
  id: string;
  title: string;
  knowledgeType: string;
  summary: string;
  lifecycleStatus: KnowledgeStatus;
  sharingScope: "TEAM" | "DIRECTORATE";
  classificationCode: ClassificationCode;
  ownerTeamCode: string | null;
  ownerUserId: string | null;
  versionLabel: string;
  revision: number;
  updatedAt: string;
  dataOrigin: string;
  sourceNote?: string | null;
  sections?: { index: number; sectionLabel: string; content: string }[];
  documents?: { id: string; title: string; provider: string; providerLocation: string }[];
}

export interface ApprovalRequest {
  id: string;
  requestType: string;
  targetEntityType: string;
  targetEntityId: string | null;
  status: "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";
  requestedBy: string;
  requestedByName: string | null;
  decidedBy: string | null;
  decidedAt: string | null;
  decisionReason: string | null;
  ownerTeamCode: string | null;
  classificationCode: ClassificationCode;
  revision: number;
  createdAt: string;
  targetTitle: string | null;
  targetLifecycleStatus: KnowledgeStatus | null;
}

export interface WorkItem {
  id: string;
  title: string;
  status: TaskStatus | string;
  ownerTeamCode: string | null;
  classificationCode: ClassificationCode;
  deadlineState: DeadlineState | null;
  dueDate?: string | null;
  targetDate?: string | null;
  progress?: number;
  description?: string;
  priority?: "LOW" | "NORMAL" | "HIGH" | "URGENT";
  workOutputId?: string | null;
  pendingMatterId?: string | null;
  revision: number;
}

export interface TeamSummary {
  id: string;
  code: string;
  name: string;
}

export interface SearchHit {
  knowledgeEntryId: string;
  title: string;
  knowledgeType: string;
  ownerTeamCode: string | null;
  classificationCode: ClassificationCode;
  sectionLabel: string | null;
  snippet: string;
  score: number;
}

export interface DraftSearchHit extends SearchHit {
  updatedAt: string;
  accessReason: "OWNER" | "REVIEWER";
}

export interface DashboardSummary {
  scope: { allTeams: boolean; teamCodes: string[]; clearanceCode: ClassificationCode };
  metrics: {
    totalActiveTasks: number;
    attentionCount: number;
    inProgressTasks: number;
    completedThisWeek: number;
    activeOutputs: number;
    tasksDueSoon: number;
    tasksOverdue: number;
    openPendingMatters: number;
    openFollowUps: number;
    pendingApprovals: number;
  };
  tasksByStatus: { status: TaskStatus; count: number }[];
  attention: {
    type: "TASK" | "FOLLOW_UP";
    id: string;
    title: string;
    category: "Tugas" | "Tindak lanjut";
    workStatus: string;
    assigneeName: string | null;
    ownerTeamCode: string | null;
    dueDate: string;
    deadlineState: DeadlineState;
  }[];
  recentKnowledge: {
    id: string;
    title: string;
    knowledgeType: string;
    ownerTeamCode: string | null;
    updatedAt: string;
  }[];
  referenceDate: string;
}

export interface HermesCitation {
  index: number;
  knowledgeEntryId: string;
  documentChunkId: string;
  title: string;
  sectionLabel: string;
  versionLabel: string;
  knowledgeType: string;
  classificationCode: ClassificationCode;
}

export interface HermesFollowUp {
  status: "NEEDS_CLARIFICATION" | "NEEDS_AUTHORIZED_REVIEW";
  title: string;
  guidance: string;
  clarificationPrompt: string | null;
}

export interface HermesAnswer {
  conversationId: string;
  messageId: string;
  decision: HermesDecision;
  reason: string;
  answer: string;
  citations: HermesCitation[];
  excludedPassages: number;
  approvalRequestId: string | null;
  followUp: HermesFollowUp | null;
  searchAttempts: number;
}

// Request schemas ---------------------------------------------------------------

export const devLoginSchema = z.object({
  email: z
    .string()
    .trim()
    .toLowerCase()
    .regex(/^[^@\s]+@sunovate\.local$/, "Gunakan email pengguna simulasi @sunovate.local"),
});
export type DevLoginInput = z.infer<typeof devLoginSchema>;

export const hermesQuerySchema = z.object({
  question: z
    .string()
    .trim()
    .min(3, "Pertanyaan minimal 3 karakter")
    .max(2000, "Pertanyaan maksimal 2000 karakter"),
  conversationId: z.uuid().optional(),
});
export type HermesQueryInput = z.infer<typeof hermesQuerySchema>;

export const hermesFeedbackSchema = z.object({
  messageId: z.uuid(),
  rating: z.enum(["HELPFUL", "NOT_HELPFUL"]),
});
export type HermesFeedbackInput = z.infer<typeof hermesFeedbackSchema>;

/** Seeded SIMULATED_DATA development accounts (fictional). */
export const SIMULATED_USERS = [
  { email: "sim.admin@sunovate.local", role: "system_admin" },
  { email: "sim.coordinator@sunovate.local", role: "knowledge_coordinator" },
  { email: "sim.lead.psun@sunovate.local", role: "team_lead" },
  { email: "sim.owner.ppsun@sunovate.local", role: "knowledge_owner" },
  { email: "sim.reviewer.akpsun@sunovate.local", role: "reviewer" },
  { email: "sim.staff.pppsun@sunovate.local", role: "staff" },
  { email: "sim.auditor@sunovate.local", role: "auditor" },
  { email: "sim.readonly.dhtv@sunovate.local", role: "read_only" },
] as const;

/** RAHASIA documents are only ever shown as watermarked page images (ADR-020). */
export interface SecureDocumentSummary {
  id: string;
  title: string;
  classificationCode: string;
  ownerTeamCode: string;
  pageCount: number;
  handling: "VIEW_ONLY";
}
