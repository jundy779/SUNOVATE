"use client";

import Link from "next/link";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
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

const STARTER_QUESTIONS = [
  "Apa metadata wajib saat mendaftarkan dokumen?",
  "Apa materi edukasi SUN ritel?",
] as const;

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
    setValue,
    control,
    formState: { errors },
  } = useForm<HermesQueryInput>({ resolver: zodResolver(hermesQuerySchema) });
  const question = useWatch({ control, name: "question" }) ?? "";

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

  const startNewConversation = () => {
    setTurns([]);
    setRated({});
    reset({ question: "" });
    ask.reset();
    feedback.reset();
  };

  return (
    <div className="chat">
      <div className="chat-log" aria-live="polite" aria-busy={ask.isPending}>
        {turns.length === 0 ? (
          <section className="savi-welcome" aria-labelledby="savi-welcome-title">
            <div>
              <h3 id="savi-welcome-title">Mulai dari pertanyaan tentang SUN</h3>
              <p>
                SAVI AI akan memeriksa bahan terbit dalam cakupan akses Anda. Pilih contoh atau
                tulis pertanyaan sendiri.
              </p>
            </div>
            <div className="savi-starter-questions" aria-label="Contoh pertanyaan">
              {STARTER_QUESTIONS.map((starter) => (
                <button
                  type="button"
                  key={starter}
                  disabled={ask.isPending}
                  onClick={() => setValue("question", starter, { shouldValidate: true })}
                >
                  {starter}
                </button>
              ))}
            </div>
          </section>
        ) : null}
        {turns.map(({ question, answer }) => (
          <article className="chat-turn" key={answer.messageId}>
            <p className="chat-question">
              <span className="sr-only">Pertanyaan: </span>
              {question}
            </p>
            <div className="chat-answer">
              <header className="savi-answer-header">
                <StatusTag tone={decisionTone(answer.decision)}>
                  {HERMES_DECISION_LABELS[answer.decision]}
                </StatusTag>
                <span>
                  {answer.citations.length
                    ? `${answer.citations.length} rujukan digunakan`
                    : "Tanpa rujukan karena jawaban tidak diteruskan"}
                </span>
              </header>
              <p className="answer-text">{answer.answer}</p>
              {answer.followUp ? (
                <section className="savi-follow-up" aria-label="Langkah berikutnya">
                  <h3>{answer.followUp.title}</h3>
                  <p>{answer.followUp.guidance}</p>
                  {answer.searchAttempts > 1 ? (
                    <p>SAVI AI telah mencoba pencarian lanjutan satu kali.</p>
                  ) : null}
                  {answer.followUp.clarificationPrompt ? (
                    <p>
                      <strong>Agar pertanyaan lebih jelas:</strong>{" "}
                      {answer.followUp.clarificationPrompt}
                    </p>
                  ) : null}
                  <p className="muted">
                    SAVI AI tidak mengirim permintaan kepada pegawai dan tidak menerbitkan informasi
                    secara otomatis.
                  </p>
                </section>
              ) : null}
              {answer.citations.length ? (
                <section className="savi-sources" aria-labelledby={`sources-${answer.messageId}`}>
                  <h3 id={`sources-${answer.messageId}`}>Sumber yang digunakan</h3>
                  <ol className="citations">
                    {answer.citations.map((citation) => (
                      <li key={citation.index}>
                        <span className="cite-index">[{citation.index}]</span>
                        <span>
                          <Link href={`/knowledge/${citation.knowledgeEntryId}`}>{citation.title}</Link>
                          <small>
                            {citation.sectionLabel} · {citation.versionLabel} ·{" "}
                            {classificationLabel(citation.classificationCode)}
                          </small>
                        </span>
                      </li>
                    ))}
                  </ol>
                </section>
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
              {feedback.isError ? (
                <p className="field-error" role="alert">
                  {feedback.error.message}
                </p>
              ) : null}
            </div>
          </article>
        ))}
      </div>

      <form className="chat-form" onSubmit={onSubmit} noValidate>
        <div className="savi-form-heading">
          <label htmlFor="question">Pertanyaan untuk SAVI AI</label>
          {turns.length ? (
            <button className="text-button" type="button" onClick={startNewConversation}>
              Mulai percakapan baru
            </button>
          ) : null}
        </div>
        <textarea
          id="question"
          rows={3}
          maxLength={2000}
          placeholder="Tulis pertanyaan yang jelas, misalnya nama dokumen, periode, proses, atau unit terkait."
          aria-invalid={errors.question ? "true" : "false"}
          aria-describedby={errors.question ? "question-error question-count" : "question-count"}
          {...register("question")}
        />
        <p className="savi-question-count" id="question-count">
          {question.length}/2000 karakter
        </p>
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
