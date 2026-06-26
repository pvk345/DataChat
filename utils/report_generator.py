import hashlib
import sys
if sys.version_info < (3, 9):
    _orig_md5 = hashlib.md5
    hashlib.md5 = lambda *args, **kwargs: _orig_md5(*args)


from dotenv import load_dotenv
load_dotenv()

import os
import io
from datetime import datetime
from typing import Tuple

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from utils.data_loader import describe_dataframe


# ── LLM setup ────────────────────────────────────────────────────────────────
def _get_llm():
    return ChatOpenAI(model="gpt-4o", temperature=0.3)


# ── Step 1: Analyze the dataset ───────────────────────────────────────────────
def _analyze_dataset(df: pd.DataFrame) -> str:
    """
    Compute key statistics from the dataframe and ask the LLM to
    identify trends, top performers, anomalies, and weak spots.
    """
    # Build a rich summary to send to the LLM
    summary_lines = [describe_dataframe(df)]

    # Add numeric column stats
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        summary_lines.append("\nNumeric column statistics:")
        summary_lines.append(df[numeric_cols].describe().to_string())

    # Add value counts for categorical columns (top 5 per column)
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    for col in cat_cols[:4]:
        summary_lines.append(f"\nTop values in '{col}':")
        summary_lines.append(df[col].value_counts().head(5).to_string())

    data_summary = "\n".join(summary_lines)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior data analyst. Given a dataset summary, extract:
1. Top 3 key trends
2. Best performing segments (products, regions, categories, etc.)
3. Worst performing segments
4. Any anomalies or surprising findings
5. Time-based patterns if dates are present

Be specific and use actual numbers from the data. Be concise."""),
        ("human", f"Here is the dataset summary:\n\n{data_summary}"),
    ])

    chain = prompt | _get_llm()
    result = chain.invoke({})
    return result.content


# ── Step 2: Write the narrative report ───────────────────────────────────────
def _write_report(analysis: str, df: pd.DataFrame) -> str:
    """
    Take the raw analysis and write a polished business report narrative.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional business report writer.
Write a clear, professional data analysis report using the analysis provided.

Structure the report with these exact sections:
## Executive Summary
## Key Findings
## Performance Analysis
## Anomalies & Risks
## Recommendations

Rules:
- Use professional but clear language
- Back every claim with specific numbers
- Keep each section focused and concise
- Recommendations should be actionable
- Do not use bullet points — write in full paragraphs"""),
        ("human", f"Write a report based on this analysis:\n\n{analysis}"),
    ])

    chain = prompt | _get_llm()
    result = chain.invoke({})
    return result.content


# ── Step 3: Export to PDF ─────────────────────────────────────────────────────
def _export_to_pdf(report_text: str, df: pd.DataFrame) -> bytes:
    """
    Convert the report markdown text into a clean PDF using reportlab.
    Returns PDF as bytes for Streamlit download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#666666"),
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=18,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a2e"),
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=18,
        spaceAfter=10,
        textColor=colors.HexColor("#333333"),
    )

    story = []

    # Title block
    story.append(Paragraph("DataChat", title_style))
    story.append(Paragraph("Automated Data Analysis Report", subtitle_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} &nbsp;|&nbsp; "
        f"{len(df):,} rows &times; {len(df.columns)} columns",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 16))

    # Parse and render report sections
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("## "):
            heading_text = line.replace("## ", "")
            story.append(Paragraph(heading_text, heading_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
            story.append(Spacer(1, 4))
        elif line.startswith("# "):
            heading_text = line.replace("# ", "")
            story.append(Paragraph(heading_text, heading_style))
        else:
            # Clean up any markdown bold (**text**) for reportlab
            line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ── Main entry point ──────────────────────────────────────────────────────────
def generate_report(df: pd.DataFrame) -> Tuple[str, bytes]:
    """
    Full pipeline: analyze → write → export.
    Returns (report_text, pdf_bytes).
    """
    analysis = _analyze_dataset(df)
    report_text = _write_report(analysis, df)
    pdf_bytes = _export_to_pdf(report_text, df)
    return report_text, pdf_bytes
