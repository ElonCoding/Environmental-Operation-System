import os
import io
import logging
from typing import Optional, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from backend.app.schemas.report import OfficerBriefResponse

logger = logging.getLogger(__name__)

# Register Devanagari / Unicode fonts
FONT_NAME = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

try:
    nirmala_path = r"C:\Windows\Fonts\Nirmala.ttc"
    if os.path.exists(nirmala_path):
        pdfmetrics.registerFont(TTFont("Nirmala", nirmala_path, subfontIndex=0))
        pdfmetrics.registerFont(TTFont("Nirmala-Bold", nirmala_path, subfontIndex=1))
        FONT_NAME = "Nirmala"
        FONT_BOLD = "Nirmala-Bold"
        logger.info("Devanagari font 'Nirmala' registered successfully for PDF generation.")
except Exception as e:
    logger.warning(f"Could not load Nirmala font ({e}), falling back to standard Helvetica.")

class NumberedCanvas:
    """Helper to add page numbers and header/footer on canvas callback."""
    pass

class PDFGenerator:
    def generate_pdf(self, brief: OfficerBriefResponse) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom paragraph styles
        title_style = ParagraphStyle(
            'BriefTitle',
            parent=styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f2942"),
            alignment=0,
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'BriefSubtitle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#0d9488"),
            spaceAfter=6
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f2942"),
            spaceBefore=10,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'BriefBody',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4
        )

        disclaimer_style = ParagraphStyle(
            'BriefDisclaimer',
            parent=styles['Normal'],
            fontName=FONT_BOLD if FONT_BOLD else FONT_NAME,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#b91c1c"),
            backColor=colors.HexColor("#fef2f2"),
            borderPadding=4,
            spaceAfter=6
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=8,
            leading=10,
            textColor=colors.white,
            alignment=1
        )

        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0f172a")
        )

        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0f172a")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph(brief.title_en, title_style))
        if brief.title_hi and brief.language in ["hi", "bilingual"]:
            story.append(Paragraph(brief.title_hi, title_style))
        story.append(Paragraph(
            f"<b>Target Event:</b> {brief.target_event} | <b>Generated:</b> {brief.generated_at}",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d9488"), spaceAfter=6))

        # 2. Prominent Disclaimer
        disclaimer_text = f"<b>IMPORTANT NOTICE:</b> {brief.disclaimer_en}"
        if brief.language in ["hi", "bilingual"]:
            disclaimer_text += f"<br/><b>महत्वपूर्ण सूचना:</b> {brief.disclaimer_hi}"
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        story.append(Spacer(1, 4))

        # 3. Executive Summary
        story.append(Paragraph("1. Executive Summary / कार्यकारी सारांश", section_heading))
        if brief.executive_summary_en:
            story.append(Paragraph(f"<b>[English]</b> {brief.executive_summary_en}", body_style))
        if brief.executive_summary_hi and brief.language in ["hi", "bilingual"]:
            story.append(Paragraph(f"<b>[हिंदी]</b> {brief.executive_summary_hi}", body_style))
        story.append(Spacer(1, 4))

        # 4. Ranked Ghats Priority Table
        story.append(Paragraph("2. Evidence-Based Ghat Risk Prioritisation (CPCB Class B Standard)", section_heading))

        headers = ["Rank", "Ghat Name", "Water Body", "Priority Level", "Score", "Violations", "Anoxia (DO=0)", "Match Conf."]
        col_widths = [32, 120, 80, 80, 42, 60, 56, 52]

        table_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in headers]]

        for g in brief.ranked_ghats:
            prio = g["priority_level"]
            score_str = f"{g['risk_score']}/100" if g['risk_score'] is not None else "N/A"
            viol_str = f"{g['violations_count']}/{g['assessable_count']} ({g['violation_rate_pct']}%)"
            anoxia_str = str(g['anoxia_count']) if g['anoxia_count'] > 0 else "0"

            row = [
                Paragraph(f"<b>#{g.get('rank', '-')}</b>", table_cell_bold),
                Paragraph(g['site_name'], table_cell_bold),
                Paragraph(g['water_body'], table_cell_style),
                Paragraph(f"<b>{prio}</b>", table_cell_style),
                Paragraph(score_str, table_cell_bold),
                Paragraph(viol_str, table_cell_style),
                Paragraph(f"<font color='{'red' if g['anoxia_count'] > 0 else 'black'}'><b>{anoxia_str}</b></font>", table_cell_style),
                Paragraph(g['site_match_confidence'], table_cell_style)
            ]
            table_data.append(row)

        rank_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        rank_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f2942")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(rank_table)
        story.append(Spacer(1, 6))

        # 5. Critical Observations
        story.append(Paragraph("3. Critical Threshold Violations Observed", section_heading))
        crit_headers = ["Ghat Name", "Year / Fest / Phase", "Parameter", "Observed", "CPCB Class B", "Source Report & Page"]
        crit_col_widths = [110, 85, 80, 55, 62, 130]

        crit_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in crit_headers]]
        for cv in brief.critical_violations[:8]:
            crit_data.append([
                Paragraph(cv['site'], table_cell_bold),
                Paragraph(f"{cv['year']} {cv['festival']} ({cv['phase']})", table_cell_style),
                Paragraph(cv['parameter'], table_cell_style),
                Paragraph(f"<font color='red'><b>{cv['observed_value']}</b></font>", table_cell_style),
                Paragraph(cv['cpcb_class_b_limit'], table_cell_style),
                Paragraph(f"{cv['report_filename']}, p.{cv['source_page']}", table_cell_style)
            ])

        crit_table = Table(crit_data, colWidths=crit_col_widths, repeatRows=1)
        crit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(crit_table)
        story.append(Spacer(1, 6))

        # 6. Operational Recommendations
        story.append(Paragraph("4. Tactical Operational Priorities for Municipal Officers", section_heading))
        for idx, p in enumerate(brief.operational_priorities_en, 1):
            story.append(Paragraph(f"• <b>Priority {idx}:</b> {p}", body_style))
        if brief.language in ["hi", "bilingual"] and brief.operational_priorities_hi:
            story.append(Spacer(1, 3))
            story.append(Paragraph("<b>हिंदी परिचालन प्राथमिकताएं:</b>", body_style))
            for idx, p in enumerate(brief.operational_priorities_hi, 1):
                story.append(Paragraph(f"• <b>प्राथमिकता {idx}:</b> {p}", body_style))
        story.append(Spacer(1, 6))

        # 7. Uncertainties & Data Gaps
        story.append(Paragraph("5. Data Quality, Confidence & Limitations Disclosure", section_heading))
        for g in brief.uncertainty_and_data_gaps_en:
            story.append(Paragraph(f"— {g}", body_style))
        story.append(Spacer(1, 6))

        # 8. Source Provenance Table
        story.append(Paragraph("6. Official Source Provenance", section_heading))
        prov_headers = ["Year", "Official MPPCB Document", "Authority / Format", "Cited Pages"]
        prov_col_widths = [45, 230, 110, 137]
        prov_data = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in prov_headers]]
        for sp in brief.source_provenance:
            prov_data.append([
                Paragraph(str(sp['year']), table_cell_bold),
                Paragraph(sp['document'], table_cell_style),
                Paragraph(sp['authority'], table_cell_style),
                Paragraph(sp['pages'], table_cell_style)
            ])
        prov_table = Table(prov_data, colWidths=prov_col_widths)
        prov_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(prov_table)

        # Build PDF document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

pdf_generator = PDFGenerator()
