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
    print("[TEST 3] Testing Grounded Q&A Feature with Source Citations...")
    q = "What is the launch date for AURA AI?"
    res = ai_service.answer_question(SAMPLE_TEXT, q)
    assert "result" in res, "Q&A output missing result."
    print(f"   Question: {q}")
    ans_clean = res['result'].encode('ascii', 'ignore').decode('ascii')
    print(f"   Answer Preview: {ans_clean}...")
    assert "Source:" in res['result'] or "source:" in res['result'].lower(), "Q&A output missing source citation tag."
    print("  -> PASSED: Grounded Q&A Source Citation!")

    # Test unanswerable question
    unans_q = "What is the stock price of Apple?"
    unans_res = ai_service.answer_question(SAMPLE_TEXT, unans_q)
    assert "does not contain enough information" in unans_res['result'].lower(), "Expected explicit no-info message for unanswerable question."
    assert "Source:" not in unans_res['result'], "Unanswerable question should NOT contain a source tag."
    print("  -> PASSED: Unanswerable question explicitly skips source tag!")


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
    print("[TEST 6] Testing Chained Action Workflow Suggestions...")
    
    # Summarize follow-up actions check
    sum_actions = ai_service.suggest_next_actions("summarize")
    sum_labels = [a['label'].lower() for a in sum_actions]
    assert any("extract action items" in l for l in sum_labels), "Summarize suggestions missing 'Extract action items'"
    assert any("follow-up email" in l for l in sum_labels), "Summarize suggestions missing 'Generate a follow-up email'"
    print("  -> PASSED: Summarize workflow suggestions verified!")

    # Analyze follow-up actions check
    ana_actions = ai_service.suggest_next_actions("analyze")
    ana_labels = [a['label'].lower() for a in ana_actions]
    assert any("ask a question" in l for l in ana_labels), "Analyze suggestions missing 'Ask a question about this'"
    assert any("summary of the findings" in l for l in ana_labels), "Analyze suggestions missing 'Generate a summary of the findings'"
    print("  -> PASSED: Analyze workflow suggestions verified!")


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
