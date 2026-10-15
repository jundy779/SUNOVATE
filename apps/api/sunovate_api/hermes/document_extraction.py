"""Bounded in-memory extraction for explicitly simulated development files.

No source file is persisted, uploaded to a provider, indexed, or sent to an
external service. Production ingestion requires a separate approved design.
"""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePath

from docx import Document
from pypdf import PdfReader

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_EXTRACTED_CHARACTERS = 100_000
MAX_PDF_PAGES = 50
MAX_DOCX_ENTRIES = 500
MAX_DOCX_UNCOMPRESSED_BYTES = 10 * 1024 * 1024

_SIMULATED_NAME = re.compile(r"^simulasi(?:[-_. ]|$)", re.IGNORECASE)
_ALLOWED_TYPES: dict[str, frozenset[str]] = {
    ".txt": frozenset({"text/plain", "application/octet-stream", ""}),
    ".md": frozenset({"text/markdown", "text/plain", "application/octet-stream", ""}),
    ".pdf": frozenset({"application/pdf", "application/octet-stream", ""}),
    ".docx": frozenset(
        {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/octet-stream",
            "",
        }
    ),
}


class ExtractionRejected(ValueError):
    """Expected validation failure safe to show as a fixed user-facing message."""


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    text: str
    extension: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    page_count: int | None
    paragraph_count: int | None


def _clean(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip() for line in normalized.split("\n"))
    return re.sub(r"\n{4,}", "\n\n\n", normalized).strip()


def _validate_text(text: str) -> str:
    cleaned = _clean(text)
    if len(cleaned) < 20:
        raise ExtractionRejected("Isi berkas terlalu singkat untuk diperiksa")
    if len(cleaned) > MAX_EXTRACTED_CHARACTERS:
        raise ExtractionRejected("Isi hasil pembacaan melebihi batas 100.000 karakter")
    return cleaned


def _extract_plain(payload: bytes) -> tuple[str, None, None]:
    if b"\x00" in payload:
        raise ExtractionRejected("Berkas teks mengandung data biner yang tidak didukung")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ExtractionRejected("Berkas teks harus menggunakan penyandian UTF-8") from exc
    return text, None, None


def _extract_pdf(payload: bytes) -> tuple[str, int, None]:
    if not payload.startswith(b"%PDF-"):
        raise ExtractionRejected("Isi berkas tidak sesuai dengan format PDF")
    try:
        reader = PdfReader(io.BytesIO(payload), strict=True)
        if reader.is_encrypted:
            raise ExtractionRejected("PDF terenkripsi belum dapat diperiksa")
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ExtractionRejected("PDF simulasi dibatasi maksimal 50 halaman")
        parts: list[str] = []
        total = 0
        for page in reader.pages:
            content = page.extract_text() or ""
            total += len(content)
            if total > MAX_EXTRACTED_CHARACTERS:
                raise ExtractionRejected("Isi hasil pembacaan melebihi batas 100.000 karakter")
            parts.append(content)
        return "\n\n".join(parts), len(reader.pages), None
    except ExtractionRejected:
        raise
    except Exception as exc:
        raise ExtractionRejected("PDF tidak dapat dibaca dengan aman") from exc


def _docx_preflight(payload: bytes) -> None:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            entries = archive.infolist()
            names = {entry.filename.lower() for entry in entries}
            if len(entries) > MAX_DOCX_ENTRIES:
                raise ExtractionRejected("Struktur DOCX terlalu kompleks untuk tahap simulasi")
            if sum(entry.file_size for entry in entries) > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise ExtractionRejected("Ukuran isi DOCX setelah dibuka melebihi batas aman")
            if "[content_types].xml" not in names or "word/document.xml" not in names:
                raise ExtractionRejected("Isi berkas tidak sesuai dengan format DOCX")
            if any(name.endswith("vbaproject.bin") for name in names):
                raise ExtractionRejected("Dokumen yang mengandung makro tidak diizinkan")
    except ExtractionRejected:
        raise
    except (zipfile.BadZipFile, OSError) as exc:
        raise ExtractionRejected("DOCX tidak dapat dibaca dengan aman") from exc


def _extract_docx(payload: bytes) -> tuple[str, None, int]:
    _docx_preflight(payload)
    try:
        document = Document(io.BytesIO(payload))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        for table in document.tables:
            for row in table.rows:
                paragraphs.append(" | ".join(cell.text.strip() for cell in row.cells))
        return "\n\n".join(paragraphs), None, len(paragraphs)
    except Exception as exc:
        raise ExtractionRejected("DOCX tidak dapat dibaca dengan aman") from exc


def extract_simulated_document(
    *, filename: str, content_type: str | None, payload: bytes
) -> ExtractedDocument:
    """Extract a bounded simulated file after extension, MIME, and structure checks."""
    safe_name = PurePath(filename.replace("\\", "/")).name
    extension = PurePath(safe_name).suffix.lower()
    if not _SIMULATED_NAME.match(safe_name):
        raise ExtractionRejected("Nama berkas harus diawali 'SIMULASI'")
    if extension not in _ALLOWED_TYPES:
        raise ExtractionRejected("Gunakan berkas simulasi berformat TXT, MD, PDF, atau DOCX")
    mime = (content_type or "").lower().split(";", 1)[0].strip()
    if mime not in _ALLOWED_TYPES[extension]:
        raise ExtractionRejected("Jenis berkas tidak sesuai dengan nama berkas")
    if not payload:
        raise ExtractionRejected("Berkas simulasi kosong")
    if len(payload) > MAX_FILE_BYTES:
        raise ExtractionRejected("Ukuran berkas simulasi dibatasi maksimal 2 MB")

    if extension in {".txt", ".md"}:
        text, pages, paragraphs = _extract_plain(payload)
    elif extension == ".pdf":
        text, pages, paragraphs = _extract_pdf(payload)
    else:
        text, pages, paragraphs = _extract_docx(payload)

    return ExtractedDocument(
        text=_validate_text(text),
        extension=extension,
        mime_type={
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }[extension],
        size_bytes=len(payload),
        checksum_sha256=sha256(payload).hexdigest(),
        page_count=pages,
        paragraph_count=paragraphs,
    )
