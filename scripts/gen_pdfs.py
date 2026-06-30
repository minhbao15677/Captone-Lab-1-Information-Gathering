#!/usr/bin/env python3
"""
Generate 6 PDF files for the SMB Shared folder.
  - 5 files: appear as locked/corrupted internal docs (unreadable content — garbled or image-only stub)
  - 1 file (credentials.pdf): readable, contains 10 username:password pairs
"""
import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

styles = getSampleStyleSheet()

# ── Credentials list (one of these is andrew / Welc0me@2024!) ────────────────
CREDENTIALS = [
    ("jsmith",   "Tr0ub4dor&3"),
    ("mwilson",  "correct.horse.battery"),
    ("andrew",   "Welc0me@2024!"),
    ("pdavis",   "S3cur3P@ss99"),
    ("lthompson","Hunter2!2024"),
    ("rbrown",   "P@ssw0rd#01"),
    ("agarcia",  "Monke$2023!"),
    ("kjohnson", "Ch@ng3Me!00"),
    ("snguyen",  "W1nt3rIs#Here"),
    ("drogers",  "Fl1pFl0p@321"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Helper: garbled-looking paragraph text (simulate unreadable/corrupted PDF)
# ─────────────────────────────────────────────────────────────────────────────
GARBLED_BLOCKS = [
    "■ ▒▒▒▒▒ ░░░░░░░░░ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    "▓▓▓▓▓▓▓ ░░░░░ ■ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
    "░ ▒▒▒▒▒▒▒▒▒▒▒▒▒ ■■■■■■ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ■ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
    "■■■■■■■■■■■■■■■■■■■■ ▓▓▓▓▓ ░░░░░░░░░░░░░░░░░░",
    "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ■ ▓▓▓▓▓▓▓▓▓▓▓▓",
    "░░░░░░░░░░░░░░░░░░ ▒▒▒▒▒▒▒▒▒ ■■■■■■■■■■■■■■■■",
    "▓▓▓▓ ■■■■ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ░░░░░░░░░░░░░░░░░░░",
]

def garbled_pdf(path, title, doc_id):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    header_style = ParagraphStyle("hdr", fontSize=14, fontName="Helvetica-Bold",
                                   alignment=TA_CENTER, textColor=colors.darkred)
    body_style   = ParagraphStyle("body", fontSize=9, fontName="Courier",
                                   textColor=colors.Color(0.4, 0.4, 0.4),
                                   leading=14)
    warn_style   = ParagraphStyle("warn", fontSize=11, fontName="Helvetica-BoldOblique",
                                   alignment=TA_CENTER, textColor=colors.orange)
    story = []
    story.append(Paragraph(f"INTERNAL DOCUMENT — {title}", header_style))
    story.append(Paragraph(f"Document ID: {doc_id}  |  Classification: CONFIDENTIAL", styles["Normal"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkred))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("⚠  This document could not be rendered correctly.", warn_style))
    story.append(Paragraph("    The file may be password-protected or corrupted.", warn_style))
    story.append(Spacer(1, 0.6*cm))
    for line in GARBLED_BLOCKS * 4:
        story.append(Paragraph(line, body_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Contact IT support to obtain the decryption key for this document.",
        styles["Italic"]
    ))
    doc.build(story)


def credentials_pdf(path):
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    title_style = ParagraphStyle("title", fontSize=16, fontName="Helvetica-Bold",
                                  alignment=TA_CENTER, spaceAfter=6)
    sub_style   = ParagraphStyle("sub",   fontSize=10, fontName="Helvetica",
                                  alignment=TA_CENTER, textColor=colors.grey, spaceAfter=4)
    note_style  = ParagraphStyle("note",  fontSize=9,  fontName="Helvetica-Oblique",
                                  textColor=colors.red)

    story = []
    story.append(Paragraph("IT Department — Temporary System Credentials", title_style))
    story.append(Paragraph("Generated: 2024-03-15  |  INTERNAL USE ONLY", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#c0392b")))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "NOTE: These are temporary default credentials issued for the Q1 2024 "
        "infrastructure migration. All users MUST change their passwords upon first login. "
        "This document is to be shredded after distribution.",
        note_style
    ))
    story.append(Spacer(1, 0.6*cm))

    table_data = [["#", "Username", "Temporary Password", "Service"]]
    services = ["FTP", "Web Portal", "FTP", "VPN", "Web Portal",
                "SSH", "FTP", "VPN", "Web Portal", "SSH"]
    for i, ((user, pwd), svc) in enumerate(zip(CREDENTIALS, services), start=1):
        table_data.append([str(i), user, pwd, svc])

    t = Table(table_data, colWidths=[1*cm, 4*cm, 6*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("FONTNAME",      (0, 1), (-1, -1), "Courier"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "⚠  Reminder: rotate these credentials within 48 hours of receipt. "
        "IT will audit compliance on 2024-03-20.",
        note_style
    ))
    doc.build(story)


# ── Build the 6 files ─────────────────────────────────────────────────────────
locked_docs = [
    ("Q1_Financial_Report_2024.pdf",      "Q1 Financial Report 2024",          "FIN-2024-001"),
    ("HR_Policy_Update_March2024.pdf",    "HR Policy Update March 2024",       "HR-2024-007"),
    ("Network_Infrastructure_Map.pdf",    "Network Infrastructure Map",        "IT-2024-032"),
    ("Board_Meeting_Minutes_Feb2024.pdf", "Board Meeting Minutes Feb 2024",    "EXEC-2024-002"),
    ("Vendor_Contracts_2024.pdf",         "Vendor Contracts 2024",             "LEGAL-2024-015"),
]

for filename, title, doc_id in locked_docs:
    garbled_pdf(os.path.join(OUT_DIR, filename), title, doc_id)
    print(f"[+] Created (garbled):    {filename}")

credentials_pdf(os.path.join(OUT_DIR, "IT_Temp_Credentials_Q1_2024.pdf"))
print(f"[+] Created (readable):   IT_Temp_Credentials_Q1_2024.pdf")
print("[*] PDF generation complete.")
