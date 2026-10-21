"""Server-side page rendering for the view-only viewer (ADR-020).

The browser only ever receives a raster image of one page. Text is never sent, so it cannot be
selected or copied, and every image carries a watermark identifying the viewer, the time, and
the session. A determined person can still photograph a screen; the watermark makes that
traceable.
"""

from __future__ import annotations

import io
import textwrap
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

PAGE_SIZE = (1240, 1754)  # A4 at 150 dpi
_MARGIN = 120
_NAVY = (13, 46, 94)
_MUTED = (107, 114, 128)
_GOLD = (201, 162, 39)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.load_default(size=size)


def watermark_label(*, display_name: str, email: str, viewed_at: datetime, session_ref: str) -> str:
    return f"{display_name}  {email}  {viewed_at:%d-%m-%Y %H:%M} WIB  sesi {session_ref}"


def render_page(
    *,
    title: str,
    page_number: int,
    page_count: int,
    body: str,
    watermark: str,
) -> bytes:
    page = Image.new("RGB", PAGE_SIZE, "white")
    draw = ImageDraw.Draw(page)
    draw.rectangle((_MARGIN, _MARGIN - 40, _MARGIN + 64, _MARGIN - 30), fill=_GOLD)
    draw.text((_MARGIN, _MARGIN), title, fill=_NAVY, font=_font(40))
    draw.text(
        (_MARGIN, _MARGIN + 64),
        f"Halaman {page_number} dari {page_count}  |  Dokumen rahasia, hanya untuk dibaca",
        fill=_MUTED,
        font=_font(24),
    )
    y = _MARGIN + 150
    body_font = _font(28)
    for paragraph in body.split("\n"):
        for line in textwrap.wrap(paragraph, width=62) or [""]:
            draw.text((_MARGIN, y), line, fill=(31, 41, 55), font=body_font)
            y += 44
        y += 18

    _apply_watermark(page, watermark)
    buffer = io.BytesIO()
    page.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _apply_watermark(page: Image.Image, label: str) -> None:
    """Tile the label diagonally across the whole page so cropping cannot remove it."""
    tile = Image.new("RGBA", (PAGE_SIZE[0] * 2, PAGE_SIZE[1] * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tile)
    font = _font(30)
    step_y = 210
    step_x = int(draw.textlength(label, font=font)) + 160
    for row, y in enumerate(range(0, tile.height, step_y)):
        offset = (row % 2) * (step_x // 2)
        for x in range(-offset, tile.width, step_x):
            draw.text((x, y), label, fill=(13, 46, 94, 46), font=font)
    rotated = tile.rotate(30, resample=Image.Resampling.BICUBIC)
    left = (rotated.width - PAGE_SIZE[0]) // 2
    top = (rotated.height - PAGE_SIZE[1]) // 2
    overlay = rotated.crop((left, top, left + PAGE_SIZE[0], top + PAGE_SIZE[1]))
    page.paste(overlay, (0, 0), overlay)
