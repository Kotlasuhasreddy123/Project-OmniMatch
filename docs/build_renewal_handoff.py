"""Build the OmniMatch renewal handoff document."""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

OUT = Path(__file__).with_name("OmniMatch Renewal Handoff and Next Steps.docx")

NAVY = "163A5F"
BLUE = "DCEAF7"
PALE = "F4F7FA"
GRAY = "D9D9D9"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color: str = GRAY) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), color)


def style_run(run, bold: bool = False, size: int | None = None, color: str | None = None) -> None:
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    style_run(r, bold=True, size=16 if level == 1 else 12, color="000000")


def add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.12
    r = p.add_run(text)
    style_run(r, size=10)


def add_bullet(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    style_run(p.add_run(text), size=10)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.width = Inches(widths[i])
        set_cell_shading(cell, NAVY)
        set_cell_border(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        style_run(p.add_run(header), bold=True, size=8, color="FFFFFF")
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].width = Inches(widths[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2 == 1:
                set_cell_shading(cells[i], PALE)
            set_cell_border(cells[i])
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            style_run(p.add_run(value), size=8)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def add_page_number(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("OmniMatch renewal handoff  |  ")
    style_run(run, size=8, color="666666")
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def build() -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    add_page_number(section)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    styles["Normal"].font.size = Pt(10)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(64)
    title.paragraph_format.space_after = Pt(12)
    style_run(title.add_run("OmniMatch Renewal Handoff and Next Steps"), bold=True, size=25, color="000000")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(24)
    style_run(subtitle.add_run("Ambient AI clinical intelligence and trial routing prototype"), size=13, color="3F3F3F")
    for line in [
        "CPSC 69100 Computer Science Masters Project  |  Fall 2026",
        "HealthTech Innovation Labs  |  Prepared for project handoff",
        "Scope: synthetic and mock data only",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(5)
        style_run(p.add_run(line), size=10, color="555555")

    doc.add_page_break()
    add_heading(doc, "Purpose and delivery summary")
    add_body(doc, "This handoff documents the renewed OmniMatch build, the market-informed differentiation, the implemented features, the verification performed, and the steps needed to run the prototype. The original Kiro-built project remains untouched. The renewed implementation is a separate working copy in the Chatgpt folder.")
    add_heading(doc, "What was preserved", 2)
    for item in [
        "Consent-gated microphone workflow and consent audit logging.",
        "RAM-only audio ingestion, Whisper-oriented transcription, negation and family-context handling.",
        "Human-in-the-loop entity approval before trial matching, asynchronous inbox routing, RBAC, and ClinicalTrials.gov v2 synchronization.",
        "Existing per-criterion eligibility display, enrollment readiness scoring, proximity logic, timeline, referral logging, transcript confidence cues, and digest workflow.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "Renewal result", 2)
    add_body(doc, "The renewed build adds two operational safety features to the matching workflow. They do not claim to decide clinical eligibility or enroll a patient. They make evidence provenance and trial-operational uncertainty explicit so a clinical coordinator can review the result safely.")
    add_table(doc, ["Deliverable", "Location", "Purpose"], [
        ["Renewed application", "Chatgpt/omnimatch-renewed", "Separate, non-destructive project copy"],
        ["Evidence Ledger", "backend/app/evidence and frontend evidence utilities", "Hashes approved transcript anchors and links them to met criteria"],
        ["Trial Freshness Gate", "backend/app/trials/freshness_service.py", "Blocks or pauses outreach when registry status, recency, or site data is insufficient"],
        ["Automated tests", "backend/tests/test_renewal_features.py", "Covers approval filtering, evidence links, and four freshness outcomes"],
    ], [1.35, 2.55, 2.9])

    add_heading(doc, "Market comparison and design choices")
    add_body(doc, "The comparison is intentionally capability-focused. Commercial product behavior changes frequently, so it should not be read as a claim that no comparable capability exists anywhere. Instead, it explains the academic prototype choices and how OmniMatch differs in workflow.")
    add_table(doc, ["Reference system", "What it demonstrates", "OmniMatch distinction"], [
        ["AWS trial pre-screening reference", "Agentic matching against patient history and protocol criteria; explanations for selected and rejected trials.", "OmniMatch begins from consent-gated ambient visit signals, requires per-entity clinician approval, and defers results to an asynchronous inbox."],
        ["AWS HealthScribe", "Ambient transcription, word confidence, evidence mapping, and explicit human review of probabilistic outputs.", "OmniMatch applies evidence linkage to trial criteria and stores only a hash plus offsets for the approved transcript anchor, not raw audio or a retained quotation."],
        ["Abridge", "Enterprise ambient documentation with EHR-integrated clinical workflows and evidence-oriented reasoning.", "OmniMatch is a focused simulated research prototype for patient-to-trial routing rather than a documentation or billing product."],
        ["ClinicalTrials.gov API v2", "Standard JSON and ISO 8601 study records exposed through a modern REST API.", "OmniMatch indexes study fields for retrieval, then adds an explicit freshness gate before coordinator routing."],
    ], [1.45, 2.55, 2.8])

    add_heading(doc, "Implemented feature 8 Evidence Ledger")
    add_body(doc, "The Evidence Ledger is inspired by evidence mapping in ambient clinical tools, but it is designed for the project constraint that raw audio must stay in RAM and synthetic data only is used. On the verification page, the browser finds each approved entity in the current transcript. It calculates SHA-256 over that exact span and sends the entity name, offsets, confidence, approval state, and digest to the API. The backend records a tamper-evident event hash over the minimized event. It does not record the source audio, the full transcript, or the textual excerpt.")
    add_table(doc, ["Control", "Implementation behavior", "Why it matters"], [
        ["Human gate", "Only approved, patient-context, non-negated entities are accepted.", "Preserves REQ 04 and avoids turning AI extraction into an automatic claim."],
        ["Privacy minimization", "Ledger keeps digest and character offsets rather than raw transcript text or audio.", "Supports traceability without expanding sensitive retention."],
        ["Criterion linkage", "Only MET criteria receive an evidence link; missing or unknown requirements remain visible as uncertainty.", "Avoids fabricated citations and distinguishes evidence from absence of evidence."],
        ["UI review", "Inbox card shows verified entity-to-criterion links.", "Lets a coordinator see why a criterion was treated as met."],
    ], [1.45, 3.2, 2.15])

    add_heading(doc, "Implemented feature 9 Trial Freshness Gate")
    add_body(doc, "A high similarity score is not proof that a site is open or able to enroll. The Trial Freshness Gate uses the registry status, the last update date, and the presence of site information to return READY, REVIEW, or BLOCKED. It is deliberately conservative: non-active registry states block routing; an undated or older-than-90-day record requires verification; missing site data requires verification; and only an active, recent record with site data is labeled ready for coordinator review.")
    add_table(doc, ["Gate level", "Condition", "Recommended action"], [
        ["READY", "Active registry state, update within 30 days, and site data available", "Route to coordinator for review"],
        ["REVIEW", "No site data, missing update date, or update older than 30 days", "Verify before outreach"],
        ["BLOCKED", "Registry status not in an active enrollment state", "Do not route"],
    ], [1.15, 3.9, 1.75])

    add_heading(doc, "Architecture and API changes")
    add_body(doc, "The two features are additive. Existing consent, verification, matching, and inbox controls remain in place. The direct match API and asynchronous inbox pipeline now both build the per-criterion evidence links and the freshness decision. This keeps a direct API search and a completed visit consistent.")
    add_table(doc, ["Area", "Change"], [
        ["Data model", "EvidenceSpan, CriterionEvidence, EvidenceLedger request and response, freshness payload, and evidence spans on match and session-complete requests."],
        ["Backend", "New /api/v1/evidence/ledger endpoint, SQLite evidence_ledger table, deterministic event hash, freshness service, enriched async inbox construction."],
        ["Frontend", "Browser-only SHA-256 span utility, evidence submission before session completion, and an accessible trust panel on each expanded inbox match."],
        ["Resilience", "Configuration ignores unrelated environment variables; embedding dependencies are loaded only when embedding work actually runs."],
    ], [1.4, 5.4])

    doc.add_page_break()
    add_heading(doc, "Verification performed")
    add_body(doc, "The renewal implementation received two focused automated verification passes in the renewed backend environment.")
    add_table(doc, ["Verification run", "Result", "Coverage"], [
        ["Renewal feature suite", "6 passed", "Approval filtering; MET-only evidence linking; READY, REVIEW, and BLOCKED freshness outcomes."],
        ["Renewal plus selected existing-feature suite", "21 passed, 2 intentionally deselected", "Renewal features, eligibility breakdown, readiness scoring, proximity ranking, transcription confidence schema, and referral schema."],
        ["Regression corrections", "Validated by passing selected suite", "Short lab criteria now reach UNKNOWN classification; great-circle distance assertion uses the correct air-distance range."],
    ], [1.75, 1.45, 3.6])
    add_heading(doc, "Runbook")
    add_body(doc, "Use the renewed project folder as the working copy. Keep the original folders as the reference baseline.")
    for item in [
        "Open Chatgpt/omnimatch-renewed. Copy backend/.env.example to backend/.env and set unique development secrets. Do not use demonstration secrets outside a local synthetic-data environment.",
        "Start the stack with Docker Compose from the renewed project root. Seed a small ClinicalTrials.gov data set before exercising matching.",
        "Open the frontend, log in with local demo credentials, grant consent, complete a synthetic session, approve entities, and submit the visit. Review the Async Inbox after the background task runs.",
        "Expand a trial card. Confirm that the criterion evidence list shows only approved terms, then inspect the Outreach Gate. READY means coordinator review is reasonable; REVIEW means verify registry or site availability; BLOCKED means do not route.",
        "Run the backend test command from backend and the frontend test and type-check commands from frontend before every demonstration or submission.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "Next implementation steps")
    add_table(doc, ["Priority", "Action", "Acceptance signal"], [
        ["1", "Add authenticated ClinicalTrials.gov snapshot timestamps and location status during sync.", "Freshness Gate uses current registry metadata for every indexed trial."],
        ["2", "Add an append-only audit viewer restricted to ADMIN and test retention behavior.", "Admin can validate consent, evidence, referral, and gate events without exposing raw audio."],
        ["3", "Replace inline ZIP centroids with a maintained geographic data source and add site recruitment-status checks.", "Distance and site availability are validated against a documented source."],
        ["4", "Create a synthetic evaluation set for transcript anchoring and fairness slices, then report uncertainty by acoustic and language conditions.", "Documented error analysis informs the next sprint."],
        ["5", "Complete production security review before any non-synthetic use: BAA, threat model, encryption key management, retention, access monitoring, and clinical governance.", "Written approval from the appropriate security and clinical authority."],
    ], [0.7, 3.75, 2.35])

    add_heading(doc, "Safety boundary")
    add_body(doc, "OmniMatch is a simulated academic prototype that uses synthetic and mock data. It supports workflow review and does not diagnose, determine eligibility, contact a patient, enroll a patient, replace a clinician, or establish production HIPAA compliance. Any real deployment requires clinical validation, governance, security review, legal review, an AWS Business Associate Agreement when applicable, and a full privacy and retention design.")

    add_heading(doc, "Research sources")
    for source in [
        "AWS. Improving patient pre screening for clinical trials with generative AI on AWS. 2024. https://aws.amazon.com/blogs/industries/improving-patient-pre-screening-for-clinical-trials-with-generative-ai-on-aws/",
        "AWS. AWS HealthScribe AI Service Card. Evidence mapping, word confidence, limitations, and human oversight guidance. https://docs.aws.amazon.com/pdfs/ai/responsible-ai/aws-healthscribe/aws-healthscribe.pdf",
        "National Library of Medicine. ClinicalTrials.gov API Version 2.0 Now Available. 2024. https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html",
        "AWS. AI powered clinical trial eligibility and safety using Amazon Bedrock AgentCore. 2026. https://aws.amazon.com/blogs/architecture/ai-agents-for-clinical-trial-screening/",
        "Abridge. Generative AI for Clinical Conversations. https://www.abridge.com/product",
    ]:
        add_bullet(doc, source)

    doc.core_properties.title = "OmniMatch Renewal Handoff and Next Steps"
    doc.core_properties.subject = "Renewed implementation, differentiation, verification, and operating procedures"
    doc.core_properties.author = "HealthTech Innovation Labs"
    doc.save(OUT)


if __name__ == "__main__":
    build()
