# ai_client.py
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re
from typing import Any, Dict, List, Optional


class AIClient:
    def __init__(self, api_key, provider="openai"):
        if not api_key:
            raise ValueError("API Key is required")

        self.provider = provider

        if provider == "xai":
            # xAI (Grok)
            self.llm = ChatOpenAI(
                temperature=0.7,
                openai_api_key=api_key,
                base_url="https://api.x.ai/v1",
                model_name="grok-beta",
            )
        elif provider == "groq":
            # Groq
            self.llm = ChatGroq(
                temperature=0.7,
                groq_api_key=api_key,
                model_name="llama-3.3-70b-versatile",
            )
        else:
            # OpenAI
            self.llm = ChatOpenAI(
                temperature=0.7,
                openai_api_key=api_key,
                model_name="gpt-3.5-turbo",
            )

        self.output_parser = StrOutputParser()

    # -------------------------
    # Core features (UNCHANGED)
    # -------------------------
    def analyze_resume(self, resume_text):
        prompt_template = """
        You are an expert HR and Technical Recruiter. Analyze the following resume text extracted from a document.

        Resume Text:
        {resume_text}

        Please provide the output in the following format:
        1. **Candidate Summary**: A brief professional summary with sub-headings
        2. **Skills Identified**: List of technical and soft skills.
        3. **Suggested Domain**: The most likely professional domain (e.g., Data Science, Frontend Dev, Digital Marketing).
        4. **Projects summary**: Give the key summary of the projects done by the user.
        5. **Candidate internship** : Provide the candidate' internship details.
        6. **Candidates personality ** : What's the candidates desire , what's his soft-skills etc..
        7. **Preferable domain for the candidate** :Provise the suggested domain for the user with a brief explanation
        """

        prompt = PromptTemplate(input_variables=["resume_text"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"resume_text": resume_text})

    def generate_interview_question(self, domain, history):
        prompt_template = """
        You are an interviewer for the domain: {domain}.

        Here is the conversation history so far:
        {history}

        Ask the next technical or behavioral question (mostly technical)irrelevant to the previous answer to assess the candidate's depth.
        Only ask ONE question.
        """

        prompt = PromptTemplate(input_variables=["domain", "history"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"domain": domain, "history": history})

    def evaluate_answer(self, question, answer, domain):
        prompt_template = """
        You are an interviewer for the domain: {domain}.

        Question: {question}
        Candidate Answer: {answer}

        Provide a very brief feedback (2-3 sentences) on the answer and whether it was correct or how it could be improved.
        At last after all the explanation of the correct answer provide the depth technical summary of how the candidate lags in technical knowledge in their choosen domain and how to improve themselves
        """

        prompt = PromptTemplate(input_variables=["question", "answer", "domain"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"question": question, "answer": answer, "domain": domain})

    def generate_roadmap(self, domain, resume_summary):
        prompt_template = """
Your task is to generate a CLEAN, PRACTICAL, and INDUSTRY-READY learning roadmap
to advance the candidate to the NEXT LEVEL (Senior / Expert) in the given domain.

Domain:
{domain}

Candidate Background (from resume analysis):
{resume_summary}

====================
STRICT REQUIREMENTS
====================

1. DURATION RULE
- Total duration MUST be between 10 to 15 weeks.
- Do NOT artificially increase weeks by splitting simple topics.
- If content fits in fewer weeks, keep it concise (prefer depth over length).

2. WEEK STRUCTURE (MANDATORY)
For EACH week, strictly follow this structure:

Week X – <Clear Topic Title>

• Goal:
  (What skill gap this week closes)

• Concepts & Technologies:
  (Bullet list of concrete concepts, tools, frameworks)

-> Learning Resources (ONLY VERIFIED SOURCES):
  - Official documentation links ONLY
    (examples: python.org, pytorch.org, tensorflow.org, huggingface.co, scikit-learn.org, spacy.io) and also some websites that are trusted websites.
  - OR tutorial videos abailable in online , these links must not provide any page not found error , it should be trusted and 100% correct link
  - Avoid blogspam, Medium paywalls, random GitHub READMEs, or dead links.
  - Ensure links are well-known and highly stable (NO 404-prone URLs).

• Hands-on Project:
  - ONE concrete, real-world project
  - Must transform theory → practical skill
  - Mention dataset / tool / expected output
  - Can provide the sample projects github link, check the github link is open correctly before giving it.


3. LINK QUALITY RULE (VERY IMPORTANT)
- Every link must be:
  - Official OR widely trusted
  - Actively maintained
  - Commonly used by professionals
  - before generating the links check the the page is good and has no error or no content and shouldn't make page not found error.
- If unsure, prefer:
  - Official documentation home page
  - YouTube search result from approved channels (mention channel name)

4. TECHNICAL DEPTH RULE
- Content must be INTERMEDIATE → ADVANCED
- Avoid beginner-level explanations
- Assume the learner already knows basics

5. OUTPUT FORMAT
- Use clean Markdown
- No emojis
- No motivational fluff
- No concluding paragraph
- No disclaimers
- Only the roadmap content

====================
BEGIN ROADMAP
====================
        """

        prompt = PromptTemplate(input_variables=["domain", "resume_summary"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"domain": domain, "resume_summary": resume_summary})

    def generate_mcqs(self, domain, resume_text, num_questions=8):
        prompt_template = """
        You are an expert interviewer and test designer for the domain: {domain}.

        Create a multiple-choice test personalized to the candidate's resume and relavent to the choosen {domain} domain.Only the technical questions and no other generic questions.

        Resume Text:
        {resume_text}

        Domain:
        {domain}

        Rules:
        - Generate exactly {num_questions} MCQs.
        - Each question must have 4 options labeled A, B, C, D.
        - Questions must match the domain and the candidate's skills/projects.
        - Mix difficulty: easy (2), medium (4), hard (2) if {num_questions}=8 (scale similarly if different).
        - Avoid repeating the same concept.
        - Output MUST be valid JSON ONLY (no markdown, no extra text).

        JSON schema (strict):
        [
          {{
            "question": "string",
            "options": ["A ...", "B ...", "C ...", "D ..."],
            "answer_index": 0,
            "explanation": "1-2 sentence explanation"
          }}
        ]
        """
        prompt = PromptTemplate(input_variables=["domain", "resume_text", "num_questions"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        raw = chain.invoke({"domain": domain, "resume_text": resume_text, "num_questions": num_questions})

        raw = (raw or "").strip()
        try:
            return json.loads(raw)
        except Exception:
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1 and end > start:
                return json.loads(raw[start : end + 1])
            raise ValueError("LLM did not return valid JSON for MCQs.")

    def generate_skill_distribution(self, resume_text, max_skills=10):
        prompt_template = """
You are a technical recruiter and skills analyst.

Extract the TOP {max_skills} concrete skills from the resume text and assign a realistic weight (percentage)
based on prominence (frequency + project relevance + experience relevance).

Rules:
- Output MUST be valid JSON ONLY (no markdown, no extra text).
- Total weight must sum to 100 exactly.
- Prefer concrete skills: languages, frameworks, tools, platforms.
- Avoid duplicates and generic words.
- category must be one of ["Programming","Framework","Tool","Database","Cloud","ML/AI","Other"].

Resume Text:
{resume_text}

Return schema:
[
  {{"skill":"Python","weight":30,"category":"Programming"}},
  {{"skill":"SQL","weight":15,"category":"Database"}}
]
"""
        prompt = PromptTemplate(input_variables=["resume_text", "max_skills"], template=prompt_template)
        chain = prompt | self.llm | self.output_parser
        raw = chain.invoke({"resume_text": resume_text, "max_skills": int(max_skills)})
        raw = (raw or "").strip()

        try:
            data = json.loads(raw)
        except Exception:
            s = raw.find("[")
            e = raw.rfind("]")
            if s != -1 and e != -1 and e > s:
                data = json.loads(raw[s : e + 1])
            else:
                raise ValueError("LLM did not return valid JSON for skill distribution.")

        if not isinstance(data, list) or not data:
            raise ValueError("Skill distribution JSON is empty/invalid.")

        cleaned = []
        total = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            skill = str(item.get("skill", "")).strip()
            category = str(item.get("category", "Other")).strip()
            w = item.get("weight", 0)

            if not skill:
                continue
            try:
                w = int(w)
            except Exception:
                continue

            cleaned.append({"skill": skill, "weight": w, "category": category})
            total += w

        if total != 100 and total > 0:
            factor = 100.0 / total
            new_total = 0
            for i in range(len(cleaned)):
                cleaned[i]["weight"] = int(round(cleaned[i]["weight"] * factor))
                new_total += cleaned[i]["weight"]
            drift = 100 - new_total
            if cleaned:
                cleaned[0]["weight"] += drift

        return cleaned

    # -------------------------
    # Assistive Mode (FIX)
    # -------------------------
    def assistive_tutor(
        self,
        user_message: str,
        context: Optional[Dict[str, str]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        allow_links: bool = False,
    ) -> str:
        """
        Added because your app.py calls ai.assistive_tutor().
        Does NOT change your other prompts; it's a new, separate prompt.
        """
        context = context or {}
        chat_history = chat_history or []

        domain = (context.get("domain") or "").strip()
        resume_summary = (context.get("resume_summary") or "").strip()
        roadmap_text = (context.get("roadmap_text") or "").strip()

        # Keep chat history small to reduce tokens
        hist_lines = []
        for m in chat_history[-10:]:
            role = m.get("role", "")
            content = (m.get("content") or "").strip()
            if content:
                hist_lines.append(f"{role.upper()}: {content}")
        history_text = "\n".join(hist_lines)

        link_rule = "You MAY include links ONLY if the user explicitly asked for links/resources." if allow_links else "Do NOT include any links or URLs."

        prompt_template = f"""
You are a real-time study tutor.

Style rules:
- Teach step-by-step.
- Ask short check questions to confirm understanding.
- Give small examples.
- Keep answers practical and directly helpful.
- {link_rule}

Use these context fields if relevant:
- Domain: {{domain}}
- Resume summary: {{resume_summary}}
- Roadmap: {{roadmap_text}}

Conversation so far:
{{history_text}}

User message:
{{user_message}}

Now respond as the tutor.
"""

        prompt = PromptTemplate(
            input_variables=["domain", "resume_summary", "roadmap_text", "history_text", "user_message"],
            template=prompt_template,
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke(
            {
                "domain": domain,
                "resume_summary": resume_summary,
                "roadmap_text": roadmap_text,
                "history_text": history_text,
                "user_message": user_message,
            }
        )

    # -------------------------
    # Placement / Job Links
    # -------------------------
    def generate_job_suggestions(self, resume_text: str, domain: str, linkedin_url: str = "") -> str:
        """
        A) AI Suggested Jobs (Resume + Target Domain)
        Returns markdown (not JSON) because your app renders markdown.
        """
        prompt_template = """
You are a placement advisor.

Goal:
Suggest job titles that match the candidate's resume + target domain.
Also provide skills gap and the exact keywords to search.

Candidate Resume Text:
{resume_text}

Target Domain:
{domain}

LinkedIn Profile URL (optional):
{linkedin_url}

Output format (Markdown):
- 8 to 12 job titles (bullet list) with the apply link
- For each title: (1) Why it fits (1 line) (2) Skills gap (2-4 bullets) (3) Search keywords (comma-separated)
- Add a "Where to apply" section with SAFE apply-search URLs (NOT specific vacancy URLs and should not give the on the website link without search) for:
  1) LinkedIn jobs search
  2) Naukri search
  3) Indeed search
Rules for URLs:
- DO NOT invent specific job posting URLs.
- Use only search URLs (these won't become 404 easily).
"""
        prompt = PromptTemplate(
            input_variables=["resume_text", "domain", "linkedin_url"],
            template=prompt_template,
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"resume_text": resume_text, "domain": domain, "linkedin_url": linkedin_url})

    def generate_employability_search_list(
        self,
        resume_text: str,
        domain: str,
        location: str = "",
        experience_level: str = "",
        search_role: str = "",
    ) -> str:
        """
        B) Employability Search List (Search Queries + Filters)
        ✅ Updated to accept search_role (required by updated app.py).
        Returns markdown (not JSON).
        """
        # sanitize inputs
        domain = (domain or "").strip()
        location = (location or "").strip()
        experience_level = (experience_level or "").strip()
        search_role = (search_role or "").strip()

        prompt_template = """
You are an employability search strategist.

Candidate Resume Text:
{resume_text}

Target Domain:
{domain}

Job Role to Search (must be used as the primary role phrase):
{search_role}

Optional Preferences:
- Location: {location}
- Experience level: {experience_level}

Task:
Generate a practical job search kit.

Output format (Markdown):
1) Recommended job portals (India-focused + global) as plain names (no URLs)
2) Boolean search strings (for LinkedIn / Naukri / Indeed):
   - Provide 6 variants of boolean strings using the role + skills from resume
3) Filters checklist:
   - location, experience, salary (optional), job type, freshness, company type
4) Keywords list:
   - 25 to 40 keywords to try, grouped by (skills/tools), (titles), (domains)
5) Ready-to-use SEARCH URLs (SAFE search URLs only; not specific vacancies):
   - LinkedIn Jobs search URL (use query + location when possible)
   - Naukri search URL
   - Indeed search URL

Rules:
- Do NOT generate specific job posting URLs.
- Do NOT claim "this vacancy is open" or "apply link works". Only provide safe search URLs and search strings.
- Use the search_role as the main title phrase.
"""
        prompt = PromptTemplate(
            input_variables=["resume_text", "domain", "search_role", "location", "experience_level"],
            template=prompt_template,
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke(
            {
                "resume_text": resume_text,
                "domain": domain,
                "search_role": search_role,
                "location": location,
                "experience_level": experience_level,
            }
        )
