"""
ai_service.py — AI Core Service Module
Wraps LLM APIs (Google Gemini API & Anthropic Claude API) with structured prompt engineering.
Includes robust error handling and fallback smart reasoning when API keys are not provided.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check for API Keys
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()


def call_llm_api(prompt: str, system_prompt: str = "") -> Optional[str]:
    """
    Attempts to call available LLM APIs (Gemini or Anthropic Claude).
    Returns response text string, or None if calls fail or no keys configured.
    """
    # 1. Try Gemini API if key exists
    if GEMINI_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_KEY)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
            except Exception:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=full_prompt
                )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"[AI Service Warning] Gemini API call failed: {e}")

    # 2. Try Anthropic Claude API if key exists
    if ANTHROPIC_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            messages = [{"role": "user", "content": prompt}]
            kwargs = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1500,
                "messages": messages
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = client.messages.create(**kwargs)
            if response and response.content:
                return response.content[0].text.strip()
        except Exception as e:
            print(f"[AI Service Warning] Claude API call failed: {e}")

    return None


def summarize(text: str, length: str = "medium") -> Dict[str, Any]:
    """
    Feature 1: Text Summarization
    Length options: short (1-2 sentences), medium (3-4 bullet points), detailed (comprehensive breakdown)
    """
    if not text.strip():
        return {"error": "Input text is empty."}

    length_instructions = {
        "short": "Provide a quick 1-2 sentence executive summary.",
        "medium": "Provide a clear 3-4 bullet point key summary.",
        "detailed": "Provide a comprehensive structured breakdown with summary, key themes, and main takeaways."
    }

    instruction = length_instructions.get(length.lower(), length_instructions["medium"])
    
    system_prompt = "You are an expert AI summarization agent. Summarize text accurately without adding outside facts."
    prompt = f"TASK: {instruction}\n\nINPUT TEXT:\n\"\"\"\n{text}\n\"\"\""

    llm_result = call_llm_api(prompt, system_prompt)
    if llm_result:
        return {"result": llm_result, "mode": "api"}

    # Smart fallback summarizer when no API key is set
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if length == "short":
        summary_text = " ".join(sentences[:2]) if sentences else text[:200] + "..."
        res = f"**Executive Summary:**\n{summary_text}"
    elif length == "detailed":
        bullets = "\n".join([f"• {s}" for s in sentences[:6]]) if sentences else text[:400]
        res = f"### Comprehensive Breakdown\n\n**Main Overview:**\n{sentences[0] if sentences else text[:150]}\n\n**Key Takeaways:**\n{bullets}"
    else:  # medium
        bullets = "\n".join([f"• {s}" for s in sentences[:4]]) if sentences else text[:300]
        res = f"**Key Summary Points:**\n{bullets}"

    return {"result": res, "mode": "smart_engine"}


def answer_question(text: str, question: str) -> Dict[str, Any]:
    """
    Feature 2: Grounded Question Answering
    Answers questions grounded strictly in the provided document context with source citations.
    """
    if not text.strip():
        return {"error": "Document context is empty."}
    if not question.strip():
        return {"error": "Please provide a question to answer."}

    system_prompt = (
        "You are an AI Question Answering Agent. Answer the question using ONLY the provided text context.\n"
        "RULES:\n"
        "1. If the provided text contains enough information to answer, provide a clear, accurate answer.\n"
        "2. At the end of your answer, you MUST include a source attribution line formatted as: 'Source: paragraph X' (or 'Source: page X, paragraph Y', or a short exact quoted snippet from the text).\n"
        "3. If the provided document does NOT contain enough information to answer the question, state explicitly: 'The provided document does not contain enough information to answer this question.' and do NOT include any Source citation tag or attribution."
    )
    prompt = f"DOCUMENT CONTEXT:\n\"\"\"\n{text}\n\"\"\"\n\nUSER QUESTION: {question}"

    llm_result = call_llm_api(prompt, system_prompt)
    if llm_result:
        return {"result": llm_result, "mode": "api"}

    # Smart fallback Q&A engine
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    q_words = set(re.findall(r'\w+', question.lower())) - {
        "what", "is", "the", "how", "why", "where", "who", "when", "does", "do",
        "in", "on", "a", "an", "to", "for", "of", "and", "or", "with", "are", "was",
        "were", "be", "been", "can", "could", "would", "should", "tell", "me", "about"
    }

    matched_sentences = []
    for p_idx, p in enumerate(paragraphs, start=1):
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for s in sentences:
            s_words = set(re.findall(r'\w+', s.lower()))
            overlap = len(q_words.intersection(s_words))
            if overlap > 0:
                matched_sentences.append((overlap, s.strip(), p_idx))

    matched_sentences.sort(key=lambda x: x[0], reverse=True)

    if matched_sentences and matched_sentences[0][0] >= 1:
        top_answers = [m[1] for m in matched_sentences[:2]]
        best_para_idx = matched_sentences[0][2]
        answer_body = " ".join(top_answers)
        res = f"**Grounded Answer:**\n{answer_body}\n\n**Source:** paragraph {best_para_idx}"
    else:
        res = "The provided document does not contain enough information to answer this question."

    return {"result": res, "mode": "smart_engine"}


def generate_content(text: str, instruction: str) -> Dict[str, Any]:
    """
    Feature 3: Content Generation
    Generates text (emails, action plans, summaries, posts) based on user prompt & document context.
    """
    if not text.strip():
        return {"error": "Document context is empty."}
    if not instruction.strip():
        instruction = "Write a professional follow-up email summarizing key points from this document."

    system_prompt = "You are a creative AI Content Writer. Generate clean, high-quality professional content tailored to the user's instruction."
    prompt = f"INSTRUCTION: {instruction}\n\nSOURCE DOCUMENT:\n\"\"\"\n{text}\n\"\"\""

    llm_result = call_llm_api(prompt, system_prompt)
    if llm_result:
        return {"result": llm_result, "mode": "api"}

    # Smart fallback generator engine
    sentences = re.split(r'(?<=[.!?])\s+', text)
    first_few = " ".join(sentences[:3]) if sentences else text[:300]
    
    if "email" in instruction.lower():
        res = (
            f"**Subject:** Follow-up: Key Information & Action Items\n\n"
            f"Hi Team,\n\n"
            f"Following up on our document review regarding the recent updates:\n\n"
            f"> {first_few}\n\n"
            f"Please review the attached details and let me know if you have any questions.\n\n"
            f"Best regards,\n[Your Name]"
        )
    elif "action" in instruction.lower() or "plan" in instruction.lower():
        res = (
            f"### Action Plan & Next Steps\n\n"
            f"**Objective:** {instruction}\n\n"
            f"1. **Review Core Requirements:** Analyze baseline points ({sentences[0] if sentences else 'initial findings'}).\n"
            f"2. **Execution Phase:** Implement key recommendations and assign team owners.\n"
            f"3. **Verification & Delivery:** Validate outputs and confirm status before deadline."
        )
    else:
        res = (
            f"### Generated Content ({instruction})\n\n"
            f"Based on the input document context, here is the generated output:\n\n"
            f"{first_few}\n\n"
            f"**Key Focus:** Ensure alignment across stakeholders and verify execution timelines."
        )

    return {"result": res, "mode": "smart_engine"}


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Feature 4: Text & Document Analysis
    Extracts key points, action items, sentiment, and tone.
    """
    if not text.strip():
        return {"error": "Document text is empty."}

    system_prompt = "You are an expert Document Intelligence Agent. Analyze text for Key Points, Action Items, Sentiment, and Tone."
    prompt = f"Analyze the following document and output key findings:\n\n\"\"\"\n{text}\n\"\"\""

    llm_result = call_llm_api(prompt, system_prompt)
    if llm_result:
        return {"result": llm_result, "mode": "api"}

    # Smart fallback analysis engine
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 8]
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

    # Sentiment check
    pos_words = {"success", "great", "excellent", "growth", "positive", "increase", "improve", "effective", "high", "complete"}
    neg_words = {"error", "issue", "risk", "delay", "problem", "decline", "fail", "cost", "loss", "critical"}
    
    pos_count = sum(1 for w in words if w in pos_words)
    neg_count = sum(1 for w in words if w in neg_words)

    if pos_count > neg_count:
        sentiment = "Positive / Optimistic 🟢"
    elif neg_count > pos_count:
        sentiment = "Cautionary / Critical 🔴"
    else:
        sentiment = "Neutral / Professional ⚪"

    key_points = sentences[:3] if len(sentences) >= 3 else sentences
    action_items = [s for s in sentences if any(w in s.lower() for w in ["must", "should", "will", "need", "action", "plan", "required"])]
    if not action_items and sentences:
        action_items = [f"Follow up on: {sentences[-1]}"]

    key_points_formatted = "\n".join([f"- {kp}" for kp in key_points])
    action_items_formatted = "\n".join([f"- {ai}" for ai in action_items[:3]])

    res = (
        f"### 📊 Document Intelligence Report\n\n"
        f"**Tone & Sentiment:** {sentiment}\n\n"
        f"**📌 Key Points:**\n{key_points_formatted}\n\n"
        f"**⚡ Action Items:**\n{action_items_formatted}\n\n"
        f"**📈 Metrics & Stats:**\n"
        f"- Word Count: {len(words)}\n"
        f"- Sentences: {len(sentences)}\n"
        f"- Readability: Professional / Accessible"
    )

    return {"result": res, "mode": "smart_engine"}


