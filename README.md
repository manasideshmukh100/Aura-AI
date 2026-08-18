# AURA AI — AI Smart Automation Agent (Dark Theme UI + Animated Mascot)

A lightweight, enterprise-ready AI productivity web application that processes documents, pastes text, and executes **Summarization**, **Grounded Q&A**, **Content Generation**, and **Document Intelligence Analysis** with an interactive **Cute Animated Smiley Mascot** and **Intelligent Suggested Next Actions**.

---

## 🌟 Key Features

1. **Text & Document Summarization**: Selectable summary length (`short` 1-2 sentences, `medium` 3-4 bullet points, or `detailed` full structured breakdown).
2. **Grounded Question Answering**: Answers questions grounded strictly in the provided document context to prevent AI hallucinations.
3. **Content Generation**: Generates custom emails, action plans, briefings, or posts based on document context & custom instructions.
4. **Document Intelligence Analysis**: Extracts key points, action items, metrics, readability, and sentiment/tone (`Positive 🟢`, `Cautionary 🔴`, `Neutral ⚪`).
5. **Intelligent Suggested Actions**: After every response, the agent presents 2-3 interactive action buttons (e.g. *"Draft Follow-up Email"*, *"Extract Action Items"*) that re-run the pipeline with 1 click.
6. **Cute Animated SVG Mascot**: Features 4 distinct animated mood states (`idle`, `thinking`, `happy/success`, `sad/error`) with real-time speech bubble feedback and interactive click/wink reactions.
7. **Dark Theme Glassmorphic UI**: High-contrast charcoal design system with violet & cyan glowing accents, responsive layout, drag-and-drop file upload (`.txt`, `.pdf`, `.md`, `.csv`), sample document loader, and Markdown export.

---

## 🏗️ Architecture & Component Overview

```
                        ┌──────────────────────────────────────────────┐
                        │      Frontend UI (Dark Theme + Mascot)       │
                        │   (HTML5 / Vanilla CSS / JS / SVG Engine)    │
                        └──────────────────────┬───────────────────────┘
                                               │
                                       HTTP REST Requests
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │       FastAPI Web Server (main.py)           │
                        │   - Endpoints: /summarize, /qa, /generate,   │
                        │     /analyze, /upload, /health               │
                        └──────────────────────┬───────────────────────┘
                                               │
                               ┌───────────────┴───────────────┐
                               ▼                               ▼
                     ┌──────────────────┐            ┌──────────────────┐
                     │   file_utils.py  │            │   ai_service.py  │
                     │ (PyPDF, Text     │            │ (Prompt Engine + │
                     │  Extractors)     │            │  Gemini/Claude)  │
                     └──────────────────┘            └──────────────────┘
```

### Directory Structure
```
ai-smart-agent/
├── backend/
│   ├── ai_service.py     # Prompt engineering & LLM API wrappers (Gemini / Claude / Fallback)
│   ├── file_utils.py     # File text extraction (.txt, .pdf, .md, .csv) & validation
│   ├── main.py           # FastAPI REST API endpoints & CORS middleware
│   ├── requirements.txt  # Python backend dependencies
│   └── .env.example      # Environment variable template for API keys
├── frontend/
│   ├── index.html        # Glassmorphic layout & SVG Mascot container
│   ├── styles.css        # Dark theme design system & glowing micro-animations
│   ├── mascot.js         # Animated SVG Smiley Mascot mood engine (idle/thinking/happy/sad)
│   └── app.js            # UI controller, document handler, API client & suggested actions
├── test_agent.py         # Automated verification script
└── README.md             # Project documentation & review guide
```

---

## 🎯 Prompt Design & Grounding Strategy (For Reviewers)

| Feature | Prompt Engineering & Design Strategy |
| :--- | :--- |
| **Grounded Q&A** | System prompt explicitly constrains the LLM: *"Answer the question using ONLY the provided text context. If the answer cannot be found, state: 'The provided document does not contain enough information'..."* This prevents hallucinating facts outside the document. |
| **Summarization** | Parametric prompts dynamically adjust constraints based on the `length` setting (`short` forces 1-2 sentence executive summary, `medium` forces 3-4 bullet points, `detailed` forces a full overview with key themes). |
| **Content Generation** | Uses zero-shot prompt framing to transform abstract document context into structured communication formats (e.g., formal email with subject line, action plan with owner steps). |
| **Document Analysis** | System prompt instructs structured breakdown extracting sentiment indicators, high-priority action items (filtering action verbs), and key takeaways. |

---

## 🚀 Quick Setup & How to Run

### Option 1: Running Backend + Frontend

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Configure API Key**:
   Copy `.env.example` to `.env` and add your Gemini or Claude API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *Note: If no API key is provided, the agent automatically runs the built-in Smart Agent Engine!*

4. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. **Open Frontend**:
   Open `frontend/index.html` directly in your browser or serve using a simple HTTP server (e.g., `python -m http.server 3000` inside `frontend/`).

---

## ⚡ Automated Verification

To run automated verification tests against the backend services:
```bash
python test_agent.py
```

---

## 📝 Demo Video Checklist (For Submission)

1. **Show Mascot States**: Point out the mascot bobbing in `idle`, pulsing during `thinking`, and bouncing happily on `success`.
2. **Demonstrate Sample Docs**: Click **Sample Docs** -> **Tech Project Specification** to show instant loading.
3. **Execute Summarize**: Run a `medium` summary and demonstrate the result card.
4. **Click Suggested Action**: Click the suggested **"Draft Follow-up Email"** chip button to show seamless automated re-execution!
5. **Demonstrate Error Handling**: Upload an empty file or run Q&A without input to show graceful error recovery.
