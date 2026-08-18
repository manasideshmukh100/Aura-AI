/**
 * mascot.js — Cute Animated SVG Smiley Mascot Engine
 * Manages mascot mood states (idle, thinking, happy, sad) and speech bubble reactions.
 */

class MascotEngine {
  constructor() {
    this.eyesElem = document.getElementById('mascotEyes');
    this.mouthElem = document.getElementById('mascotMouth');
    this.messageElem = document.getElementById('mascotMessage');
    this.mascotSvg = document.getElementById('smileyMascot');
    this.mascotWrapper = document.getElementById('mascotWrapper');
    
    this.currentMood = 'idle';
    this.initEvents();
  }

  initEvents() {
    if (!this.mascotWrapper) return;

    // Interactive click reaction: wink & bounce
    this.mascotWrapper.addEventListener('click', () => {
      this.triggerWink();
    });
  }

  setMood(mood, customMessage = '') {
    this.currentMood = mood;

    switch (mood) {
      case 'thinking':
        this.renderThinkingState(customMessage || "Thinking... Analyzing your document and running AI logic 🧠");
        break;
      case 'happy':
      case 'success':
        this.renderHappyState(customMessage || "All done! Here is your output and suggested next steps ✨");
        break;
      case 'sad':
      case 'error':
        this.renderSadState(customMessage || "Oops! An error occurred. Please check your document and try again.");
        break;
      case 'idle':
      default:
        this.renderIdleState(customMessage || "Hi there! What document or task would you like me to process today? ✨");
        break;
    }
  }

  renderIdleState(message) {
    if (this.eyesElem) {
      this.eyesElem.innerHTML = `
        <ellipse class="eye left" cx="42" cy="52" rx="4.5" ry="6" fill="#ffffff" />
        <ellipse class="eye right" cx="78" cy="52" rx="4.5" ry="6" fill="#ffffff" />
      `;
    }
    if (this.mouthElem) {
      this.mouthElem.setAttribute('d', 'M 44 68 Q 60 80 76 68');
      this.mouthElem.setAttribute('stroke', '#ffffff');
    }
    if (this.messageElem) this.messageElem.textContent = message;
  }

  renderThinkingState(message) {
    if (this.eyesElem) {
      // Curious eyes looking slightly upwards
      this.eyesElem.innerHTML = `
        <ellipse class="eye left" cx="44" cy="48" rx="4.5" ry="5.5" fill="#ffffff" />
        <ellipse class="eye right" cx="76" cy="48" rx="4.5" ry="5.5" fill="#ffffff" />
        <circle cx="44" cy="46" r="2" fill="#6d28d9" />
        <circle cx="76" cy="46" r="2" fill="#6d28d9" />
      `;
    }
    if (this.mouthElem) {
      // Thinking '...' squiggle mouth
      this.mouthElem.setAttribute('d', 'M 48 70 Q 60 65 72 70');
      this.mouthElem.setAttribute('stroke', '#ffffff');
    }
    if (this.messageElem) this.messageElem.textContent = message;
  }

  renderHappyState(message) {
    if (this.eyesElem) {
      // Happy ^_^ curve eyes
      this.eyesElem.innerHTML = `
        <path d="M 36 54 Q 42 44 48 54" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
        <path d="M 72 54 Q 78 44 84 54" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
      `;
    }
    if (this.mouthElem) {
      // Big happy smile
      this.mouthElem.setAttribute('d', 'M 40 66 Q 60 84 80 66');
      this.mouthElem.setAttribute('stroke', '#ffffff');
    }
    if (this.messageElem) this.messageElem.textContent = message;

    // Small bounce animation
    if (this.mascotSvg) {
      this.mascotSvg.style.transform = 'scale(1.15) rotate(-3deg)';
      setTimeout(() => {
        this.mascotSvg.style.transform = '';
      }, 400);
    }
  }

  renderSadState(message) {
    if (this.eyesElem) {
      // Concerned downturned eyes
      this.eyesElem.innerHTML = `
        <ellipse class="eye left" cx="42" cy="54" rx="4" ry="4" fill="#ffffff" />
        <ellipse class="eye right" cx="78" cy="54" rx="4" ry="4" fill="#ffffff" />
      `;
    }
    if (this.mouthElem) {
      // Slight frown line
      this.mouthElem.setAttribute('d', 'M 46 72 Q 60 65 74 72');
      this.mouthElem.setAttribute('stroke', '#f472b6');
    }
    if (this.messageElem) this.messageElem.textContent = message;
  }

  triggerWink() {
    if (this.currentMood !== 'idle') return;

    if (this.eyesElem) {
      this.eyesElem.innerHTML = `
        <path d="M 36 52 Q 42 46 48 52" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" />
        <ellipse class="eye right" cx="78" cy="52" rx="4.5" ry="6" fill="#ffffff" />
      `;
      if (this.messageElem) this.messageElem.textContent = "Teehee! Ready to automate your workflow! 😉";

      setTimeout(() => {
        this.renderIdleState("Hi there! What document or task would you like me to process today? ✨");
      }, 1500);
    }
  }
}

// Global mascot instance
window.mascot = new MascotEngine();