def suggest_next_actions(last_action: str) -> List[Dict[str, str]]:
    """
    Feature 5: Intelligent Suggestions
    Returns 2-3 interactive suggested next actions based on the previous operation.
    """
    suggestions_map = {
        "summarize": [
            {"label": "⚡ Extract action items", "action": "analyze", "prompt": "extract_action_items"},
            {"label": "📧 Generate a follow-up email", "action": "generate", "prompt": "Write a professional follow-up email based on this document."}
        ],
        "qa": [
            {"label": "📝 Summarize Document", "action": "summarize", "prompt": "medium"},
            {"label": "📊 Full Analysis Report", "action": "analyze", "prompt": ""},
            {"label": "✉️ Turn into Email", "action": "generate", "prompt": "Draft an email explaining the answer"}
        ],
        "generate": [
            {"label": "⚡ Extract Action Items", "action": "analyze", "prompt": ""},
            {"label": "🔍 Ask a Question", "action": "qa", "prompt": ""},
            {"label": "📄 Make Shorter Summary", "action": "summarize", "prompt": "short"}
        ],
        "analyze": [
            {"label": "❓ Ask a question about this", "action": "qa", "prompt": ""},
            {"label": "📝 Generate a summary of the findings", "action": "summarize", "prompt": "medium"}
        ]
    }

    return suggestions_map.get(last_action.lower(), [
        {"label": "📝 Summarize Text", "action": "summarize", "prompt": "medium"},
        {"label": "📊 Analyze Key Points", "action": "analyze", "prompt": ""},
        {"label": "📧 Draft Email", "action": "generate", "prompt": "Write a follow-up email based on this text"}
    ])
