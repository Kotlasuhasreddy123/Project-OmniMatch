"""
convert_report.py
Converts OmniMatch_Complete_Progress_Report.md into:
  1. OmniMatch_Complete_Progress_Report.docx  (Word document)
  2. OmniMatch_Complete_Progress_Report.pdf   (PDF via ReportLab)

Run from the docs/ folder:
    python convert_report.py
"""

import re
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
DOCS_DIR  = Path(__file__).parent
MD_FILE   = DOCS_DIR / "OmniMatch_Complete_Progress_Report.md"
DOCX_FILE = DOCS_DIR / "OmniMatch_Complete_Progress_Report.docx"
PDF_FILE  = DOCS_DIR / "OmniMatch_Complete_Progress_Report.pdf"

md_text = MD_FILE.read_text(encoding="utf-8")
lines   = md_text.splitlines()

print(f"Source: {MD_FILE.name}  ({len(lines)} lines)")

# ══════════════════════════════════════════════════════════════════════════════
#  PART 1 — DOCX via python-docx
# ══════════════════════════════════════════════════════════════════════════════
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_bg(cell, hex_color: str):
    """Set table cell background colour."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)

def add_horizontal_rule(doc):
    """Insert a thin grey horizontal rule paragraph."""
    p   = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pb  = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "AAAAAA")
    pb.append(bot)
    pPr.append(pb)
    p.paragraph_format.space_after = Pt(4)

def apply_inline_styles(para, text: str):
    """Parse **bold**, `code`, and plain text segments into runs."""
    # Split on **bold** and `code` markers
    parts = re.split(r"(\*\*.*?\*\*|`[^`]+`)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = para.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = para.add_run(part[1:-1])
            run.font.name = "Courier New"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
        else:
            para.add_run(part)

def build_docx():
    doc = Document()

    # ── Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # ── Default paragraph style
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    # ── Heading colours
    HEADING_COLORS = {
        "Heading 1": RGBColor(0x1E, 0x3A, 0x8A),   # dark blue
        "Heading 2": RGBColor(0x1D, 0x4E, 0xD8),   # blue
        "Heading 3": RGBColor(0x25, 0x63, 0xEB),   # medium blue
        "Heading 4": RGBColor(0x37, 0x74, 0xCA),   # lighter blue
    }
    for hname, color in HEADING_COLORS.items():
        hstyle = doc.styles[hname]
        hstyle.font.color.rgb = color
        hstyle.font.name = "Calibri"

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Skip blank lines (add spacing)
        if not stripped:
            i += 1
            continue

        # ── Horizontal rule
        if stripped == "---":
            add_horizontal_rule(doc)
            i += 1
            continue

        # ── Headings
        if stripped.startswith("#"):
            level = len(re.match(r"^#+", stripped).group())
            text  = stripped.lstrip("#").strip()
            # Strip anchor tags like <a name="..."></a>
            text  = re.sub(r"<a[^>]*>.*?</a>", "", text).strip()
            hname = f"Heading {min(level, 4)}"
            doc.add_heading(text, level=min(level, 4))
            i += 1
            continue

        # ── Fenced code block
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = "\n".join(code_lines)
            p = doc.add_paragraph(style="No Spacing")
            run = p.add_run(code_text)
            run.font.name = "Courier New"
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(0x1F, 0x2D, 0x3D)
            p.paragraph_format.left_indent  = Cm(1.0)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after  = Pt(4)
            continue

        # ── Table (detect by leading |)
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) < 2:
                continue

            # Parse header
            header_cells = [c.strip() for c in table_lines[0].split("|") if c.strip()]
            col_count    = len(header_cells)
            # Find data rows (skip separator line with ---)
            data_rows = []
            for tl in table_lines[2:]:
                cells = [c.strip() for c in tl.split("|")]
                cells = [c for j, c in enumerate(cells) if j > 0 and j <= col_count]
                while len(cells) < col_count:
                    cells.append("")
                data_rows.append(cells)

            tbl = doc.add_table(rows=1 + len(data_rows), cols=col_count)
            tbl.style = "Table Grid"

            # Header row
            hrow = tbl.rows[0]
            for j, cell_text in enumerate(header_cells):
                cell = hrow.cells[j]
                cell.text = ""
                run = cell.paragraphs[0].add_run(re.sub(r"\*\*|`", "", cell_text))
                run.bold      = True
                run.font.size = Pt(9)
                run.font.name = "Calibri"
                set_cell_bg(cell, "D1E4F6")

            # Data rows
            for ri, row_cells in enumerate(data_rows):
                row = tbl.rows[ri + 1]
                bg  = "FFFFFF" if ri % 2 == 0 else "F0F7FF"
                for j, cell_text in enumerate(row_cells):
                    cell = row.cells[j]
                    cell.text = ""
                    p    = cell.paragraphs[0]
                    clean = re.sub(r"<[^>]+>", "", cell_text)
                    apply_inline_styles(p, clean)
                    for run in p.runs:
                        run.font.size = Pt(9)
                        run.font.name = "Calibri"
                    set_cell_bg(cell, bg)

            doc.add_paragraph()
            continue

        # ── Bullet list
        if stripped.startswith(("- ", "* ", "• ")):
            text = stripped[2:]
            p    = doc.add_paragraph(style="List Bullet")
            apply_inline_styles(p, text)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue

        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s", "", stripped)
            p    = doc.add_paragraph(style="List Number")
            apply_inline_styles(p, text)
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue

        # ── Checkbox items (- [ ] or - [x])
        if re.match(r"^-\s+\[[ x]\]", stripped):
            checked = "[x]" in stripped[:6].lower()
            text    = re.sub(r"^-\s+\[[ xX]\]\s*", "", stripped)
            marker  = "☑" if checked else "☐"
            p       = doc.add_paragraph(style="List Bullet")
            apply_inline_styles(p, f"{marker}  {text}")
            p.paragraph_format.space_after = Pt(2)
            i += 1
            continue

        # ── Blockquote (> lines)
        if stripped.startswith(">"):
            text = stripped.lstrip("> ").strip()
            p    = doc.add_paragraph(style="No Spacing")
            apply_inline_styles(p, text)
            p.paragraph_format.left_indent  = Cm(1.5)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after  = Pt(2)
            fmt  = p.paragraph_format
            from docx.oxml import OxmlElement as OXE
            pPr  = p._p.get_or_add_pPr()
            pb   = OXE("w:pBdr")
            lft  = OXE("w:left")
            lft.set(qn("w:val"),   "single")
            lft.set(qn("w:sz"),    "12")
            lft.set(qn("w:color"), "2563EB")
            pb.append(lft)
            pPr.append(pb)
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        # ── Normal paragraph
        # Strip HTML anchor tags
        text = re.sub(r"<a[^>]*>.*?</a>", "", stripped).strip()
        if text:
            p = doc.add_paragraph(style="Normal")
            apply_inline_styles(p, text)
            p.paragraph_format.space_after = Pt(4)
        i += 1

    doc.save(DOCX_FILE)
    print(f"✅ DOCX saved: {DOCX_FILE.name}")

# ══════════════════════════════════════════════════════════════════════════════
#  PART 2 — PDF via ReportLab
# ══════════════════════════════════════════════════════════════════════════════
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles   import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units     import cm
from reportlab.lib           import colors
from reportlab.platypus      import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Preformatted, HRFlowable,
)
from reportlab.lib.enums    import TA_LEFT, TA_CENTER

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

def sanitize(text: str) -> str:
    """Escape XML special chars for ReportLab Paragraph."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Restore markdown bold/code as RL tags
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>",   text)
    text = re.sub(r"`([^`]+)`",      r"<font name='Courier' color='#C00000'>\1</font>", text)
    # Remove leftover HTML-looking anchor tags
    text = re.sub(r"&lt;a[^&]*&gt;.*?&lt;/a&gt;", "", text)
    return text

