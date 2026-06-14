---
name: resume-optimizer
version: 1.0.0
description: Build and optimize CVs/resumes with ATS scoring, keyword analysis, PDF/DOCX export, and multiple templates. Tailor resumes for specific job descriptions automatically.
tags: [resume, cv, ats, job-search, pdf, docx, career, optimization, latex]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Resume Optimizer Skill

## Setup

```bash
pip install python-docx reportlab spacy scikit-learn python-dotenv
python -m spacy download en_core_web_sm
```

## Resume Data Structure

```python
from dataclasses import dataclass, field

@dataclass
class ResumeContact:
    name: str
    email: str
    phone: str
    location: str
    linkedin: str = ""
    github: str = ""
    website: str = ""

@dataclass
class ResumeExperience:
    company: str
    role: str
    start: str        # "Jan 2022"
    end: str          # "Present"
    location: str
    bullets: list[str] = field(default_factory=list)

@dataclass
class ResumeEducation:
    institution: str
    degree: str
    field: str
    start: str
    end: str
    gpa: str = ""
    achievements: list[str] = field(default_factory=list)

@dataclass
class ResumeSkills:
    technical: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)

@dataclass
class Resume:
    contact: ResumeContact
    summary: str
    experience: list[ResumeExperience] = field(default_factory=list)
    education: list[ResumeEducation] = field(default_factory=list)
    skills: ResumeSkills = field(default_factory=ResumeSkills)
    certifications: list[str] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    languages_spoken: list[dict] = field(default_factory=list)  # [{"language": "Spanish", "level": "Native"}]
```

## ATS Keyword Analysis

```python
import re
from collections import Counter
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, top_n: int = 30) -> list[str]:
    """Extract important keywords from a job description."""
    doc = nlp(text.lower())
    
    # Filter to nouns, proper nouns, adjectives — skip stopwords
    keywords = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in {"NOUN", "PROPN", "ADJ"}
        and len(token.text) > 2
    ]
    
    counter = Counter(keywords)
    return [word for word, _ in counter.most_common(top_n)]

def ats_score(resume: Resume, job_description: str) -> dict:
    """Calculate ATS compatibility score against a job description."""
    jd_keywords = set(extract_keywords(job_description, top_n=50))
    
    # Build resume text blob
    resume_text = " ".join([
        resume.summary,
        " ".join(resume.skills.technical),
        " ".join(resume.skills.tools),
        " ".join([b for exp in resume.experience for b in exp.bullets]),
    ]).lower()
    
    resume_doc = nlp(resume_text)
    resume_words = {token.lemma_ for token in resume_doc if not token.is_stop}
    
    matched = jd_keywords & resume_words
    missing = jd_keywords - resume_words
    
    score = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0
    
    return {
        "score": round(score, 1),
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "recommendation": "Good ATS match" if score >= 70 else "Add missing keywords to improve ATS score"
    }

def optimize_for_job(resume: Resume, job_description: str) -> dict:
    """Suggest bullet improvements to target a specific JD."""
    score = ats_score(resume, job_description)
    recommendations = []
    
    if score["score"] < 60:
        recommendations.append("⚠️  ATS score < 60%. You may be filtered automatically.")
    
    missing = score["missing_keywords"][:10]
    if missing:
        recommendations.append(f"Add these keywords to bullets/skills: {', '.join(missing)}")
    
    # Check quantification
    all_bullets = [b for exp in resume.experience for b in exp.bullets]
    quantified = sum(1 for b in all_bullets if any(c.isdigit() for c in b))
    pct = (quantified / len(all_bullets) * 100) if all_bullets else 0
    if pct < 50:
        recommendations.append(f"Only {pct:.0f}% of bullets have numbers. Add metrics (%, $, #users, time saved).")
    
    return {"ats_score": score, "recommendations": recommendations}
```

## Bullet Point Improver

