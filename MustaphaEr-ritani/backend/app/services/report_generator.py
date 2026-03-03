"""
PDF Report Generator Service.
Generates downloadable PDF reports for match results.
"""

import io
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_match_report(match_data: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF report for a candidate-job match.

    Args:
        match_data: Dictionary containing match results

    Returns:
        PDF file as bytes
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Colors
        primary = HexColor("#6366f1")
        success = HexColor("#10b981")
        danger = HexColor("#ef4444")
        light_bg = HexColor("#f8fafc")
        dark_text = HexColor("#1e293b")

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=24,
            textColor=primary,
            spaceAfter=6,
            alignment=TA_CENTER,
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=12,
            textColor=HexColor("#64748b"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=primary,
            spaceBefore=16,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=11,
            textColor=dark_text,
            spaceAfter=4,
        )

        story = []

        # Header
        story.append(Paragraph("AI Resume Screening Report", title_style))
        story.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=2, color=primary))
        story.append(Spacer(1, 0.5 * cm))

        # Candidate & Job Info
        story.append(Paragraph("Match Summary", section_style))
        info_data = [
            ["Candidate", match_data.get("candidate_name", "N/A")],
            ["Position", match_data.get("job_title", "N/A")],
            ["Language", match_data.get("language", "en").upper()],
            ["Match Score", f"{match_data.get('match_score', 0):.1f}%"],
        ]
        info_table = Table(info_data, colWidths=[5 * cm, 12 * cm])
        info_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), light_bg),
                ("TEXTCOLOR", (0, 0), (0, -1), primary),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [white, light_bg]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ])
        )
        story.append(info_table)
        story.append(Spacer(1, 0.5 * cm))

        # Score visualization (text-based bar)
        score = match_data.get("match_score", 0)
        score_color = success if score >= 70 else (HexColor("#f59e0b") if score >= 40 else danger)
        story.append(Paragraph("Match Score", section_style))
        score_style = ParagraphStyle(
            "Score",
            parent=styles["Normal"],
            fontSize=36,
            textColor=score_color,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
        story.append(Paragraph(f"{score:.1f}%", score_style))

        # Matched Skills
        matched = match_data.get("matched_skills", [])
        story.append(Paragraph(f"✅ Matched Skills ({len(matched)})", section_style))
        if matched:
            skills_text = "  •  ".join([s.title() for s in matched])
            story.append(Paragraph(skills_text, body_style))
        else:
            story.append(Paragraph("No matched skills found.", body_style))

        story.append(Spacer(1, 0.3 * cm))

        # Missing Skills
        missing = match_data.get("missing_skills", [])
        story.append(Paragraph(f"❌ Missing Skills ({len(missing)})", section_style))
        if missing:
            skills_text = "  •  ".join([s.title() for s in missing])
            story.append(Paragraph(skills_text, body_style))
        else:
            story.append(Paragraph("All required skills are present!", body_style))

        story.append(Spacer(1, 0.5 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e2e8f0")))
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph(
                "Generated by AI Resume Screening System | Powered by Sentence Transformers",
                ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                               textColor=HexColor("#94a3b8"), alignment=TA_CENTER),
            )
        )

        doc.build(story)
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise RuntimeError(f"Could not generate PDF report: {e}")
