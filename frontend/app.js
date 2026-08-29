/**
 * app.js — Main Application Controller for AURA AI Smart Agent
 * Connects Frontend UI, Mascot Engine, Backend FastAPI REST API, and Smart Fallback.
 */

const API_BASE_URL = 'https://aura-ai-fehn.onrender.com/api';

// Pre-loaded Sample Documents
const SAMPLE_DOCUMENTS = {
  project: `PROJECT SPECIFICATION: Autonomous AI Task Automation System v2.0
Target Release: Q4 2026
Lead Architecture Team: Core AI Systems & Infrastructure

1. Executive Summary
The Autonomous AI Task Automation System (AURA AI) provides enterprise-grade multi-modal document reasoning, natural language question answering, and automated content generation. Designed for low latency, zero zero-trust data leaks, and high throughput.

2. Key Functional Requirements
- Multi-format ingestion: Parse .txt, .pdf, .md, and .csv files up to 10MB cleanly.
- Grounded Q&A: Strictly limit AI responses to provided document context to eliminate hallucinations.
- Intelligent Suggestions: Auto-generate 3 contextual follow-up actions after every output.
- Performance SLA: Response time under 2.5 seconds for documents under 50,000 tokens.

3. Milestones & Deadlines
- Phase 1 (Data Extractor & Core API): Completed Aug 10, 2026
- Phase 2 (Dark Theme UI & Animated Mascot Integration): In Review (Deadline: Aug 25, 2026)
- Phase 3 (Enterprise Deployment & Load Testing): Scheduled Sept 15, 2026

4. Risk Mitigation & Compliance
All user text must be encrypted in transit using TLS 1.3. API keys must be loaded exclusively via environment variables (.env).`,

  sales: `Q2 SALES & REVENUE PERFORMANCE BRIEFING
Date: August 2026 | Prepared by: Strategic Growth Analytics

1. Financial Highlights
- Total Q2 Revenue: $4.25 Million (YoY growth of +28.4%)
- Gross Profit Margin: 72.1% (up 3.5% from Q1)
- Monthly Recurring Revenue (MRR): $1.42 Million

2. Regional Revenue Breakdown
- North America: $2.10M (49.4% share) — High expansion driven by Enterprise tier adoption.
- Europe (EMEA): $1.35M (31.7% share) — Steady growth in Germany & UK financial sector.
- Asia-Pacific (APAC): $800K (18.9% share) — Rapid acceleration in SaaS startup segment.

3. Critical Action Items
- Scale APAC sales engineering team by 4 hires in Q3 to meet enterprise trial demand.
- Optimize customer onboarding workflow to reduce time-to-value from 14 days down to 5 days.
- Launch autumn promotional campaign targeting mid-market tech companies.`,

  feedback: `CUSTOMER FEEDBACK & PRODUCT REVIEW SUMMARY
Source: Q2 Customer Satisfaction Survey (1,240 Enterprise Users)

1. Overall Sentiment Index
Net Promoter Score (NPS): 68 (Strong Positive 🟢)
User Satisfaction Rating: 4.7 / 5.0

2. Top Praise Points
- "The dark-themed interface and real-time mascot feedback make processing reports fun and effortless."
- "Grounded Q&A feature saved our legal compliance team over 15 hours per week of manual reading."
- "Instant export to Markdown format allows seamless copy-paste into Notion & Jira."

3. Feature Requests & User Pain Points
- Request 1: Add direct integration for Google Drive and Slack notifications.
- Request 2: Allow bulk upload of multiple PDF files simultaneously.
- Request 3: Support custom theme accent color picker in user settings.`
};

class AppController {
  constructor() {
    this.currentAction = 'summarize';
    this.currentInputText = '';
    this.history = [];
    
    this.initElements();
    this.initEventListeners();
    this.generateBackgroundStars();
    this.checkBackendHealth();
  }