```python
STRONG_VERBS = [
    "Architected", "Automated", "Built", "Delivered", "Designed",
    "Drove", "Engineered", "Increased", "Launched", "Led",
    "Optimized", "Reduced", "Scaled", "Shipped", "Streamlined"
]

def improve_bullet(bullet: str) -> str:
    """
    Template for improving a resume bullet.
    Format: [Strong Verb] + [Task] + [Tool/Method] + [Quantified Result]
    
    Before: "Helped with the development of new features"
    After:  "Engineered 12 new API endpoints using FastAPI, reducing response time by 40%"
    """
    # Check if bullet starts with strong verb
    first_word = bullet.split()[0].rstrip(",.")
    if first_word not in STRONG_VERBS:
        suggestion = f"Start with a stronger verb. Instead of '{first_word}', try one of: {', '.join(STRONG_VERBS[:5])}"
    else:
        suggestion = None
    
    has_number = any(c.isdigit() for c in bullet)
    has_percentage = "%" in bullet
    
    feedback = {
        "original": bullet,
        "has_metric": has_number or has_percentage,
        "strong_verb": first_word in STRONG_VERBS,
        "suggestion": suggestion,
        "template": "[Strong Verb] + [What you did] + [How/Tool] + [Result: X% / $X / X users]"
    }
    return feedback

def review_all_bullets(resume: Resume) -> list[dict]:
    """Review all bullets across all experiences."""
    issues = []
    for exp in resume.experience:
        for bullet in exp.bullets:
            feedback = improve_bullet(bullet)
            if not feedback["has_metric"] or not feedback["strong_verb"]:
                issues.append({
                    "company": exp.company,
                    "role": exp.role,
                    "bullet": bullet,
                    "has_metric": feedback["has_metric"],
                    "strong_verb": feedback["strong_verb"],
                    "suggestion": feedback["suggestion"],
                })
    return issues
```

