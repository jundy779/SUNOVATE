"""Rule-based ScopeGuard (development). Known to have false positives/negatives.

Evaluation order: policy override -> financial decision -> general coding ->
write intent -> SUN domain. See docs/05-ai-rag/scope-guard.md.
"""

from __future__ import annotations

import re
import unicodedata
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
        r"\b(act|behave|respond)\s+as\s+(an?\s+)?(unrestricted|uncensored|unfiltered|root)\b",
        r"\b(do\s+anything\s+now|dan\s+mode)\b",
        r"\b(disregard|override)\s+(the\s+|all\s+|any\s+)*(instructions|rules|policies|guardrails)\b",
        r"\b(reveal|show|print|repeat|expose)\s+(the\s+|your\s+|hidden\s+|internal\s+)*"
        r"(instructions|system\s*prompt|developer\s*message|guardrails)\b",
        r"\b(ungkapkan|tunjukkan|salin|bocorkan)\s+(instruksi\s+internal|instruksi\s+tersembunyi|"
        r"pesan\s+developer|guardrail)\b",
        r"\b(tampilkan|bocorkan|ungkapkan|berikan)\s+(api[_ -]?key|token|secret|password|"
        r"kata\s+sandi|kredensial)\b",
        r"\b(tampilkan|bocorkan|buka)\s+(seluruh\s+|semua\s+)?(dokumen|data)\s+"
        r"(rahasia|terbatas|confidential)",
        r"\b(akses|buka|rangkum)\s+(dokumen|data|file)\s+(tim\s+lain|yang\s+bukan\s+hak|"
        r"tanpa\s+izin)\b",
        r"\binstruksi\s+(untuk|kepada)\s+(ai|asisten|hermes|model)\b",
        r"\b(kirim|unggah|upload|bagikan|salin|ekspor|export|teruskan|forward)\b.{0,80}"
        r"\b(chatgpt|claude|gemini|copilot|ai\s+eksternal|model\s+eksternal|agent\s+eksternal|"
        r"mcp|plugin|webhook|url\s+publik)\b",
        r"\b(publikasikan|terbitkan|indeks(kan)?|masukkan)\b.{0,80}"
        r"\b(search\s*engine|mesin\s+pencari|ai\s*search|seo|geo|aio|crawler|scraper|publik|umum)\b",
        r"\b(buat|jadikan)\b.{0,50}\b(dokumen|data|isi|jawaban)\b.{0,50}"
        r"\b(dapat\s+dicari|terindeks|publik|terbuka\s+untuk\s+umum)\b",
        r"\b(base64|rot13|hex(?:adecimal)?|obfuscate|samarkan|encode)\b.{0,80}"
        r"\b(dokumen|data|rahasia|terbatas|confidential|instruksi|prompt)\b",
        r"\b(pecah|bagi|split)\b.{0,50}\b(dokumen|data|rahasia|terbatas)\b.{0,50}"
        r"\b(pesan|bagian|chunk)\b",
        r"\bgunakan\s+(browser|tool|alat|mcp|agent)\b.{0,80}\b(kirim|unggah|bocorkan|ekspor|publik)\b",
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
        r"\b(pilihkan|tentukan)\s+(seri\s+)?(sun|sbn|obligasi)\s+.*\b(untung|menguntungkan|beli)",
        r"\b(sun|sbn|obligasi)\s+mana\s+.*\b(paling\s+)?(untung|menguntungkan)\b",
        r"\bstrategi\s+(trading|jual\s+beli)\s+(sun|sbn|obligasi)\b",
    )
)

CODING_ACTION_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bbuat(kan)?\s+(kode|program|fungsi|script|skrip|aplikasi|query\s+sql)\b",
        r"\b(write|generate|fix|debug)\s+(the\s+|a\s+|some\s+|my\s+)?(code|script|function)\b",
        r"\b(coding|ngoding|debugging)\b",
    )
)

PROGRAMMING_LANGUAGE = re.compile(
    r"\b(python|javascript|typescript|golang|php|html|css|regex|kotlin|rust)\b",
    re.IGNORECASE,
)

WRITE_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"(?:^|\b(?:tolong|mohon|coba|segera)\s+)"
        r"(hapus|ubah|perbarui|perbaharui|tambah|setujui|publikasi|terbitkan|arsipkan|kirim|tugaskan)\b",
        r"\b(hapuskan|ubahlah|tambahkan|setujui|publikasikan|terbitkan|arsipkan|kirimkan|tugaskan)\b",
        r"\bbuat(kan)?\s+(tugas|entri|knowledge|pending|tindak\s+lanjut|approval)\b",
        r"(?:^|\bplease\s+)(delete|approve|publish|create|send|assign)\b",
        r"\b(saya|aku)\s+(ingin|mau)\s+(menghapus|mengubah|memperbarui|menambah|"
        r"menerbitkan|mengarsipkan|mengirim|menugaskan)\b",
    )
)

STRONG_DOMAIN_TERMS = (
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
    "ppsun",
    "akpsun",
    "psun",
    "pppsun",
    "dhtv",
    "sun tematik",
    "klasifikasi",
    "dealer",
    "ritel",
    "setelmen",
    "portofolio",
    "valas",
    "hermes",
    "sunovate",
)
_STRONG_DOMAIN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in STRONG_DOMAIN_TERMS) + r")\b", re.IGNORECASE
)

CONTEXTUAL_DOMAIN_PAIRS = tuple(
    tuple(re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in pair)
    for pair in (
        ("metadata", "dokumen"),
        ("metadata", "knowledge"),
        ("entri", "knowledge"),
        ("kajian", "pasar"),
        ("catatan", "keputusan"),
        ("output", "tim"),
        ("tugas", "tim"),
        ("pending", "tindak lanjut"),
        ("milestone", "output"),
        ("bahan", "rapat"),
        ("arsip", "dokumen"),
    )
)


@dataclass(frozen=True)
class ScopeDecision:
    decision: str | None  # None => in scope, continue pipeline
    reason: str
    message: str


IN_SCOPE = ScopeDecision(None, "in_scope", "")


def _matches(patterns: tuple[re.Pattern[str], ...], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    without_format_chars = "".join(ch for ch in normalized if unicodedata.category(ch) != "Cf")
    return " ".join(without_format_chars.split())


def _has_domain_context(text: str) -> bool:
    return bool(_STRONG_DOMAIN.search(text)) or any(
        all(pattern.search(text) for pattern in pair) for pair in CONTEXTUAL_DOMAIN_PAIRS
    )


def _is_general_coding(text: str) -> bool:
    if _matches(CODING_ACTION_PATTERNS, text):
        return True
    return bool(PROGRAMMING_LANGUAGE.search(text)) and not _has_domain_context(text)


def is_instruction_like(text: str) -> bool:
    """Used for both user questions and retrieved passages (indirect injection)."""
    return _matches(POLICY_PATTERNS, _normalize(text))


class ScopeGuard:
    def evaluate(self, question: str) -> ScopeDecision:
        text = _normalize(question)
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
        if _is_general_coding(text):
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
        if not _has_domain_context(text):
            return ScopeDecision(
                "REFUSED_OUT_OF_SCOPE",
                "out_of_domain",
                "Pertanyaan berada di luar domain SUN dan knowledge Direktorat SUN.",
            )
        return IN_SCOPE