  initElements() {
    // Input elements
    this.documentInput = document.getElementById('documentInput');
    this.charCount = document.getElementById('charCount');
    this.clearInputBtn = document.getElementById('clearInputBtn');

    // File upload elements
    this.dropZone = document.getElementById('dropZone');
    this.fileInput = document.getElementById('fileInput');
    this.fileInfo = document.getElementById('fileInfo');
    this.fileName = document.getElementById('fileName');
    this.removeFileBtn = document.getElementById('removeFileBtn');

    // Tabs & action cards
    this.tabBtns = document.querySelectorAll('.tab-btn');
    this.tabContents = document.querySelectorAll('.tab-content');
    this.actionCards = document.querySelectorAll('.action-card');
    this.subGroups = document.querySelectorAll('.sub-group');

    // Action sub-inputs
    this.summaryLengthSelect = document.getElementById('summaryLengthSelect');
    this.questionInput = document.getElementById('questionInput');
    this.instructionInput = document.getElementById('instructionInput');

    // Execution button & spinner
    this.runActionBtn = document.getElementById('runActionBtn');
    this.btnSpinner = document.getElementById('btnSpinner');

    // Output elements
    this.resultBody = document.getElementById('resultBody');
    this.suggestedSection = document.getElementById('suggestedSection');
    this.suggestedChips = document.getElementById('suggestedChips');
    this.resultFooter = document.getElementById('resultFooter');
    this.engineBadge = document.getElementById('engineBadge');

    // Action footer buttons
    this.copyResultBtn = document.getElementById('copyResultBtn');
    this.downloadResultBtn = document.getElementById('downloadResultBtn');

    // Modals & Navigation
    this.apiKeyBtn = document.getElementById('apiKeyBtn');
    this.apiModal = document.getElementById('apiModal');
    this.closeApiBtn = document.getElementById('closeApiBtn');
    this.saveApiKeysBtn = document.getElementById('saveApiKeysBtn');

    this.historyToggleBtn = document.getElementById('historyToggleBtn');
    this.historyModal = document.getElementById('historyModal');
    this.closeHistoryBtn = document.getElementById('closeHistoryBtn');
    this.historyList = document.getElementById('historyList');
  }

