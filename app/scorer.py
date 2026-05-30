import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert HR analyst specializing in AI and machine learning literacy assessment.

Your task is to read a resume and score the candidate's AI literacy on a scale from 0 to 10.

SCORING RUBRIC:
- 0.0–0.9  : No mention of AI, ML, or data science. Completely unrelated field.
- 1.0–1.9  : Incidental AI exposure only (e.g., used an AI-powered tool like Grammarly or Canva).
- 2.0–2.9  : Basic consumer-level AI awareness. May mention ChatGPT or "AI tools" without technical depth.
- 3.0–3.9  : Familiarity with AI concepts. Took an introductory ML or AI course. Can use off-the-shelf models.
- 4.0–4.9  : Practical AI application. Used ML libraries (scikit-learn, HuggingFace) or AI APIs in projects.
- 5.0–5.9  : Solid applied ML skills. Has built and deployed ML models. Comfortable with Python data stack.
- 6.0–6.9  : Intermediate ML practitioner. Experience with deep learning frameworks (TensorFlow, PyTorch).
- 7.0–7.9  : Advanced ML/AI skills. LLM integration, RAG pipelines, prompt engineering, or AI system design.
- 8.0–8.9  : Strong AI expertise. Published work, open-source contributions, or production AI systems at scale.
- 9.0–9.9  : Deep AI specialization. PhD-level research, novel model development, or significant industry impact.
- 10.0     : Pioneering AI expert. Core contributor to foundational models or transformative AI research.

INSTRUCTIONS:
- Read the resume carefully for any signals of AI/ML knowledge: tools, frameworks, projects, education, certifications, job roles, publications.
- Be objective and calibrate to the full range — most candidates will score between 0 and 6.
- Respond with ONLY a single decimal number (e.g., 4.5). No explanation, no other text."""


def score_resume(filename: str, text: str) -> tuple[str, float]:
    truncated = text[:15000]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Resume content:\n\n{truncated}"}
        ],
    )
    raw = response.content[0].text.strip()
    score = float(raw)
    score = round(max(0.0, min(10.0, score)), 1)
    return filename, score
