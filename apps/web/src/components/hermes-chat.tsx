"use client";

import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import {
  hermesQuerySchema,
  type ApiErrorBody,
  type Envelope,
  type HermesAnswer,
  type HermesQueryInput,
} from "@sunovate/contracts";
import { HERMES_DECISION_LABELS } from "@sunovate/shared-types";
import { zodResolver } from "@/lib/zod-resolver";
import { classificationLabel } from "@/lib/ui-labels";
import { StatusTag, type Tone } from "./page-elements";

interface Turn {
  question: string;
  answer: HermesAnswer;
}

async function askHermes(input: HermesQueryInput): Promise<HermesAnswer> {
  const response = await fetch("/api/hermes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
    throw new Error(body?.message ?? "SAVI AI tidak dapat menjawab saat ini");
  }
  return ((await response.json()) as Envelope<HermesAnswer>).data;
}

async function sendFeedback(messageId: string, rating: "HELPFUL" | "NOT_HELPFUL"): Promise<void> {
  const response = await fetch("/api/hermes/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messageId, rating }),
  });
  if (!response.ok) throw new Error("Penilaian belum dapat dikirim");
}

function decisionTone(decision: HermesAnswer["decision"]): Tone {
  if (decision === "ANSWERED") return "success";
  if (decision === "REQUIRES_HUMAN_APPROVAL" || decision === "INSUFFICIENT_EVIDENCE") return "warning";
  return "risk";
}

export function HermesChat() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [rated, setRated] = useState<Record<string, string>>({});
  const conversationId = turns.at(-1)?.answer.conversationId;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<HermesQueryInput>({ resolver: zodResolver(hermesQuerySchema) });

  const ask = useMutation({
    mutationFn: askHermes,
    onSuccess: (answer, input) => {
      setTurns((previous) => [...previous, { question: input.question, answer }]);
      reset({ question: "" });
    },
  });
  const feedback = useMutation({
    mutationFn: ({ messageId, rating }: { messageId: string; rating: "HELPFUL" | "NOT_HELPFUL" }) =>
      sendFeedback(messageId, rating),
    onSuccess: (_, variables) => setRated((r) => ({ ...r, [variables.messageId]: variables.rating })),
  });

  const onSubmit = handleSubmit((values) =>
    ask.mutate(conversationId ? { ...values, conversationId } : values),
  );

  return (
    <div className="chat">
      <div className="chat-log" aria-live="polite" aria-busy={ask.isPending}>
        {turns.length === 0 ? (
          <p className="muted">
            Ajukan pertanyaan tentang pengetahuan SUN yang boleh Anda akses. Contoh: Informasi apa
            saja yang wajib dicatat saat mendaftarkan dokumen?
          </p>
        ) : null}
        {turns.map(({ question, answer }) => (
          <article className="chat-turn" key={answer.messageId}>
            <p className="chat-question">
              <span className="sr-only">Pertanyaan: </span>
              {question}
            </p>
            <div className="chat-answer">
              <StatusTag tone={decisionTone(answer.decision)}>
                {HERMES_DECISION_LABELS[answer.decision]}
              </StatusTag>
              <p className="answer-text">{answer.answer}</p>
              {answer.citations.length ? (
                <ol className="citations" aria-label="Sumber">
                  {answer.citations.map((citation) => (
                    <li key={citation.index}>
                      <span className="cite-index">[{citation.index}]</span>{" "}
                      <Link href={`/knowledge/${citation.knowledgeEntryId}`}>{citation.title}</Link>
                      <span>
                        {" "}
                        - {citation.sectionLabel} - {citation.versionLabel} -{" "}
                        {classificationLabel(citation.classificationCode)}
                      </span>
                    </li>
                  ))}
                </ol>
              ) : null}
              {answer.approvalRequestId ? (
                <p className="muted">
                  Permintaan persetujuan telah dicatat. Tidak ada perubahan data yang dijalankan
                  sebelum petugas berwenang memberikan keputusan.
                </p>
              ) : null}
              {answer.excludedPassages > 0 ? (
                <p className="muted">
                  {answer.excludedPassages} bagian sumber diabaikan karena berisi teks menyerupai
                  instruksi.
                </p>
              ) : null}
              <div className="feedback" role="group" aria-label="Penilaian jawaban">
                {rated[answer.messageId] ? (
                  <span className="muted">Terima kasih, penilaian Anda telah dicatat.</span>
                ) : (
                  <>
                    <button
                      className="button secondary"
                      type="button"
                      onClick={() => feedback.mutate({ messageId: answer.messageId, rating: "HELPFUL" })}
                    >
                      Membantu
                    </button>
                    <button
                      className="button secondary"
                      type="button"
                      onClick={() =>
                        feedback.mutate({ messageId: answer.messageId, rating: "NOT_HELPFUL" })
                      }
                    >
                      Tidak membantu
                    </button>
                  </>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>

      <form className="chat-form" onSubmit={onSubmit} noValidate>
        <label htmlFor="question">Pertanyaan untuk SAVI AI</label>
        <textarea
          id="question"
          rows={3}
          aria-invalid={errors.question ? "true" : "false"}
          aria-describedby={errors.question ? "question-error" : undefined}
          {...register("question")}
        />
        {errors.question ? (
          <p className="field-error" id="question-error" role="alert">
            {errors.question.message}
          </p>
        ) : null}
        {ask.isError ? (
          <p className="field-error" role="alert">
            {ask.error.message}
          </p>
        ) : null}
        <button className="button" type="submit" disabled={ask.isPending}>
          {ask.isPending ? "SAVI AI sedang memeriksa sumber..." : "Kirim pertanyaan"}
        </button>
      </form>
    </div>
  );
}
