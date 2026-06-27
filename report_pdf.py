from __future__ import annotations
import io
import math
import pandas as pd

try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


# ── Brand palette (RGB tuples) ─────────────────────────────────────────────────
PRIMARY_ORANGE = (237, 105, 9)
PRIMARY_BLUE = (2, 48, 107)
SECONDARY_BLUE = (16, 89, 159)
ACCENT_PURPLE = (159, 49, 130)
DARK_ORANGE = (164, 73, 6)
WHITE = (255, 255, 255)
OFF_WHITE = (244, 246, 251)
GRAY_LIGHT = (221, 227, 237)
GRAY_MID = (138, 150, 170)
DARK_TEXT = (30, 46, 74)


def _grade_color(grade: str):
    g = str(grade).strip().upper()
    if g.startswith("A"):
        return PRIMARY_ORANGE
    if g.startswith("B"):
        return SECONDARY_BLUE
    if g.startswith("C"):
        return ACCENT_PURPLE
    if g.startswith("D"):
        return DARK_ORANGE
    return (185, 28, 28)


def _grade_bg(grade: str):
    g = str(grade).strip().upper()
    if g.startswith("A"):
        return (253, 232, 216)
    if g.startswith("B"):
        return (214, 228, 245)
    if g.startswith("C"):
        return (240, 221, 239)
    return (254, 226, 226)


def _pct_to_arc(pdf, cx, cy, r, pct, color):
    """Filled semicircle arc, left-to-right, pct of 180 degrees."""
    start_deg = 180
    sweep = pct / 100 * 180
    steps = max(24, int(sweep * 2))
    pdf.set_fill_color(*color)
    pts = [(cx, cy)]
    for i in range(steps + 1):
        angle = math.radians(start_deg - sweep * i / steps)
        pts.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    pts.append((cx, cy))
    pdf.polygon(pts, style="F")


