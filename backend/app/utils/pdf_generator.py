import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_report_pdf(report_data: Dict[str, Any]) -> io.BytesIO:
    """Generates a professional PDF report from the final analysis and roadmap data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=14,
    )
    heading2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e40af"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=4,
    )
    bold_label_style = ParagraphStyle(
        "BoldLabel",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("Resume Intelligence & Interview Readiness Report", title_style))
    analysis_data = report_data.get("analysis", {})
    target_role = analysis_data.get("target_role", "Candidate Evaluation")
    story.append(Paragraph(f"<b>Target Role:</b> {target_role} | <b>Generated:</b> {report_data.get('generated_at', '')[:10]}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=12))

    # Overall Scores
    scores = analysis_data.get("scores", {})
    overall_score = scores.get("overall_score", 0)
    story.append(Paragraph("Match Assessment Scores", heading2_style))

    score_table_data = [
        [Paragraph("<b>Metric</b>", bold_label_style), Paragraph("<b>Score</b>", bold_label_style), Paragraph("<b>Weight</b>", bold_label_style)]
    ]
    
    metrics = [
        ("Overall Score", f"{overall_score}/100", "100%"),
        ("Skill Match", f"{scores.get('skill_match_score', {}).get('score', 0)}/100", "35%"),
        ("Experience", f"{scores.get('experience_score', {}).get('score', 0)}/100", "20%"),
        ("Project Quality", f"{scores.get('project_score', {}).get('score', 0)}/100", "20%"),
        ("Keyword Coverage", f"{scores.get('keyword_score', {}).get('score', 0)}/100", "15%"),
        ("Seniority Alignment", f"{scores.get('seniority_score', {}).get('score', 0)}/100", "10%"),
    ]
    for metric, sc, wt in metrics:
        score_table_data.append([Paragraph(metric, body_style), Paragraph(sc, body_style), Paragraph(wt, body_style)])

    table = Table(score_table_data, colWidths=[200, 150, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(table)
    # Mock Interview Performance
    interview_perf = report_data.get("interview_performance")
    if interview_perf and interview_perf.get("answered_count", 0) > 0:
        story.append(Paragraph("Mock Interview Performance", heading2_style))
        story.append(Paragraph(f"<b>Overall Interview Score:</b> {interview_perf.get('overall_interview_score', 0)}/100 (Answered {interview_perf.get('answered_count', 0)}/{interview_perf.get('question_count', 0)})", body_style))
        dims = interview_perf.get("dimension_scores", {})
        if dims:
            dim_table_data = [
                [Paragraph("<b>Interview Dimension</b>", bold_label_style), Paragraph("<b>Score</b>", bold_label_style), Paragraph("<b>Weight</b>", bold_label_style)],
                [Paragraph("Technical Accuracy", body_style), Paragraph(f"{dims.get('technical_accuracy', 0)}/100", body_style), Paragraph("35%", body_style)],
                [Paragraph("Relevance", body_style), Paragraph(f"{dims.get('relevance', 0)}/100", body_style), Paragraph("20%", body_style)],
                [Paragraph("Completeness", body_style), Paragraph(f"{dims.get('completeness', 0)}/100", body_style), Paragraph("20%", body_style)],
                [Paragraph("Structure & Clarity", body_style), Paragraph(f"{dims.get('structure_and_clarity', 0)}/100", body_style), Paragraph("15%", body_style)],
                [Paragraph("Communication", body_style), Paragraph(f"{dims.get('communication', 0)}/100", body_style), Paragraph("10%", body_style)],
            ]
            dim_table = Table(dim_table_data, colWidths=[200, 150, 100])
            dim_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(dim_table)
            story.append(Spacer(1, 8))

        k_strengths = interview_perf.get("key_strengths", [])
        if k_strengths:
            story.append(Paragraph("<b>Demonstrated Interview Strengths:</b>", bold_label_style))
            for s in k_strengths:
                story.append(Paragraph(f"• {s}", body_style))
            story.append(Spacer(1, 6))

        k_weaknesses = interview_perf.get("key_weaknesses", [])
        if k_weaknesses:
            story.append(Paragraph("<b>Observed Gaps & Improvement Areas:</b>", bold_label_style))
            for w in k_weaknesses:
                story.append(Paragraph(f"• {w}", body_style))
            story.append(Spacer(1, 6))

        recs = interview_perf.get("recommendations", [])
        if recs:
            story.append(Paragraph("<b>Interview Coaching Recommendations:</b>", bold_label_style))
            for r in recs:
                story.append(Paragraph(f"• {r}", body_style))
            story.append(Spacer(1, 10))

    # Skill Gap Summary
    gap_summary = analysis_data.get("gap_summary", {})
    story.append(Paragraph("Executive Skill Gap Summary", heading2_style))
    readiness = gap_summary.get("overall_readiness", "moderate").capitalize()
    story.append(Paragraph(f"<b>Overall Readiness:</b> {readiness}", body_style))
    
    narrative = gap_summary.get("narrative_summary", "No narrative available.")
    story.append(Paragraph(f"<b>Assessment:</b> {narrative}", body_style))
    story.append(Spacer(1, 10))

    # Critical Missing & Quick Wins
    missing = gap_summary.get("critical_missing_skills", [])
    if missing:
        story.append(Paragraph(f"<b>Critical Missing Skills:</b> {', '.join(missing)}", body_style))
    quick_wins = gap_summary.get("quick_wins", [])
    if quick_wins:
        story.append(Paragraph("<b>Quick Wins:</b>", bold_label_style))
        for win in quick_wins:
            story.append(Paragraph(f"• {win}", body_style))
    story.append(Spacer(1, 12))

    # Career Roadmap
    roadmap = report_data.get("roadmap", {})
    story.append(Paragraph("Personalized Career Roadmap", heading2_style))

    # Personalized Learning Roadmap Priority Skills
    pers_roadmap = report_data.get("learning_roadmap", {})
    if isinstance(pers_roadmap, dict) and "learning_roadmap" in pers_roadmap:
        pers_roadmap = pers_roadmap["learning_roadmap"]
    priority_skills = pers_roadmap.get("priority_skills", []) if isinstance(pers_roadmap, dict) else []
    if priority_skills:
        story.append(Paragraph("<b>Target Priority Skills & Project Tasks:</b>", bold_label_style))
        for p in priority_skills[:4]:
            skill_text = f"• <b>{p.get('skill')}</b> ({p.get('estimated_effort')}): {p.get('why_it_matters')}<br/>&nbsp;&nbsp;<b>Project Task:</b> {p.get('project_task')}"
            story.append(Paragraph(skill_text, body_style))
        story.append(Spacer(1, 6))

    immediate = roadmap.get("immediate_resume_improvements", [])
    if immediate:
        story.append(Paragraph("<b>Immediate Resume Improvements:</b>", bold_label_style))
        for item in immediate:
            story.append(Paragraph(f"• {item}", body_style))
        story.append(Spacer(1, 6))

    learning = roadmap.get("short_term_learning_actions", [])
    if learning:
        story.append(Paragraph("<b>Short-Term Learning Actions:</b>", bold_label_style))
        for act in learning:
            story.append(Paragraph(f"• <b>{act.get('topic')}:</b> {act.get('learning_objective')} ({act.get('timeframe')})", body_style))
        story.append(Spacer(1, 6))

    projects = roadmap.get("project_suggestions", [])
    if projects:
        story.append(Paragraph("<b>Recommended Portfolio Projects:</b>", bold_label_style))
        for proj in projects:
            story.append(Paragraph(f"• <b>{proj.get('project_title')}:</b> {proj.get('problem_statement')}", body_style))
        story.append(Spacer(1, 6))

    interview_focus = roadmap.get("interview_preparation_focus_areas", [])
    if interview_focus:
        story.append(Paragraph("<b>Interview Focus Areas:</b>", bold_label_style))
        for f in interview_focus:
            story.append(Paragraph(f"• {f}", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
