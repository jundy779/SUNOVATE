"""Rule-based ScopeGuard (development). Known to have false positives/negatives.

Evaluation order: policy override -> financial decision -> general coding ->
write intent -> SUN domain. See docs/05-ai-rag/scope-guard.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

POLICY_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\babaikan\s+(semua\s+|seluruh\s+)?(instruksi|aturan|kebijakan|perintah)",
        r"\bignore\s+(all\s+|any\s+|previous\s+|prior\s+|the\s+)*(instructions|rules|policies)",
        r"\bsystem\s*prompt\b",
        r"\bjailbreak\b",
        r"\bdeveloper\s+mode\b",
        r"\btanpa\s+(batasan|filter|pemeriksaan\s+izin|otorisasi)\b",
        r"\b(lewati|bypass|abaikan)\s+(otorisasi|izin|pemeriksaan|keamanan|authorization)\b",
        r"\bberpura[- ]pura\b",
        r"\bpretend\s+(you|to)\b",
        r"\b(tampilkan|bocorkan|buka)\s+(seluruh\s+|semua\s+)?(dokumen|data)\s+"
        r"(rahasia|terbatas|confidential)",
        r"\binstruksi\s+(untuk|kepada)\s+(ai|asisten|hermes|model)\b",
    )
)

FINANCIAL_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bsebaiknya\s+(di)?(beli|jual|lepas)",
        r"\brekomendasi(kan)?\s+(investasi|beli|jual|seri)",
        r"\bharga\s+wajar\b",
        r"\bprediksi\s+(yield|imbal\s+hasil|harga|kupon)",
        r"\b(should\s+i\s+(buy|sell)|investment\s+advice)\b",
    )
)

CODING_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(python|javascript|typescript|golang|php|html|css|regex|kotlin|rust)\b",
        r"\bbuat(kan)?\s+(kode|program|fungsi|script|skrip|aplikasi|query\s+sql)\b",
        r"\b(write|generate|fix|debug)\s+(the\s+|a\s+|some\s+|my\s+)?(code|script|function)\b",
        r"\b(coding|ngoding|debugging)\b",
    )
)

WRITE_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\b(hapus|hapuskan|ubah|ubahlah|perbarui|perbaharui|tambahkan|setujui|publikasikan|"
        r"terbitkan|arsipkan|kirim|kirimkan|tugaskan)\b",
        r"\bbuat(kan)?\s+(tugas|entri|knowledge|pending|tindak\s+lanjut|approval)\b",
        r"\b(delete|approve|publish|create|send|assign)\b",
    )
)

DOMAIN_TERMS = (
    "sun",
    "surat utang",
    "obligasi",
    "spn",
    "sbn",
    "lelang",
    "buyback",
    "debt switch",
    "private placement",
    "bookbuilding",
    "regulasi",
    "peraturan",
    "pmk",
    "undang-undang",
    "sop",
    "playbook",
    "kajian",
    "close out",
    "lesson learned",
    "knowledge",
    "dokumen",
    "rapat",
    "tim",
    "ppsun",
    "akpsun",
    "psun",
    "pppsun",
    "dhtv",
    "tematik",
    "pending",
    "tindak lanjut",
    "output",
    "tugas",
    "milestone",
    "metadata",
    "klasifikasi",
    "dealer",
    "ritel",
    "setelmen",
    "portofolio",
    "pasar",
    "valas",
    "edukasi",
    "arsip",
    "bahan",
    "referensi",
    "entri",
    "catatan",
    "keputusan",
    "review",
    "hermes",
    "sunovate",
)
_DOMAIN = re.compile(r"\b(" + "|".join(re.escape(t) for t in DOMAIN_TERMS) + r")\b", re.IGNORECASE)


@dataclass(frozen=True)
class ScopeDecision:
    decision: str | None  # None => in scope, continue pipeline
    reason: str
    message: str


IN_SCOPE = ScopeDecision(None, "in_scope", "")


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def is_instruction_like(text: str) -> bool:
    """Used for both user questions and retrieved passages (indirect injection)."""
    return _matches(POLICY_PATTERNS, text)


class ScopeGuard:
    def evaluate(self, question: str) -> ScopeDecision:
        text = " ".join(question.split())
        if is_instruction_like(text):
            return ScopeDecision(
                "REFUSED_POLICY",
                "policy_override",
                "Permintaan ditolak karena mencoba mengubah atau melewati kebijakan sistem.",
            )
        if _matches(FINANCIAL_PATTERNS, text):
            return ScopeDecision(
                "REFUSED_POLICY",
                "financial_decision",
                "Hermes tidak memberikan rekomendasi atau keputusan keuangan. Silakan merujuk "
                "pada proses dan pejabat yang berwenang.",
            )
        if _matches(CODING_PATTERNS, text):
            return ScopeDecision(
                "REFUSED_GENERAL_CODING",
                "general_coding",
                "Hermes hanya melayani pertanyaan knowledge domain SUN, bukan bantuan pemrograman.",
            )
        if _matches(WRITE_PATTERNS, text):
            return ScopeDecision(
                "REQUIRES_HUMAN_APPROVAL",
                "write_intent",
                "Hermes tidak menjalankan perubahan data. Permintaan dicatat sebagai usulan yang "
                "memerlukan persetujuan manusia yang berwenang.",
            )
        if not _DOMAIN.search(text):
            return ScopeDecision(
                "REFUSED_OUT_OF_SCOPE",
                "out_of_domain",
                "Pertanyaan berada di luar domain SUN dan knowledge Direktorat SUN.",
            )
        return IN_SCOPE