def generate_pdf(
    row: pd.Series, exercise: str, course: str, comments: str = ""
) -> bytes:
    if not FPDF_AVAILABLE:
        return _fallback_pdf(row, exercise, course)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()
    W, H = 210, 297
    M = 14  # margin

    gc = _grade_color(row["Grade"])
    gcbg = _grade_bg(row["Grade"])

    # ── Header gradient (two-tone rectangles) ─────────────────────────────────
    pdf.set_fill_color(*PRIMARY_BLUE)
    pdf.rect(0, 0, W, 34, style="F")
    pdf.set_fill_color(*SECONDARY_BLUE)
    pdf.rect(W * 0.55, 0, W * 0.45, 34, style="F")
    # Orange accent stripe
    pdf.set_fill_color(*PRIMARY_ORANGE)
    pdf.rect(0, 34, W, 4, style="F")

    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(M, 7)
    pdf.cell(100, 9, "REPORT CARD", ln=False)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(M, 18)
    pdf.cell(0, 5, f"Exercise: {exercise}", ln=True)
    pdf.set_x(M)
    pdf.cell(0, 4, f"Course: {course}", ln=True)

    # ── Student info block ────────────────────────────────────────────────────
    pdf.set_fill_color(*OFF_WHITE)
    pdf.rect(M, 44, W - 2 * M, 36, style="F")
    # Left accent bar
    pdf.set_fill_color(*PRIMARY_ORANGE)
    pdf.rect(M, 44, 3, 36, style="F")

    pdf.set_text_color(*PRIMARY_BLUE)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_xy(M + 7, 47)
    pdf.cell(0, 8, str(row["Name"]), ln=True)

    info_items = [
        ("Reg. No.", str(row["Registration Number"])),
        ("Username", str(row["UserName"])),
        ("Email", str(row["Email"])),
        ("Contact", str(row["Contact Number"])),
    ]
    if str(row.get("Section", "-")).strip() not in ("-", "nan"):
        info_items.append(("Section", str(row["Section"])))

    col_w = (W - 2 * M - 10) / 2
    for i, (label, val) in enumerate(info_items):
        col = i % 2
        ri = i // 2
        x = M + 7 + col * col_w
        y = 57 + ri * 9
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*GRAY_MID)
        pdf.cell(col_w * 0.36, 3.5, label.upper(), ln=False)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*DARK_TEXT)
        pdf.cell(col_w * 0.64, 3.5, val, ln=False)

    # ── Metric tiles (4 across) ───────────────────────────────────────────────
    y0 = 88
    tile_w = (W - 2 * M - 9) / 4
    tile_h = 28
    tile_accents = [PRIMARY_ORANGE, gc, SECONDARY_BLUE, ACCENT_PURPLE]
    metrics = [
        (
            "SCORE",
            f"{row['Marks Obtained']}/{row['Total Marks']}",
            f"{row['Percentage']:.1f}%",
        ),
        ("GRADE", str(row["Grade"]), ""),
        ("RANK", f"#{row['Rank']}", "in class"),
        ("ATTEMPTS", str(row["Total Attempts"]), "total tries"),
    ]

    for i, ((label, value, sub), accent) in enumerate(zip(metrics, tile_accents)):
        x = M + i * (tile_w + 3)
        pdf.set_fill_color(*GRAY_LIGHT)
        pdf.rect(x, y0, tile_w, tile_h, style="F")
        pdf.set_fill_color(*accent)
        pdf.rect(x, y0, tile_w, 2.5, style="F")

        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(*GRAY_MID)
        pdf.set_xy(x + 2, y0 + 5)
        pdf.cell(tile_w - 4, 3.5, label, align="C", ln=False)

        # Grade tile: show coloured badge
        if i == 1:
            pdf.set_fill_color(*gcbg)
            bx, bw, bh = x + tile_w * 0.2, tile_w * 0.6, 11
            pdf.rect(bx, y0 + 10, bw, bh, style="F")
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(*gc)
            pdf.set_xy(bx, y0 + 11)
            pdf.cell(bw, bh - 1, value, align="C", ln=False)
        else:
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(*DARK_TEXT)
            pdf.set_xy(x + 2, y0 + 9)
            pdf.cell(tile_w - 4, 9, value, align="C", ln=False)
            if sub:
                pdf.set_font("Helvetica", "", 6.5)
                pdf.set_text_color(*GRAY_MID)
                pdf.set_xy(x + 2, y0 + 21)
                pdf.cell(tile_w - 4, 4, sub, align="C", ln=False)

    # ── Gauge ─────────────────────────────────────────────────────────────────
    y_g = y0 + tile_h + 12
    cx = W / 2
    cy = y_g + 30
    r = 30

    # Background semicircle
    _pct_to_arc(pdf, cx, cy, r, 100, GRAY_LIGHT)
    _pct_to_arc(pdf, cx, cy, r * 0.6, 100, WHITE)
    # Zone tints
    _pct_to_arc(pdf, cx, cy, r, 40, (254, 226, 226))
    _pct_to_arc(pdf, cx, cy, r * 0.6, 100, WHITE)
    # Value fill
    _pct_to_arc(pdf, cx, cy, r, row["Percentage"], gc)
    _pct_to_arc(pdf, cx, cy, r * 0.6, 100, WHITE)

    # Centre label
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*PRIMARY_BLUE)
    pdf.set_xy(cx - 22, cy - 11)
    pdf.cell(44, 11, f"{row['Percentage']:.1f}%", align="C", ln=False)

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*GRAY_MID)
    pdf.set_xy(cx - 28, cy + 2)
    pdf.cell(56, 5, "Overall Percentage", align="C", ln=False)

    # Axis labels
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*GRAY_MID)
    pdf.set_xy(cx - r - 14, cy - 2)
    pdf.cell(14, 4, "0%", align="C")
    pdf.set_xy(cx + r, cy - 2)
    pdf.cell(14, 4, "100%", align="C")

    # ── Score progress bar ────────────────────────────────────────────────────
    y_bar = y_g + 54
    bx = M + 28
    bw = W - 2 * M - 56
    bh = 7
    fw = bw * row["Percentage"] / 100

    pdf.set_fill_color(*GRAY_LIGHT)
    pdf.rect(bx, y_bar, bw, bh, style="F")
    pdf.set_fill_color(*gc)
    pdf.rect(bx, y_bar, fw, bh, style="F")

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_xy(bx - 26, y_bar)
    pdf.cell(24, bh, "Score:", align="R", ln=False)
    pdf.set_xy(bx + bw + 2, y_bar)
    pdf.set_text_color(*gc)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(26, bh, f"{row['Percentage']:.1f}%")
    
    # ── Teacher's Comments ─────────────────────────────────────

    y_comments = y_bar + 18

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*PRIMARY_BLUE)
    pdf.set_xy(M, y_comments)
    pdf.cell(0, 6, "Teacher's Comments", ln=True)

    # Comment box
    box_y = y_comments + 7
    box_h = 28

    pdf.set_fill_color(*OFF_WHITE)
    pdf.set_draw_color(*GRAY_LIGHT)
    pdf.rect(M, box_y, W - 2 * M, box_h, style="DF")

    pdf.set_xy(M + 4, box_y + 4)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*DARK_TEXT)

    if comments.strip():
        pdf.multi_cell(W - 2 * M - 8, 5, comments)
    else:
        pdf.multi_cell(
            W - 2 * M - 8,
            5,
            "No comments provided."
        )
    

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.set_fill_color(*PRIMARY_BLUE)
    pdf.rect(0, H - 14, W, 14, style="F")
    pdf.set_fill_color(*PRIMARY_ORANGE)
    pdf.rect(0, H - 14, W, 2, style="F")
    pdf.set_text_color(*GRAY_MID)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(M, H - 10)
    pdf.cell(0, 5, "Generated by Report Card Generator | Confidential", align="C")

    return bytes(pdf.output())


def _fallback_pdf(row, exercise, course, comments=""):
    lines = [
        "REPORT CARD",
        "",
        f"Exercise : {exercise}",
        f"Course   : {course}",
        "",
        f"Student  : {row['Name']}",
        f"Reg. No. : {row['Registration Number']}",
        f"Email    : {row['Email']}",
        "",
        f"Score    : {row['Marks Obtained']} / {row['Total Marks']}",
        f"Pct      : {row['Percentage']:.2f}%",
        f"Grade    : {row['Grade']}",
        f"Rank     : #{row['Rank']}",
        f"Attempts : {row['Total Attempts']}",
    ]
    buf = io.BytesIO()
    buf.write("\n".join(lines).encode())
    return buf.getvalue()
