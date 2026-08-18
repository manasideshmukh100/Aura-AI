"""
test_agent.py — Automated Verification Script for AURA AI Smart Automation Agent
Tests:
1. File text extraction (file_utils.py)
2. AI Service logic & fallback engine (ai_service.py)
3. Summarization, Grounded Q&A, Content Generation, Analysis
4. Suggested Next Actions generation
"""

import os
import sys

# Add backend directory to module search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import file_utils
import ai_service

SAMPLE_TEXT = """
PROJECT RELEASE ANNOUNCEMENT: AURA AI Platform v1.0
Target Launch Date: September 1, 2026
Lead Engineer: Prabhakar Deshmukh

The AURA AI Automation Agent simplifies document workflows by offering automatic summarization,
grounded question answering, email generation, and document intelligence.

Key Deliverables:
- Implement Dark Theme UI with glassmorphic aesthetic.
- Develop cute animated SVG smiley mascot with idle, thinking, and happy mood states.
- Ensure all API keys are kept secure in .env environment variables.
- Support .txt and .pdf document uploads under 5MB.
"""


def test_file_utils():
    print("[TEST 1] Testing file_utils extraction...")
    text_bytes = SAMPLE_TEXT.encode("utf-8")
    extracted, err = file_utils.extract_text_from_file("sample.txt", text_bytes)
    assert not err, f"Extraction failed: {err}"
    assert "AURA AI Platform" in extracted, "Extracted text missing expected content."
    print("  -> PASSED: file_utils test!")


def test_ai_summarize():
    print("[TEST 2] Testing Summarization Feature...")
    res = ai_service.summarize(SAMPLE_TEXT, length="medium")
    assert "result" in res, "Summarization output missing result."
    print(f"   Summary Mode: {res.get('mode')}")
    preview = res['result'][:120].encode('ascii', 'ignore').decode('ascii')
    print(f"   Output Preview: {preview}...")
    print("  -> PASSED: Summarize feature!")


def test_ai_qa():
    print("[TEST 3] Testing Grounded Q&A Feature...")
    q = "What is the launch date for AURA AI?"
    res = ai_service.answer_question(SAMPLE_TEXT, q)
    assert "result" in res, "Q&A output missing result."
    print(f"   Question: {q}")
    ans_clean = res['result'].encode('ascii', 'ignore').decode('ascii')
    print(f"   Answer Preview: {ans_clean[:120]}...")
    print("  -> PASSED: Grounded Q&A feature!")


def test_ai_generate():
    print("[TEST 4] Testing Content Generation Feature...")
    instr = "Write a follow-up email about the launch date"
    res = ai_service.generate_content(SAMPLE_TEXT, instr)
    assert "result" in res, "Generate output missing result."
    preview = res['result'][:120].encode('ascii', 'ignore').decode('ascii')
    print(f"   Output Preview: {preview}...")
    print("  -> PASSED: Content Generation feature!")


def test_ai_analyze():
    print("[TEST 5] Testing Document Analysis Feature...")
    res = ai_service.analyze_text(SAMPLE_TEXT)
    assert "result" in res, "Analyze output missing result."
    preview = res['result'][:120].encode('ascii', 'ignore').decode('ascii')
    print(f"   Output Preview: {preview}...")
    print("  -> PASSED: Document Analysis feature!")


def test_suggested_actions():
    print("[TEST 6] Testing Suggested Next Actions...")
    actions = ai_service.suggest_next_actions("summarize")
    assert len(actions) >= 2, "Expected at least 2 suggested next actions."
    labels_clean = [a['label'].encode('ascii', 'ignore').decode('ascii') for a in actions]
    print(f"   Suggestions: {labels_clean}")
    print("  -> PASSED: Suggested Next Actions!")


if __name__ == "__main__":
    print("==================================================")
    print("Starting AURA AI Agent Automated Verification Suite")
    print("==================================================")
    test_file_utils()
    test_ai_summarize()
    test_ai_qa()
    test_ai_generate()
    test_ai_analyze()
    test_suggested_actions()
    print("==================================================")
    print("SUCCESS: ALL VERIFICATION TESTS PASSED PERFECTLY!")
    print("==================================================")
