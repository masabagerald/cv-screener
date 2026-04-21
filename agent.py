import asyncio
from pypdf import PdfReader
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

load_dotenv()

# ── Output schemas ─────────────────────────────────────────────

class CriterionScore(BaseModel):
    criterion: str
    score: int = Field(ge=1, le=10)
    justification: str

class CandidateReview(BaseModel):
    candidate_name: str
    overall_score: int = Field(ge=1, le=10)
    recommendation: str  # "Shortlist" | "Consider" | "Reject"
    scores: list[CriterionScore]
    strengths: list[str]
    concerns: list[str]
    jd_match_summary: str  # one paragraph on fit vs JD
    has_cover_letter: bool

# ── Tools ──────────────────────────────────────────────────────

@function_tool
def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF (CV or cover letter)."""
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text[:8000]

@function_tool
def score_candidate(
    candidate_name: str,
    skills_match: int,
    experience_relevance: int,
    education_fit: int,
    cover_letter_quality: int,
    communication_clarity: int,
) -> dict:
    """
    Score a candidate across five dimensions (1-10 each).
    cover_letter_quality should be 0 if no cover letter was provided.
    Returns a dict the agent uses to build the final structured review.
    """
    scores = [skills_match, experience_relevance, education_fit, communication_clarity]
    if cover_letter_quality > 0:
        scores.append(cover_letter_quality)
    return {
        "candidate_name": candidate_name,
        "skills_match": skills_match,
        "experience_relevance": experience_relevance,
        "education_fit": education_fit,
        "cover_letter_quality": cover_letter_quality,
        "communication_clarity": communication_clarity,
        "overall": round(sum(scores) / len(scores)),
    }

@function_tool
def check_requirements(
    candidate_name: str,
    requirements: list[str],
    met: list[bool],
) -> dict:
    """
    Check which JD requirements the candidate explicitly meets.
    Pass parallel lists: requirements[i] met by met[i].
    """
    results = [
        {"requirement": r, "met": m}
        for r, m in zip(requirements, met)
    ]
    met_count = sum(met)
    return {
        "candidate": candidate_name,
        "results": results,
        "met_count": met_count,
        "total": len(requirements),
        "percentage": round(met_count / len(requirements) * 100) if requirements else 0,
    }

# ── Agent factory ──────────────────────────────────────────────

def make_screener_agent(job_description: str) -> Agent:
    return Agent(
        name="CV Screener",
        model="gpt-4o",
        tools=[extract_text, score_candidate, check_requirements],
        output_type=CandidateReview,
        instructions=f"""
You are a senior HR professional and hiring manager conducting a highly selective screening of job applications.

The job description you are hiring for:
---
{job_description}
---

MANDATORY RULES:
- Be strict and evidence-based. Do not assume or infer missing information.
- If something is not explicitly stated in the CV or cover letter, treat it as NOT MET.
- Do NOT reward potential — only proven, demonstrated experience counts.
- A score of 7+ means strong and immediately hireable.
- Most candidates should score between 3–6 unless clearly exceptional.
- Every judgment must reference explicit evidence from the candidate’s documents.

PROCESS:

1. Call extract_text with the CV pdf_path.
2. If cover_letter_path is provided, call extract_text again.

3. Call check_requirements:
   - Extract ALL key requirements from the job description.
   - For EACH requirement, mark:
     Met / Partially Met / Not Met
   - Provide direct evidence OR write “No evidence found”.
   - If more than 30% of core requirements are Not Met → cannot be shortlisted.

4. Call score_candidate with scores (1–10):
   - skills_match
   - experience_relevance
   - education_fit
   - cover_letter_quality (0 if none)
   - communication_clarity

SCORING GUIDE:
- 1–3: Major gaps, weak or irrelevant
- 4–6: Partial fit, clear gaps
- 7–8: Strong fit, minor gaps
- 9–10: Exceptional, exceeds requirements

- Each score MUST have a one-sentence justification with evidence.

5. Strengths:
- List EXACTLY 2–3 strengths.
- Must directly relate to the job.
- Must reference specific evidence (skills, tools, achievements).

6. Concerns / Gaps:
- List ALL meaningful gaps:
  missing skills, missing tools, low experience, inconsistencies, overqualification.
- Be direct. Do not soften or hide issues.

7. Summary:
- One concise paragraph.
- Clearly state how well the candidate meets core requirements.
- State whether they are immediately effective or need ramp-up.

8. Final Decision (STRICT):
- Shortlist → ≥70% requirements met, mostly scores 7+, no critical gaps
- Consider → ~50–70% met, some gaps
- Reject → <50% met OR missing critical requirements

- Provide ONE clear sentence justifying the decision.

OUTPUT REQUIREMENTS:
- Be structured, concise, and objective.
- No generic praise or vague statements.
- No assumptions.
- Prioritize accuracy over politeness.
""",
    )

# ── Runner — processes one candidate ───────────────────────────

async def screen_candidate(
    job_description: str,
    cv_path: str,
    cover_letter_path: str | None = None,
) -> CandidateReview:
    agent = make_screener_agent(job_description)
    parts = [f"Please screen this candidate. CV path: {cv_path}"]
    if cover_letter_path:
        parts.append(f"Cover letter path: {cover_letter_path}")
    else:
        parts.append("No cover letter was provided.")
    result = await Runner.run(agent, input=" ".join(parts))
    return result.final_output

# ── Batch runner — runs all candidates in parallel ─────────────

async def screen_all(
    job_description: str,
    candidates: list[dict],  # [{"cv": path, "cover_letter": path|None}]
) -> list[CandidateReview]:
    tasks = [
        screen_candidate(
            job_description,
            c["cv"],
            c.get("cover_letter"),
        )
        for c in candidates
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    reviews = []
    for r in results:
        if isinstance(r, Exception):
            print(f"Agent error for a candidate: {r}")
        else:
            reviews.append(r)

    # Sort by overall score descending
    reviews.sort(key=lambda r: r.overall_score, reverse=True)
    return reviews