def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_FILE),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
        title="OmniMatch Complete Progress Report",
        author="HealthTech Innovation Labs",
    )

    base  = getSampleStyleSheet()
    NAVY  = colors.HexColor("#1E3A8A")
    BLUE  = colors.HexColor("#2563EB")
    LBLUE = colors.HexColor("#3B82F6")
    GREY  = colors.HexColor("#6B7280")
    WHITE = colors.white
    LBKG  = colors.HexColor("#EFF6FF")

    styles = {
        "h1":   ParagraphStyle("h1",   fontSize=18, textColor=NAVY,  leading=24, spaceAfter=8,  spaceBefore=14, fontName="Helvetica-Bold"),
        "h2":   ParagraphStyle("h2",   fontSize=14, textColor=NAVY,  leading=19, spaceAfter=6,  spaceBefore=12, fontName="Helvetica-Bold"),
        "h3":   ParagraphStyle("h3",   fontSize=12, textColor=BLUE,  leading=16, spaceAfter=5,  spaceBefore=10, fontName="Helvetica-Bold"),
        "h4":   ParagraphStyle("h4",   fontSize=11, textColor=BLUE,  leading=15, spaceAfter=4,  spaceBefore=8,  fontName="Helvetica-Bold"),
        "body": ParagraphStyle("body", fontSize=9.5, textColor=colors.HexColor("#111827"), leading=14, spaceAfter=5, fontName="Helvetica"),
        "code": ParagraphStyle("code", fontSize=8,   fontName="Courier", backColor=colors.HexColor("#F3F4F6"),
                               leftIndent=12, spaceAfter=6, spaceBefore=4, leading=11,
                               borderColor=colors.HexColor("#D1D5DB"), borderWidth=0.5, borderPadding=5),
        "bull": ParagraphStyle("bull", fontSize=9.5, leading=14, leftIndent=18, spaceAfter=2,
                               bulletIndent=6, fontName="Helvetica"),
        "quote":ParagraphStyle("quote",fontSize=9, leading=13, leftIndent=16, spaceAfter=4,
                               textColor=GREY, fontName="Helvetica-Oblique",
                               borderLeftWidth=3, borderLeftColor=BLUE, borderLeftPadding=6),
        "thhd": ParagraphStyle("thhd", fontSize=8.5, textColor=WHITE, fontName="Helvetica-Bold", leading=11),
        "tdcl": ParagraphStyle("tdcl", fontSize=8.5, textColor=colors.HexColor("#111827"), fontName="Helvetica", leading=11),
    }

    story  = []
    in_code = False
    code_buf = []

    def flush_code():
        nonlocal in_code, code_buf
        if code_buf:
            story.append(Preformatted("\n".join(code_buf), styles["code"]))
            story.append(Spacer(1, 4))
        code_buf = []
        in_code  = False

    i = 0
    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        # ── Code block
        if stripped.startswith("```"):
            if in_code:
                flush_code()
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not stripped:
            story.append(Spacer(1, 3))
            i += 1
            continue

        if stripped == "---":
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=4))
            i += 1
            continue

        # ── Headings
        if stripped.startswith("#"):
            level = len(re.match(r"^#+", stripped).group())
            text  = stripped.lstrip("#").strip()
            text  = re.sub(r"<a[^>]*>.*?</a>", "", text).strip()
            key   = f"h{min(level, 4)}"
            story.append(Paragraph(sanitize(text), styles[key]))
            i += 1
            continue

        # ── Table
        if stripped.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1

            if len(tbl_lines) < 2:
                continue

            headers = [c.strip() for c in tbl_lines[0].split("|") if c.strip()]
            ncols   = len(headers)
            data    = [[Paragraph(sanitize(re.sub(r"\*\*|`","",h)), styles["thhd"]) for h in headers]]

            for tl in tbl_lines[2:]:
                cells = [c.strip() for c in tl.split("|")]
                cells = [c for j, c in enumerate(cells) if j > 0 and j <= ncols]
                while len(cells) < ncols:
                    cells.append("")
                data.append([Paragraph(sanitize(c), styles["tdcl"]) for c in cells])

            col_w = (PAGE_W - 2 * MARGIN) / ncols
            tbl   = Table(data, colWidths=[col_w] * ncols, repeatRows=1)
            ts    = TableStyle([
                ("BACKGROUND",  (0, 0), (-1,  0), NAVY),
                ("TEXTCOLOR",   (0, 0), (-1,  0), WHITE),
                ("FONTNAME",    (0, 0), (-1,  0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 8.5),
                ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LBKG]),
                ("TOPPADDING",  (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ])
            tbl.setStyle(ts)
            story.append(tbl)
            story.append(Spacer(1, 8))
            continue

        # ── Checkbox items
        if re.match(r"^-\s+\[[ xX]\]", stripped):
            checked = "x" in stripped[3:5].lower()
            text    = re.sub(r"^-\s+\[[ xX]\]\s*", "", stripped)
            marker  = "☑" if checked else "☐"
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{marker}&nbsp; {sanitize(text)}", styles["bull"]))
            i += 1
            continue

        # ── Bullet
        if stripped.startswith(("- ", "* ")):
            text = stripped[2:]
            story.append(Paragraph(f"• &nbsp;{sanitize(text)}", styles["bull"]))
            i += 1
            continue

        # ── Numbered list
        if re.match(r"^\d+\.\s", stripped):
            m    = re.match(r"^(\d+)\.\s+(.*)", stripped)
            num  = m.group(1)
            text = m.group(2)
            story.append(Paragraph(f"<b>{num}.</b>&nbsp; {sanitize(text)}", styles["bull"]))
            i += 1
            continue

        # ── Blockquote
        if stripped.startswith(">"):
            text = stripped.lstrip("> ").strip()
            story.append(Paragraph(sanitize(text), styles["quote"]))
            i += 1
            continue

        # ── Normal paragraph
        text = re.sub(r"<a[^>]*>.*?</a>", "", stripped).strip()
        if text:
            story.append(Paragraph(sanitize(text), styles["body"]))
        i += 1

    flush_code()

    # ── Page header/footer
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN, PAGE_H - 1.4 * cm,
                          "OmniMatch — CPSC-69100 Master's Project | HealthTech Innovation Labs")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.4 * cm,
                               f"Page {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, PAGE_H - 1.6 * cm, PAGE_W - MARGIN, PAGE_H - 1.6 * cm)
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"✅ PDF  saved: {PDF_FILE.name}")

# ── Run both conversions ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("Converting OmniMatch_Complete_Progress_Report.md …\n")
    build_docx()
    build_pdf()
    print("\nDone! Files saved in docs/")
