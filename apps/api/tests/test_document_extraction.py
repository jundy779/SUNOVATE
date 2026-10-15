"""Bounded extraction tests for explicitly simulated files."""

from __future__ import annotations

import io
import zipfile

import pytest
import xlwt
from docx import Document
from openpyxl import Workbook

from sunovate_api.hermes.document_extraction import (
    MAX_FILE_BYTES,
    ExtractionRejected,
    extract_simulated_document,
)


def test_extracts_utf8_text_without_persisting_source() -> None:
    payload = b"Pasal 1\nIsi simulasi yang cukup panjang untuk diperiksa oleh sistem."

    result = extract_simulated_document(
        filename="SIMULASI-contoh.txt", content_type="text/plain", payload=payload
    )

    assert result.text.startswith("Pasal 1")
    assert result.extension == ".txt"
    assert result.size_bytes == len(payload)
    assert len(result.checksum_sha256) == 64


def test_extracts_docx_paragraphs_and_tables() -> None:
    document = Document()
    document.add_paragraph("SIMULASI dokumen untuk pemeriksaan isi yang aman dan terbatas.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "Kolom satu"
    table.cell(0, 1).text = "Kolom dua"
    buffer = io.BytesIO()
    document.save(buffer)

    result = extract_simulated_document(
        filename="SIMULASI-dokumen.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        payload=buffer.getvalue(),
    )

    assert "Kolom satu | Kolom dua" in result.text
    assert result.paragraph_count == 2


def test_extracts_xlsx_values_without_executing_formulas() -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Hasil Lelang"
    worksheet.append(["Seri", "Nominal", "Catatan"])
    worksheet.append(["SIMULASI-FR", 1_000_000, "Data untuk pemeriksaan manusia"])
    worksheet.append(["Rumus", "=1+1", None])
    buffer = io.BytesIO()
    workbook.save(buffer)

    result = extract_simulated_document(
        filename="SIMULASI-hasil-lelang.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        payload=buffer.getvalue(),
    )

    assert "Lembar: Hasil Lelang" in result.text
    assert "SIMULASI-FR | 1000000 | Data untuk pemeriksaan manusia" in result.text
    assert "=1+1" not in result.text
    assert result.sheet_count == 1


def test_extracts_legacy_xls_values() -> None:
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet("Rekonsiliasi")
    rows = [
        ("Seri", "Status"),
        ("SIMULASI-FR", "Perlu pemeriksaan manusia"),
    ]
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            worksheet.write(row_index, column_index, value)
    buffer = io.BytesIO()
    workbook.save(buffer)

    result = extract_simulated_document(
        filename="SIMULASI-rekonsiliasi.xls",
        content_type="application/vnd.ms-excel",
        payload=buffer.getvalue(),
    )

    assert "Lembar: Rekonsiliasi" in result.text
    assert "SIMULASI-FR | Perlu pemeriksaan manusia" in result.text
    assert result.sheet_count == 1


@pytest.mark.parametrize(
    ("filename", "content_type", "payload", "message"),
    [
        ("dokumen.txt", "text/plain", b"Isi simulasi yang panjang dan aman.", "diawali"),
        ("SIMULASI.exe", "application/octet-stream", b"data", "XLSX, atau XLS"),
        ("SIMULASI.txt", "text/plain", b"teks\x00biner yang tidak aman", "data biner"),
        ("SIMULASI.pdf", "application/pdf", b"bukan pdf yang valid", "format PDF"),
        ("SIMULASI.xls", "application/vnd.ms-excel", b"bukan xls", "format XLS"),
        ("SIMULASI.txt", "text/plain", b"a" * (MAX_FILE_BYTES + 1), "maksimal 2 MB"),
    ],
)
def test_rejects_unsafe_or_mislabelled_files(
    filename: str, content_type: str, payload: bytes, message: str
) -> None:
    with pytest.raises(ExtractionRejected, match=message):
        extract_simulated_document(
            filename=filename, content_type=content_type, payload=payload
        )


def test_rejects_macro_payload_before_docx_parsing() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr("word/document.xml", "<document />")
        archive.writestr("word/vbaProject.bin", b"macro")

    with pytest.raises(ExtractionRejected, match="makro"):
        extract_simulated_document(
            filename="SIMULASI-makro.docx",
            content_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            payload=buffer.getvalue(),
        )