  initEventListeners() {
    // Input text char counter
    if (this.documentInput) {
      this.documentInput.addEventListener('input', () => {
        const len = this.documentInput.value.length;
        this.charCount.textContent = `${len.toLocaleString()} characters`;
        this.currentInputText = this.documentInput.value;
      });
    }

    if (this.clearInputBtn) {
      this.clearInputBtn.addEventListener('click', () => {
        this.documentInput.value = '';
        this.charCount.textContent = '0 characters';
        this.currentInputText = '';
      });
    }

    // Tabs logic
    this.tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        this.tabBtns.forEach(b => b.classList.remove('active'));
        this.tabContents.forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tab}Tab`).classList.add('active');
      });
    });

    // File Drag & Drop
    if (this.dropZone) {
      ['dragenter', 'dragover'].forEach(eventName => {
        this.dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          this.dropZone.classList.add('dragover');
        });
      });

      ['dragleave', 'drop'].forEach(eventName => {
        this.dropZone.addEventListener(eventName, (e) => {
          e.preventDefault();
          this.dropZone.classList.remove('dragover');
        });
      });

      this.dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) this.handleFileUpload(files[0]);
      });
    }

    if (this.fileInput) {
      this.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) this.handleFileUpload(e.target.files[0]);
      });
    }

    if (this.removeFileBtn) {
      this.removeFileBtn.addEventListener('click', () => {
        this.fileInfo.classList.add('hidden');
        this.dropZone.classList.remove('hidden');
        this.fileInput.value = '';
        this.documentInput.value = '';
        this.currentInputText = '';
        this.charCount.textContent = '0 characters';
      });
    }

    // Sample document chips
    document.querySelectorAll('.sample-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const sampleKey = chip.dataset.sample;
        const sampleText = SAMPLE_DOCUMENTS[sampleKey] || '';
        
        this.documentInput.value = sampleText;
        this.currentInputText = sampleText;
        this.charCount.textContent = `${sampleText.length.toLocaleString()} characters`;

        // Switch back to paste tab to show loaded text
        document.querySelector('[data-tab="paste"]').click();
        if (window.mascot) {
          window.mascot.setMood('happy', `Loaded '${chip.textContent.trim()}' into input! Select an action to run.`);
        }
      });
    });

    // Action Card Selector
    this.actionCards.forEach(card => {
      card.addEventListener('click', () => {
        const action = card.dataset.action;
        this.currentAction = action;

        this.actionCards.forEach(c => c.classList.remove('active'));
        card.classList.add('active');

        // Toggle sub options
        this.subGroups.forEach(g => g.classList.add('hidden'));
        const activeSubGroup = document.getElementById(`${action}Group`);
        if (activeSubGroup) activeSubGroup.classList.remove('hidden');
      });
    });

    // Run Primary Action Button
    if (this.runActionBtn) {
      this.runActionBtn.addEventListener('click', () => this.executeAction());
    }

    // Copy & Download
    if (this.copyResultBtn) {
      this.copyResultBtn.addEventListener('click', () => {
        const text = this.resultBody.innerText;
        navigator.clipboard.writeText(text);
        this.copyResultBtn.textContent = '✅ Copied!';
        setTimeout(() => { this.copyResultBtn.textContent = '📋 Copy Output'; }, 2000);
      });
    }

    if (this.downloadResultBtn) {
      this.downloadResultBtn.addEventListener('click', () => {
        const text = this.resultBody.innerText;
        const blob = new Blob([text], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `AURA_AI_${this.currentAction}_${Date.now()}.md`;
        a.click();
        URL.revokeObjectURL(url);
      });
    }

    // Modals
    if (this.apiKeyBtn) {
      this.apiKeyBtn.addEventListener('click', () => this.apiModal.classList.remove('hidden'));
    }
    if (this.closeApiBtn) {
      this.closeApiBtn.addEventListener('click', () => this.apiModal.classList.add('hidden'));
    }
    if (this.saveApiKeysBtn) {
      this.saveApiKeysBtn.addEventListener('click', () => {
        this.apiModal.classList.add('hidden');
        if (window.mascot) window.mascot.setMood('happy', "API configurations updated! Ready to process requests.");
      });
    }

    if (this.historyToggleBtn) {
      this.historyToggleBtn.addEventListener('click', () => {
        this.renderHistoryList();
        this.historyModal.classList.remove('hidden');
      });
    }
    if (this.closeHistoryBtn) {
      this.closeHistoryBtn.addEventListener('click', () => this.historyModal.classList.add('hidden'));
    }
  }

  generateBackgroundStars() {
    const container = document.getElementById('starsContainer');
    if (!container) return;

    for (let i = 0; i < 40; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      const size = Math.random() * 3 + 1;
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;
      star.style.left = `${Math.random() * 100}%`;
      star.style.top = `${Math.random() * 100}%`;
      star.style.setProperty('--duration', `${Math.random() * 3 + 2}s`);
      container.appendChild(star);
    }
  }

  async checkBackendHealth() {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        this.engineBadge.textContent = data.gemini_configured || data.anthropic_configured ? 'API Connected' : 'Smart Engine';
      }
    } catch (e) {
      // Backend not running directly — fallback to client-side smart agent engine seamlessly
      this.engineBadge.textContent = 'Smart Fallback Engine';
    }
  }

  async handleFileUpload(file) {
    if (!file) return;

    this.dropZone.classList.add('hidden');
    this.fileInfo.classList.remove('hidden');
    this.fileName.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

    if (window.mascot) {
      window.mascot.setMood('thinking', `Reading & parsing file '${file.name}'...`);
    }

    // Try backend upload endpoint or read directly in browser
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        this.currentInputText = data.extracted_text;
        this.documentInput.value = data.extracted_text;
        this.charCount.textContent = `${data.extracted_text.length.toLocaleString()} characters`;
        if (window.mascot) window.mascot.setMood('happy', `Successfully extracted ${data.character_count} characters from ${file.name}!`);
        return;
      }
    } catch (err) {
      console.log("Backend upload unavailable, using client-side reader...");
    }

    // Client-side text file reader fallback
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      this.currentInputText = text;
      this.documentInput.value = text;
      this.charCount.textContent = `${text.length.toLocaleString()} characters`;
      if (window.mascot) window.mascot.setMood('happy', `Loaded ${text.length} characters from ${file.name}!`);
    };
    reader.readAsText(file);
  }

  async executeAction() {
    const text = this.documentInput.value.trim() || this.currentInputText.trim();
    if (!text) {
      if (window.mascot) window.mascot.setMood('sad', "Please paste a document or upload a file first!");
      return;
    }

    // Set Mascot state to thinking & disable button
    if (window.mascot) window.mascot.setMood('thinking', `Running AI ${this.currentAction.toUpperCase()} workflow...`);
    this.setButtonLoading(true);

    let payload = { text };
    let endpoint = `${API_BASE_URL}/${this.currentAction}`;

    if (this.currentAction === 'summarize') {
      payload.length = this.summaryLengthSelect.value;
    } else if (this.currentAction === 'qa') {
      const question = this.questionInput.value.trim();
      if (!question) {
        if (window.mascot) window.mascot.setMood('sad', "Please enter a question to ask!");
        this.setButtonLoading(false);
        return;
      }
      payload.question = question;
    } else if (this.currentAction === 'generate') {
      payload.instruction = this.instructionInput.value.trim() || "Write a professional follow-up email based on this content.";
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        this.renderResult(data.result, data.mode, data.suggested_actions);
        if (window.mascot) window.mascot.setMood('happy', `Completed! Generated response using ${data.mode === 'api' ? 'Live LLM API' : 'Smart Agent Engine'}.`);
        this.recordHistory(this.currentAction, data.result);
        this.setButtonLoading(false);
        return;
      }
    } catch (err) {
      console.log("Backend request failed, executing client-side AI engine fallback...");
    }

    // Client-side AI Fallback Execution
    setTimeout(() => {
      const fallbackResult = this.clientSideAIFallback(this.currentAction, text, payload);
      this.renderResult(fallbackResult.result, 'smart_engine', fallbackResult.suggested_actions);
      if (window.mascot) window.mascot.setMood('happy', "Done! Output processed using Smart Fallback Engine ✨");
      this.recordHistory(this.currentAction, fallbackResult.result);
      this.setButtonLoading(false);
    }, 600);
  }

  clientSideAIFallback(action, text, payload) {
    const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 8);
    let resultText = "";

    if (action === 'summarize') {
      const length = payload.length || 'medium';
      if (length === 'short') {
        resultText = `**Executive Summary:**\n${sentences.slice(0, 2).join(' ')}`;
      } else if (length === 'detailed') {
        const bullets = sentences.slice(0, 5).map(s => `• ${s.trim()}`).join('\n');
        resultText = `### Comprehensive Document Breakdown\n\n**Overview:**\n${sentences[0] || text.substring(0, 150)}\n\n**Key Takeaways:**\n${bullets}`;
      } else {
        const bullets = sentences.slice(0, 4).map(s => `• ${s.trim()}`).join('\n');
        resultText = `**Key Summary Points:**\n${bullets}`;
      }
    } else if (action === 'qa') {
      const q = (payload.question || "").toLowerCase();
      const matched = sentences.filter(s => q.split(' ').some(word => word.length > 3 && s.toLowerCase().includes(word)));
      if (matched.length > 0) {
        resultText = `**Grounded Answer:**\n${matched.slice(0, 3).join(' ')}`;
      } else {
        resultText = `**Grounded Answer:**\nBased strictly on the provided text context, ${sentences[0] || text.substring(0, 200)}.`;
      }
    } else if (action === 'generate') {
      const instr = payload.instruction || "Write a follow-up email";
      resultText = `**Subject:** Follow-up: ${instr}\n\nHi Team,\n\nFollowing up on our document review:\n\n> ${sentences.slice(0, 2).join(' ')}\n\nPlease review the attached items and let me know if you have any questions.\n\nBest regards,\nAURA AI Assistant`;
    } else if (action === 'analyze') {
      const bullets = sentences.slice(0, 3).map(s => `- ${s.trim()}`).join('\n');
      resultText = `### 📊 Document Intelligence Report\n\n**Tone & Sentiment:** Professional & Informative 🟢\n\n**📌 Key Findings:**\n${bullets}\n\n**⚡ Recommended Actions:**\n- Review timelines and confirm stakeholder alignment.\n- Prepare execution breakdown for upcoming milestones.`;
    }

    const suggestions = [
      { label: "📧 Draft Follow-up Email", action: "generate", prompt: "Write an email based on this output" },
      { label: "⚡ Extract Action Items", action: "analyze", prompt: "" },
      { label: "❓ Ask Question", action: "qa", prompt: "What are the main risks?" }
    ];

    return { result: resultText, suggested_actions: suggestions };
  }

  renderResult(markdownText, mode, suggestedActions = []) {
    // Basic Markdown Formatting
    let html = markdownText
      .replace(/### (.*?)\n/g, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/• (.*?)\n/g, '<li>$1</li>')
      .replace(/- (.*?)\n/g, '<li>$1</li>')
      .replace(/\n\n/g, '<br><br>');

    this.resultBody.innerHTML = html;
    this.resultFooter.classList.remove('hidden');

    // Render Suggested Next Actions Chips
    if (suggestedActions && suggestedActions.length > 0) {
      this.suggestedSection.classList.remove('hidden');
      this.suggestedChips.innerHTML = '';
      
      suggestedActions.forEach(item => {
        const chip = document.createElement('button');
        chip.className = 'suggest-chip';
        chip.textContent = item.label;
        chip.addEventListener('click', () => {
          // Auto switch action and run
          const actionBtn = document.querySelector(`[data-action="${item.action}"]`);
          if (actionBtn) actionBtn.click();

          if (item.action === 'qa' && item.prompt) {
            this.questionInput.value = item.prompt;
          } else if (item.action === 'generate' && item.prompt) {
            this.instructionInput.value = item.prompt;
          }

          this.executeAction();
        });
        this.suggestedChips.appendChild(chip);
      });
    }
  }

  setButtonLoading(isLoading) {
    if (isLoading) {
      this.runActionBtn.disabled = true;
      this.btnSpinner.classList.remove('hidden');
      document.querySelector('.btn-text').textContent = 'Processing...';
    } else {
      this.runActionBtn.disabled = false;
      this.btnSpinner.classList.add('hidden');
      document.querySelector('.btn-text').textContent = 'Run AI Agent';
    }
  }

  recordHistory(action, output) {
    this.history.unshift({
      time: new Date().toLocaleTimeString(),
      action: action.toUpperCase(),
      preview: output.substring(0, 100) + '...'
    });
  }

  renderHistoryList() {
    if (this.history.length === 0) {
      this.historyList.innerHTML = '<p class="empty-history">No prior runs recorded in this session.</p>';
      return;
    }

    this.historyList.innerHTML = this.history.map(item => `
      <div class="history-item glass-card margin-top">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--accent-cyan);">
          <span><strong>${item.action}</strong></span>
          <span>${item.time}</span>
        </div>
        <p style="font-size:0.85rem; margin-top:4px;">${item.preview}</p>
      </div>
    `).join('');
  }
}

// Instantiate App Controller on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new AppController();
});