## Export to DOCX

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def export_to_docx(resume: Resume, output_path: str = "resume.docx"):
    """Generate a clean ATS-friendly DOCX resume."""
    doc = Document()

    # Margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    def add_heading(text, level=1, color=(0, 0, 0)):
        para = doc.add_paragraph()
        run = para.add_run(text)
        run.bold = True
        run.font.size = Pt(14 if level == 1 else 12)
        run.font.color.rgb = RGBColor(*color)
        return para

    def add_divider():
        para = doc.add_paragraph()
        para.add_run("─" * 70).font.size = Pt(8)

    # Contact
    contact_para = doc.add_paragraph()
    contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = contact_para.add_run(resume.contact.name)
    run.bold = True
    run.font.size = Pt(18)

    doc.add_paragraph(
        f"{resume.contact.email} | {resume.contact.phone} | {resume.contact.location}"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER

    if resume.contact.linkedin or resume.contact.github:
        links = " | ".join(filter(None, [resume.contact.linkedin, resume.contact.github]))
        doc.add_paragraph(links).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Summary
    add_divider()
    add_heading("PROFESSIONAL SUMMARY", color=(31, 73, 125))
    doc.add_paragraph(resume.summary)

    # Experience
    add_divider()
    add_heading("EXPERIENCE", color=(31, 73, 125))
    for exp in resume.experience:
        p = doc.add_paragraph()
        p.add_run(exp.role).bold = True
        p.add_run(f" — {exp.company}")
        p2 = doc.add_paragraph()
        p2.add_run(f"{exp.start} – {exp.end} | {exp.location}").italic = True
        for bullet in exp.bullets:
            doc.add_paragraph(bullet, style="List Bullet")

    # Education
    add_divider()
    add_heading("EDUCATION", color=(31, 73, 125))
    for edu in resume.education:
        p = doc.add_paragraph()
        p.add_run(f"{edu.degree} in {edu.field}").bold = True
        p.add_run(f" — {edu.institution}")
        doc.add_paragraph(f"{edu.start} – {edu.end}").italic = True

    # Skills
    add_divider()
    add_heading("SKILLS", color=(31, 73, 125))
    if resume.skills.technical:
        doc.add_paragraph(f"Technical: {', '.join(resume.skills.technical)}")
    if resume.skills.tools:
        doc.add_paragraph(f"Tools: {', '.join(resume.skills.tools)}")

    doc.save(output_path)
    return output_path
```

## Export to PDF (via reportlab)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib import colors

def export_to_pdf(resume: Resume, output_path: str = "resume.pdf"):
    """Generate a clean PDF resume."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Name
    name_style = ParagraphStyle("name", fontSize=20, fontName="Helvetica-Bold", alignment=1)
    story.append(Paragraph(resume.contact.name, name_style))
    story.append(Spacer(1, 0.3*cm))

    # Contact line
    contact_line = f"{resume.contact.email} | {resume.contact.phone} | {resume.contact.location}"
    story.append(Paragraph(contact_line, ParagraphStyle("contact", alignment=1, fontSize=10)))
    story.append(Spacer(1, 0.5*cm))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles["Heading2"]))
    story.append(Paragraph(resume.summary, styles["Normal"]))
    story.append(Spacer(1, 0.4*cm))

    # Experience
    story.append(Paragraph("EXPERIENCE", styles["Heading2"]))
    for exp in resume.experience:
        story.append(Paragraph(f"<b>{exp.role}</b> — {exp.company} ({exp.start}–{exp.end})", styles["Normal"]))
        for b in exp.bullets:
            story.append(Paragraph(f"• {b}", styles["Normal"]))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    return output_path
```

## Full Workflow Example

```python
resume = Resume(
    contact=ResumeContact(
        name="Maria García",
        email="maria@example.com",
        phone="+34 600 000 000",
        location="Madrid, Spain",
        linkedin="linkedin.com/in/mariagarcia",
        github="github.com/mariagarcia"
    ),
    summary="Senior Backend Engineer with 5+ years building scalable APIs. Led teams of 4-8 engineers. Specialized in Python, FastAPI, and cloud-native architectures.",
    experience=[
        ResumeExperience(
            company="TechCorp",
            role="Senior Backend Engineer",
            start="Jan 2022",
            end="Present",
            location="Madrid, Spain",
            bullets=[
                "Architected microservices platform handling 10M requests/day, reducing latency by 45%",
                "Led migration from monolith to Kubernetes, saving €80K/year in infrastructure",
                "Mentored 3 junior engineers, 2 of whom were promoted within 12 months"
            ]
        )
    ],
    education=[
        ResumeEducation(
            institution="Universidad Politécnica de Madrid",
            degree="M.Sc.",
            field="Computer Science",
            start="2016",
            end="2018"
        )
    ],
    skills=ResumeSkills(
        technical=["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka"],
        tools=["Docker", "Kubernetes", "AWS", "Terraform", "GitHub Actions"]
    )
)

jd = """
We are looking for a Senior Engineer with experience in Python, microservices,
Kubernetes, CI/CD pipelines, and cloud infrastructure. Experience with Terraform
and AWS required. Strong communication skills needed.
"""

# ATS Analysis
result = optimize_for_job(resume, jd)
print(f"ATS Score: {result['ats_score']['score']}%")
for rec in result["recommendations"]:
    print(f"  → {rec}")

# Bullet Review
issues = review_all_bullets(resume)
for issue in issues:
    print(f"  [{issue['company']}] {issue['bullet'][:60]}…")
    if issue["suggestion"]:
        print(f"     → {issue['suggestion']}")

# Export
export_to_docx(resume, "maria_garcia_resume.docx")
export_to_pdf(resume, "maria_garcia_resume.pdf")
```

## References
- [python-docx](https://python-docx.readthedocs.io/) — Word document generation
- [reportlab](https://www.reportlab.com/) — PDF generation
- [spaCy](https://spacy.io/) — NLP for keyword extraction
- [Jobscan](https://www.jobscan.co/) — Online ATS checker (for validation)
