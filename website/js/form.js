/**
 * Masii Web Form Engine — The 36 Gunas
 * Progressive disclosure: one question at a time, mimicking the Telegram bot's conversational feel.
 * Depends on form-config.js being loaded first.
 */

(function () {
  "use strict";

  // ============== API CONFIG ==============
  const API_BASE = window.location.hostname === "localhost"
    ? "http://localhost:8080"
    : "https://masii-bot.fly.dev";

  // ============== STATE ==============
  const state = {
    phase: "intro",        // intro | intent | proxy | gunas | sub_question | close | phone | done | error
    introIndex: 0,
    proxyIndex: 0,
    currentGuna: 0,
    currentSubStep: null,  // for multi-step questions (step1, step2, step3, etc.)
    pendingSubQuestion: null,
    previousSection: null,
    showingTransition: false,
    answers: {},
    meta: {                // non-guna answers (intent, proxy info)
      intent: null,
      proxy_relation: null,
      proxy_consent: null
    }
  };

  // ============== DOM ==============
  const container = document.getElementById("form-container");
  const progressBar = document.getElementById("progress-fill");
  const progressText = document.getElementById("progress-text");

  // ============== RENDER HELPERS ==============

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => {
      if (k === "className") node.className = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2).toLowerCase(), v);
      else node.setAttribute(k, v);
    });
    children.forEach(c => {
      if (typeof c === "string") node.appendChild(document.createTextNode(c));
      else if (c) node.appendChild(c);
    });
    return node;
  }

  function clear() {
    container.innerHTML = "";
  }

  function updateProgress() {
    if (state.phase === "intro" || state.phase === "intent" || state.phase === "proxy") {
      progressBar.style.width = "0%";
      progressText.textContent = "";
      return;
    }
    if (state.phase === "done" || state.phase === "close") {
      progressBar.style.width = "100%";
      progressText.textContent = "36 of 36";
      return;
    }
    // Count only actually-answered gunas (not pre-emptively skipped ones)
    let answered = 0;
    for (let i = 1; i <= TOTAL_GUNAS; i++) {
      const q = QUESTIONS[i];
      if (!q) continue;
      // Only count as done if we've actually passed this question
      if (i < state.currentGuna) {
        answered++;
      }
    }
    const pct = Math.round((answered / TOTAL_GUNAS) * 100);
    progressBar.style.width = pct + "%";
    progressText.textContent = `${answered} of ${TOTAL_GUNAS}`;
  }

  function renderCard(content, fadeIn = true) {
    clear();
    const card = el("div", { className: "form-card" + (fadeIn ? " fade-in" : "") });
    if (typeof content === "string") {
      card.innerHTML = content;
    } else {
      card.appendChild(content);
    }
    container.appendChild(card);
    updateProgress();
    // Scroll to top of card
    card.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderMessage(text, buttonLabel, onClick) {
    const frag = document.createDocumentFragment();
    const msg = el("div", { className: "form-message" });
    msg.innerHTML = text.replace(/\n/g, "<br>");
    frag.appendChild(msg);
    const btn = el("button", { className: "form-btn form-btn-primary", onClick }, buttonLabel);
    frag.appendChild(btn);
    renderCard(frag);
  }

  function renderOptions(questionText, options, onSelect, columns) {
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    const grid = el("div", { className: "form-options" + (columns ? ` cols-${columns}` : "") });
    options.forEach(opt => {
      const btn = el("button", {
        className: "form-btn form-btn-option",
        onClick: () => {
          if (opt.requires_text) {
            renderTextFollowUp(questionText, opt, onSelect);
          } else {
            onSelect(opt.value);
          }
        }
      }, opt.label);
      grid.appendChild(btn);
    });
    frag.appendChild(grid);
    renderCard(frag);
  }

  function renderTextInput(questionText, placeholder, onSubmit) {
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    const input = el("textarea", {
      className: "form-input",
      placeholder: placeholder || "",
      rows: "3"
    });
    frag.appendChild(input);
    const btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: () => {
        const val = input.value.trim();
        if (!val) {
          input.classList.add("shake");
          setTimeout(() => input.classList.remove("shake"), 500);
          return;
        }
        onSubmit(val);
      }
    }, "Continue →");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(() => input.focus(), 100);
  }

  function renderTextFollowUp(questionText, opt, onSelect) {
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    const note = el("p", { className: "form-note" }, `Selected: ${opt.label}`);
    frag.appendChild(note);
    const input = el("input", {
      className: "form-input form-input-single",
      type: "text",
      placeholder: "Please specify..."
    });
    frag.appendChild(input);
    const btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: () => {
        const val = input.value.trim();
        if (!val) {
          input.classList.add("shake");
          setTimeout(() => input.classList.remove("shake"), 500);
          return;
        }
        onSelect(val);
      }
    }, "Continue →");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(() => input.focus(), 100);
  }


  // ============== PHASE: INTRO ==============

  function showIntro() {
    state.phase = "intro";
    const msg = INTRO_MESSAGES[state.introIndex];
    renderMessage(msg.text, msg.button, () => {
      state.introIndex++;
      if (state.introIndex < INTRO_MESSAGES.length) {
        showIntro();
      } else {
        showIntent();
      }
    });
  }

  // ============== PHASE: INTENT ==============

  function showIntent() {
    state.phase = "intent";
    renderOptions(INTENT_MESSAGE.text, INTENT_MESSAGE.options, (val) => {
      state.meta.intent = val;
      if (val === "proxy") {
        state.proxyIndex = 0;
        showProxy();
      } else {
        startGunas();
      }
    });
  }

  // ============== PHASE: PROXY ==============

  function showProxy() {
    state.phase = "proxy";
    const msg = PROXY_MESSAGES[state.proxyIndex];
    renderOptions(msg.text, msg.options, (val) => {
      if (state.proxyIndex === 0) {
        state.meta.proxy_relation = val;
      } else {
        state.meta.proxy_consent = val;
      }
      state.proxyIndex++;
      if (state.proxyIndex < PROXY_MESSAGES.length) {
        showProxy();
      } else {
        // If consent is "not_yet", show the notice
        if (state.meta.proxy_consent === "not_yet") {
          renderMessage(PROXY_NO_CONSENT_MESSAGE, "Continue →", () => startGunas());
        } else {
          startGunas();
        }
      }
    });
  }

  // ============== PHASE: GUNAS ==============

  function startGunas() {
    state.phase = "gunas";
    state.currentGuna = 1;
    state.previousSection = null;
    // Show first section transition
    showGuna(1);
  }

  function showGuna(num) {
    // Past the end?
    if (num > TOTAL_GUNAS) {
      showClose();
      return;
    }

    // Skip logic
    if (shouldSkipQuestion(num, state.answers)) {
      const next = getNextQuestion(state.answers, num);
      state.currentGuna = next;
      showGuna(next);
      return;
    }

    state.currentGuna = num;
    state.phase = "gunas";

    // Check section transition
    const section = getSectionForQuestion(num);
    const transitionKey = getTransitionKey(section, state.previousSection);
    if (transitionKey && SECTION_TRANSITIONS[transitionKey]) {
      state.showingTransition = true;
      const text = SECTION_TRANSITIONS[transitionKey].replace("{name}", state.answers.first_name || "");
      renderMessage(text, "Continue →", () => {
        state.showingTransition = false;
        state.previousSection = section;
        renderGunaQuestion(num);
      });
      return;
    }
    state.previousSection = section;
    renderGunaQuestion(num);
  }

  function renderGunaQuestion(num) {
    const q = QUESTIONS[num];
    if (!q) return;

    // Multi-step types
    if (q.type === "two_step_date") {
      renderDateQuestion(num, q);
      return;
    }
    if (q.type === "location_tree") {
      renderLocationQuestion(num, q);
      return;
    }

    // Text input
    if (q.type === "text_input") {
      renderTextInput(q.text, q.placeholder, (val) => {
        saveAnswer(q.field, val);
        advanceFromGuna(num);
      });
      return;
    }

    // Single select — resolve options
    let options = q.options;
    if (typeof options === "string") {
      options = getConditionalOptions(num, state.answers);
      if (!options) {
        // Shouldn't happen if skip logic is correct, but be safe
        advanceFromGuna(num);
        return;
      }
    }

    renderOptions(q.text, options, (val) => {
      saveAnswer(q.field, val);
      advanceFromGuna(num);
    }, q.columns);
  }


  // ============== MULTI-STEP: DATE (Guna 7) ==============

  function renderDateQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      let options = q.step1.options;
      if (options === "birth_years") options = getBirthYears();
      renderOptions(q.step1.text, options, (val) => {
        state.answers._birth_year = val;
        state.currentSubStep = "step2";
        renderDateQuestion(num, q);
      }, q.step1.columns);
    } else if (state.currentSubStep === "step2") {
      renderOptions(q.step2.text, q.step2.options, (val) => {
        state.answers._birth_month = val;
        // Compose date_of_birth as "YYYY-MM-15" (day=15 as placeholder)
        const dob = `${state.answers._birth_year}-${val.padStart(2, "0")}-15`;
        saveAnswer(q.field, dob);
        state.currentSubStep = null;
        advanceFromGuna(num);
      }, q.step2.columns);
    }
  }


  // ============== MULTI-STEP: LOCATION (Guna 8) ==============

  function renderLocationQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      renderOptions(q.step1.text, q.step1.options, (val) => {
        state.answers._location_type = val;
        state.currentSubStep = "step2";
        renderLocationQuestion(num, q);
      });
    } else if (state.currentSubStep === "step2") {
      const isIndia = state.answers._location_type === "India";
      const step = isIndia ? q.step2_india : q.step2_abroad;
      let options = step.options;
      if (options === "states_india") options = getStatesIndia();
      if (options === "countries") options = getCountries();
      renderOptions(step.text, options, (val) => {
        saveAnswer(step.field, val);
        if (isIndia) {
          saveAnswer("country_current", "India");
        }
        state.currentSubStep = "step3";
        renderLocationQuestion(num, q);
      }, step.columns);
    } else if (state.currentSubStep === "step3") {
      renderTextInput(q.step3.text, q.step3.placeholder, (val) => {
        saveAnswer(q.step3.field, val);
        state.currentSubStep = null;
        advanceFromGuna(num);
      });
    }
  }


  // ============== ADVANCE LOGIC ==============

  function advanceFromGuna(currentNum) {
    // Check for sub-questions after this guna
    for (const [key, subQ] of Object.entries(SUB_QUESTIONS)) {
      if (subQ.after_guna === currentNum && shouldAskSubQuestion(key, state.answers)) {
        state.pendingSubQuestion = key;
        showSubQuestion(key);
        return;
      }
    }

    const next = getNextQuestion(state.answers, currentNum);
    state.currentGuna = next;
    showGuna(next);
  }

  function showSubQuestion(key) {
    state.phase = "sub_question";
    const subQ = SUB_QUESTIONS[key];
    renderOptions(subQ.text, subQ.options, (val) => {
      saveAnswer(subQ.field, val);
      state.pendingSubQuestion = null;
      // Continue to next guna after the sub-question's parent
      const next = getNextQuestion(state.answers, subQ.after_guna);
      state.currentGuna = next;
      state.phase = "gunas";
      showGuna(next);
    });
  }


  // ============== SAVE ANSWER ==============

  function saveAnswer(field, value) {
    state.answers[field] = value;
  }


  // ============== PHASE: CLOSE ==============

  function showClose() {
    state.phase = "close";
    const text = CLOSE_MESSAGE.replace(/{name}/g, state.answers.first_name || "");
    renderMessage(text, "Almost done — one last thing →", () => {
      showPhone();
    });
  }


  // ============== PHASE: PHONE ==============

  function showPhone() {
    state.phase = "phone";
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, "Your phone number");
    frag.appendChild(q);
    const note = el("p", { className: "form-note" }, "We'll use this to send you your match. No spam, ever.");
    frag.appendChild(note);

    const row = el("div", { className: "phone-row" });
    const countrySelect = el("select", { className: "form-select phone-code" });
    const codes = [
      { label: "+91 India", value: "+91" },
      { label: "+1 USA/CAN", value: "+1" },
      { label: "+44 UK", value: "+44" },
      { label: "+61 AUS", value: "+61" },
      { label: "+971 UAE", value: "+971" },
      { label: "+65 SG", value: "+65" },
      { label: "+49 DE", value: "+49" },
      { label: "+64 NZ", value: "+64" },
      { label: "+966 SA", value: "+966" },
      { label: "+974 QA", value: "+974" }
    ];
    codes.forEach(c => {
      const opt = el("option", { value: c.value }, c.label);
      countrySelect.appendChild(opt);
    });
    row.appendChild(countrySelect);

    const phoneInput = el("input", {
      className: "form-input form-input-single phone-number",
      type: "tel",
      placeholder: "Phone number"
    });
    row.appendChild(phoneInput);
    frag.appendChild(row);

    const btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: () => {
        const code = countrySelect.value;
        const phone = phoneInput.value.trim().replace(/\D/g, "");
        if (!phone || phone.length < 7) {
          phoneInput.classList.add("shake");
          setTimeout(() => phoneInput.classList.remove("shake"), 500);
          return;
        }
        const fullPhone = code + phone;
        submitForm(fullPhone);
      }
    }, "Submit →");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(() => phoneInput.focus(), 100);
  }


  // ============== SUBMIT ==============

  async function submitForm(phone) {
    state.phase = "done";
    // Show loading
    renderMessage("Submitting your answers...", "", () => {});
    // Remove the empty button
    const btn = container.querySelector(".form-btn");
    if (btn) btn.style.display = "none";

    // Build payload
    const payload = {
      phone: phone,
      name: state.answers.first_name || "",
      answers: {},
      meta: state.meta
    };

    // Collect all guna answers with their db_table info
    for (let i = 1; i <= TOTAL_GUNAS; i++) {
      const q = QUESTIONS[i];
      if (!q) continue;

      if (q.type === "location_tree") {
        // Location has multiple fields
        ["country_current", "state_india", "city_current"].forEach(f => {
          if (state.answers[f] != null) {
            payload.answers[f] = { value: state.answers[f], table: "users" };
          }
        });
        continue;
      }
      if (q.type === "two_step_date") {
        if (state.answers[q.field] != null) {
          payload.answers[q.field] = { value: state.answers[q.field], table: q.db_table };
        }
        continue;
      }
      if (state.answers[q.field] != null) {
        payload.answers[q.field] = { value: state.answers[q.field], table: q.db_table };
      }
    }

    // Sub-question answers
    for (const [key, subQ] of Object.entries(SUB_QUESTIONS)) {
      if (state.answers[subQ.field] != null) {
        payload.answers[subQ.field] = { value: state.answers[subQ.field], table: subQ.db_table };
      }
    }

    try {
      const resp = await fetch(API_BASE + "/api/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      showSuccess(data);
    } catch (err) {
      console.error("Submit error:", err);
      showError(phone);
    }
  }

  function showSuccess() {
    const name = state.answers.first_name || "";
    const frag = document.createDocumentFragment();
    const check = el("div", { className: "success-check" }, "✓");
    frag.appendChild(check);
    const h = el("h2", { className: "form-question" }, `You're in, ${name}.`);
    frag.appendChild(h);
    const p = el("p", { className: "form-note" },
      "Masii is on it. When she finds someone worth your time, she'll reach out."
    );
    frag.appendChild(p);
    const link = el("a", { href: "index.html", className: "form-btn form-btn-primary" }, "Back to Masii");
    frag.appendChild(link);
    renderCard(frag);
  }

  function showError(phone) {
    state.phase = "error";
    const frag = document.createDocumentFragment();
    const h = el("h2", { className: "form-question" }, "Something went wrong.");
    frag.appendChild(h);
    const p = el("p", { className: "form-note" },
      "Your answers are saved locally. Try again or reach out on Telegram."
    );
    frag.appendChild(p);
    const btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: () => submitForm(phone)
    }, "Try again →");
    frag.appendChild(btn);
    const tg = el("a", {
      href: "https://t.me/masii_bot",
      className: "form-btn form-btn-secondary",
      target: "_blank"
    }, "Open Telegram →");
    frag.appendChild(tg);
    renderCard(frag);
  }


  // ============== INIT ==============

  function init() {
    showIntro();
  }

  // Start
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
