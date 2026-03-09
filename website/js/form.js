/**
 * Masii Web Form Engine — V3
 * Driven by form-config.generated.js (YAML source of truth).
 * Flow-based navigation using getQuestionFlow().
 */

(function () {
  "use strict";

  // ============== API CONFIG ==============
  const API_BASE = window.location.hostname === "localhost"
    ? "http://localhost:8080"
    : "https://masii-bot.fly.dev";

  // ============== STATE ==============
  const state = {
    phase: "email",      // email | otp | resume | intro | questions | review | close | phone | done | error | proxy
    flow: [],            // ordered array of question IDs from getQuestionFlow()
    flowIndex: 0,        // current position in flow[]
    currentSubStep: null, // for multi-step questions (step1, step2, step3)
    previousSection: null,
    editingFromReview: false,
    editingField: null,
    proxyIndex: 0,
    answers: {},
    meta: {
      intent: null,
      email: null,
      proxy: {}
    }
  };

  // ============== DOM ==============
  const container = document.getElementById("form-container");
  const pillsContainer = document.getElementById("progress-pills");
  const sectionName = document.getElementById("section-name");
  const sectionCount = document.getElementById("section-count");
  const backBtn = document.getElementById("back-btn");

  // ============== CONFIG PATCHES ==============
  // Patch pref_age_range: change to same-screen layout (two dropdowns side by side)
  (function () {
    var q = QUESTIONS[QUESTION_INDEX["pref_age_range"]];
    if (q) {
      q.type = "two_step_same_screen";
      q.hasDoesntMatter = false;
    }
  })();

  // Patch pref_family_status: add "Same or lower" option
  (function () {
    var q = QUESTIONS[QUESTION_INDEX["pref_family_status"]];
    if (q && q.options) {
      // Insert after "Same or higher"
      var idx = q.options.findIndex(function (o) { return o.value === "Same or higher"; });
      if (idx >= 0) {
        q.options.splice(idx + 1, 0, { label: "Same or lower", value: "Same or lower" });
      }
    }
  })();

  // ============== RENDER HELPERS ==============

  function el(tag, attrs) {
    var children = Array.prototype.slice.call(arguments, 2);
    var node = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(function (entry) {
      var k = entry[0], v = entry[1];
      if (k === "className") node.className = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2).toLowerCase(), v);
      else node.setAttribute(k, v);
    });
    children.forEach(function (c) {
      if (typeof c === "string") node.appendChild(document.createTextNode(c));
      else if (c) node.appendChild(c);
    });
    return node;
  }

  function clear() {
    container.innerHTML = "";
  }

  function renderCard(content, fadeIn) {
    if (fadeIn === undefined) fadeIn = true;
    clear();
    var card = el("div", { className: "form-card" + (fadeIn ? " fade-in" : "") });
    if (typeof content === "string") {
      card.innerHTML = content;
    } else {
      card.appendChild(content);
    }
    container.appendChild(card);
    updateProgressUI();
    card.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderMessage(text, buttonLabel, onClick) {
    var frag = document.createDocumentFragment();
    var msg = el("div", { className: "form-message" });
    msg.innerHTML = text.replace(/\n/g, "<br>");
    frag.appendChild(msg);
    if (buttonLabel) {
      var btn = el("button", { className: "form-btn form-btn-primary", onClick: onClick }, buttonLabel);
      frag.appendChild(btn);
    }
    renderCard(frag);
  }

  function renderPhoneInput(questionText, placeholder, onSubmit) {
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    var row = el("div", { className: "phone-row" });
    var countrySelect = el("select", { className: "form-select phone-code" });
    var codes = [
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
    codes.forEach(function (c) {
      var opt = el("option", { value: c.value }, c.label);
      countrySelect.appendChild(opt);
    });
    row.appendChild(countrySelect);
    var phoneInput = el("input", {
      className: "form-input form-input-single phone-number",
      type: "tel",
      placeholder: placeholder || "Phone number"
    });
    row.appendChild(phoneInput);
    frag.appendChild(row);
    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () {
        var code = countrySelect.value;
        var phone = phoneInput.value.trim().replace(/\D/g, "");
        if (!phone || phone.length < 7) {
          phoneInput.classList.add("shake");
          setTimeout(function () { phoneInput.classList.remove("shake"); }, 500);
          return;
        }
        onSubmit(code + phone);
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { phoneInput.focus(); }, 100);
  }


  // ============== AUTH HELPERS ==============

  var currentUserId = null;

  function getStorageKey() {
    return currentUserId ? "masii_form_" + currentUserId : null;
  }

  function persistState() {
    var key = getStorageKey();
    if (!key) return;
    try {
      localStorage.setItem(key, JSON.stringify({
        phase: state.phase,
        flow: state.flow,
        flowIndex: state.flowIndex,
        currentSubStep: state.currentSubStep,
        previousSection: state.previousSection,
        answers: state.answers,
        meta: state.meta
      }));
    } catch (e) {
      console.error("Failed to persist state:", e);
    }
  }

  function restoreState(saved) {
    state.answers = saved.answers || {};
    state.meta = saved.meta || { intent: null, email: null, proxy: {} };
    state.previousSection = saved.previousSection || null;
    state.currentSubStep = saved.currentSubStep || null;

    // Recompute flow from current answers (source of truth)
    recomputeFlow();

    if (saved.phase === "questions" && saved.flowIndex != null) {
      // Try to restore position: find the question at the saved flowIndex
      var savedFlow = saved.flow || [];
      var savedQId = savedFlow[saved.flowIndex];
      if (savedQId) {
        var idx = state.flow.indexOf(savedQId);
        state.flowIndex = idx >= 0 ? idx : Math.min(saved.flowIndex, state.flow.length - 1);
      } else {
        state.flowIndex = Math.min(saved.flowIndex || 0, state.flow.length - 1);
      }
      state.phase = "questions";
      showQuestion();
    } else if (saved.phase === "review") {
      showReview();
    } else if (saved.phase === "close") {
      showClose();
    } else if (saved.phase === "phone") {
      showPhone();
    } else {
      // Default: start from intro
      showIntro();
    }
  }

  function calculateProgress() {
    if (!state.answers || Object.keys(state.answers).length === 0) return 0;
    var flow = state.flow.length > 0 ? state.flow : getQuestionFlow(state.answers);
    var answered = 0;
    for (var i = 0; i < flow.length; i++) {
      var q = QUESTIONS[QUESTION_INDEX[flow[i]]];
      if (q && state.answers[q.field] != null) answered++;
    }
    return flow.length > 0 ? Math.round((answered / flow.length) * 100) : 0;
  }


  // ============== FLOW NAVIGATION ==============

  function recomputeFlow() {
    var currentQId = state.flow[state.flowIndex];
    state.flow = getQuestionFlow(state.answers);

    // Exclude setup questions (intent, full_name, preferred_name, gender) from main flow
    // They are handled as part of the intro → questions transition
    // Actually keep them in flow - they ARE part of the flow in V3

    if (currentQId) {
      var newIdx = state.flow.indexOf(currentQId);
      if (newIdx >= 0) {
        state.flowIndex = newIdx;
      }
      // If current question got skipped, flowIndex stays and showQuestion will handle it
    }
  }

  function getCurrentQuestion() {
    if (state.flowIndex >= state.flow.length) return null;
    var qId = state.flow[state.flowIndex];
    return QUESTIONS[QUESTION_INDEX[qId]] || null;
  }

  function advanceToNext() {
    if (state.editingFromReview) {
      state.editingFromReview = false;
      state.editingField = null;
      persistState();
      showReview();
      return;
    }
    // Capture the question we just answered BEFORE recomputing
    var justAnsweredId = state.flow[state.flowIndex];
    state.currentSubStep = null;

    // Recompute flow (answer may have unlocked/removed downstream questions)
    state.flow = getQuestionFlow(state.answers);

    // Find the just-answered question in the new flow and go to the one after it
    if (justAnsweredId) {
      var answeredIdx = state.flow.indexOf(justAnsweredId);
      if (answeredIdx >= 0) {
        state.flowIndex = answeredIdx + 1;
      } else {
        state.flowIndex++;
      }
    } else {
      state.flowIndex++;
    }

    persistState();
    showQuestion();
  }

  function goBack() {
    if (state.flowIndex <= 0) return;
    state.flowIndex--;
    state.currentSubStep = null;
    showQuestion(true); // skipTransition = true
  }


  // ============== PROGRESS UI ==============

  function updateProgressUI() {
    if (!pillsContainer) return;

    // Only show progress during questions phase
    var showProgress = (state.phase === "questions" || state.phase === "review");
    pillsContainer.style.display = showProgress ? "flex" : "none";
    if (sectionName) sectionName.style.display = showProgress ? "inline" : "none";
    if (sectionCount) sectionCount.style.display = showProgress ? "inline" : "none";

    if (!showProgress) {
      if (backBtn) backBtn.style.display = "none";
      return;
    }

    var currentQ = getCurrentQuestion();
    if (!currentQ) {
      // Review phase — all completed
      renderPills("personality"); // last section
      if (sectionName) sectionName.textContent = "Review";
      if (sectionCount) sectionCount.textContent = "";
      if (backBtn) backBtn.style.display = "none";
      return;
    }

    var currentSection = currentQ.section;
    renderPills(currentSection);

    // Section counter
    var sectionLabel = SECTIONS[currentSection] ? SECTIONS[currentSection].label : currentSection;
    var sectionQs = state.flow.filter(function (qId) {
      var q = QUESTIONS[QUESTION_INDEX[qId]];
      return q && q.section === currentSection;
    });
    var posInSection = sectionQs.indexOf(state.flow[state.flowIndex]) + 1;
    if (sectionName) sectionName.textContent = sectionLabel;
    if (sectionCount) sectionCount.textContent = posInSection + " of " + sectionQs.length;

    // Back button
    if (backBtn) {
      backBtn.style.display = state.flowIndex > 0 ? "inline" : "none";
      backBtn.onclick = goBack;
    }
  }

  function renderPills(currentSection) {
    pillsContainer.innerHTML = "";
    // Skip "setup" from pill display
    var displaySections = SECTION_ORDER.filter(function (s) { return s !== "setup"; });
    var currentIdx = displaySections.indexOf(currentSection);

    displaySections.forEach(function (section, i) {
      var pill = el("div", { className: "progress-pill" });
      if (i < currentIdx) pill.classList.add("completed");
      else if (i === currentIdx) pill.classList.add("current");
      else pill.classList.add("upcoming");
      pillsContainer.appendChild(pill);
    });

    // Scroll to center current pill
    var currentPill = pillsContainer.querySelector(".progress-pill.current");
    if (currentPill) {
      currentPill.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    }
  }


  // ============== PHASE: EMAIL ==============

  function showEmail() {
    state.phase = "email";
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, "Let\u2019s start with your email");
    frag.appendChild(q);
    var note = el("p", { className: "form-note" }, "So you can pick up where you left off, on any device.");
    frag.appendChild(note);
    var input = el("input", {
      className: "form-input form-input-single",
      type: "email",
      placeholder: "you@email.com"
    });
    frag.appendChild(input);
    var errorDiv = el("p", { className: "form-error" });
    errorDiv.style.display = "none";
    frag.appendChild(errorDiv);
    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: async function () {
        var email = input.value.trim();
        if (!email || !email.includes("@")) {
          input.classList.add("shake");
          setTimeout(function () { input.classList.remove("shake"); }, 500);
          return;
        }
        btn.disabled = true;
        btn.textContent = "Sending code...";
        errorDiv.style.display = "none";
        try {
          await window.signInWithOtp(email);
          state.meta.email = email;
          showOtp(email);
        } catch (err) {
          errorDiv.textContent = err.message || "Something went wrong. Try again.";
          errorDiv.style.display = "block";
          btn.disabled = false;
          btn.textContent = "Continue \u2192";
        }
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
  }


  // ============== PHASE: OTP ==============

  function showOtp(email) {
    state.phase = "otp";
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, "Check your inbox");
    frag.appendChild(q);
    var note = el("p", { className: "form-note" }, "Enter the 6-digit code we sent to " + email);
    frag.appendChild(note);
    var input = el("input", {
      className: "form-input form-input-single form-otp-input",
      type: "text",
      placeholder: "000000",
      maxLength: "6"
    });
    frag.appendChild(input);
    var errorDiv = el("p", { className: "form-error" });
    errorDiv.style.display = "none";
    frag.appendChild(errorDiv);
    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: async function () {
        var code = input.value.trim();
        if (!code || code.length < 6) {
          input.classList.add("shake");
          setTimeout(function () { input.classList.remove("shake"); }, 500);
          return;
        }
        btn.disabled = true;
        btn.textContent = "Verifying...";
        errorDiv.style.display = "none";
        try {
          var result = await window.verifyOtp(email, code);
          currentUserId = result.user ? result.user.id : null;
          onAuthComplete();
        } catch (err) {
          errorDiv.textContent = err.message || "Invalid code. Try again.";
          errorDiv.style.display = "block";
          btn.disabled = false;
          btn.textContent = "Verify \u2192";
        }
      }
    }, "Verify \u2192");
    frag.appendChild(btn);
    var resend = el("button", {
      className: "form-btn form-btn-link",
      onClick: async function () {
        resend.textContent = "Sending...";
        try {
          await window.signInWithOtp(email);
          resend.textContent = "Code resent \u2713";
        } catch (err) {
          resend.textContent = "Resend code";
        }
      }
    }, "Resend code");
    frag.appendChild(resend);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
  }


  // ============== AUTH COMPLETE ==============

  function onAuthComplete() {
    var key = getStorageKey();
    if (!key) { showIntro(); return; }
    try {
      var saved = localStorage.getItem(key);
      if (saved) {
        var parsed = JSON.parse(saved);
        // Handle V2 state migration
        if (parsed.currentGuna != null && !parsed.flow) {
          // V2 format: preserve answers, restart navigation
          if (parsed.answers && Object.keys(parsed.answers).length > 0) {
            showResume(parsed);
            return;
          }
        }
        if (parsed.answers && Object.keys(parsed.answers).length > 0) {
          showResume(parsed);
          return;
        }
      }
    } catch (e) {
      console.error("Failed to load saved state:", e);
    }
    showIntro();
  }


  // ============== PHASE: RESUME ==============

  function showResume(savedState) {
    state.phase = "resume";
    // Temporarily compute progress
    var origAnswers = state.answers;
    state.answers = savedState.answers || {};
    var pct = calculateProgress();
    state.answers = origAnswers;

    var name = (savedState.answers && savedState.answers.preferred_name) ||
               (savedState.answers && savedState.answers.full_name) || "";
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, "Welcome back" + (name ? ", " + name : "") + "!");
    frag.appendChild(q);
    var note = el("p", { className: "form-note" }, "You were " + pct + "% done.");
    frag.appendChild(note);
    var resumeBtn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () { restoreState(savedState); }
    }, "Resume \u2192");
    frag.appendChild(resumeBtn);
    var startOverBtn = el("button", {
      className: "form-btn form-btn-secondary",
      onClick: function () {
        var key = getStorageKey();
        if (key) localStorage.removeItem(key);
        // Reset all in-memory state
        state.answers = {};
        state.flow = [];
        state.flowIndex = 0;
        state.currentSubStep = null;
        state.previousSection = null;
        state.editingFromReview = false;
        state.editingField = null;
        state.proxyIndex = 0;
        state.meta = { intent: null, email: state.meta.email, proxy: {} };
        showIntro();
      }
    }, "Start over");
    frag.appendChild(startOverBtn);
    renderCard(frag);
  }


  // ============== PHASE: INTRO ==============

  function showIntro() {
    state.phase = "intro";
    renderMessage(INTRO.text, INTRO.button, function () {
      recomputeFlow();
      state.flowIndex = 0;
      state.phase = "questions";
      state.previousSection = null;
      persistState();
      showQuestion();
    });
  }


  // ============== PHASE: QUESTIONS ==============

  function showQuestion(skipTransition) {
    state.phase = "questions";

    // Past the end of flow?
    if (state.flowIndex >= state.flow.length) {
      showReview();
      return;
    }

    var qId = state.flow[state.flowIndex];
    var q = QUESTIONS[QUESTION_INDEX[qId]];
    if (!q) {
      // Safety: advance past unknown question
      state.flowIndex++;
      showQuestion();
      return;
    }

    // Intent branching: if "For someone else", go to proxy flow
    if (q.id === "intent" && state.answers.intent) {
      // Already answered, skip
      advanceToNext();
      return;
    }

    // Section transition check (skip when going back)
    if (!skipTransition && q.section !== state.previousSection && SECTION_TRANSITIONS[q.section]) {
      var name = state.answers.preferred_name || state.answers.full_name || "";
      var text = SECTION_TRANSITIONS[q.section].replace(/{name}/g, name);
      state.previousSection = q.section;
      renderMessage(text, "Continue \u2192", function () {
        renderQuestion(q);
      });
      return;
    }
    state.previousSection = q.section;
    renderQuestion(q);
  }


  // ============== QUESTION RENDERING ==============

  function getResolvedOptions(q) {
    // Try conditional options first
    if (q.optionsConditional) {
      var resolved = resolveConditionalOptions(q.id, state.answers);
      if (resolved) return resolved;
    }
    // Dynamic string reference
    if (typeof q.options === "string") {
      return resolveOptions(q.id, state.answers);
    }
    // Static array
    return q.options;
  }

  function renderQuestion(q) {
    // Multi-step types
    if (q.type === "two_step_date") { renderDateQuestion(q); return; }
    if (q.type === "location_tree") { renderLocationQuestion(q); return; }
    if (q.type === "two_step_location") { renderTwoStepLocationQuestion(q); return; }
    if (q.type === "two_step_range") { renderTwoStepRangeQuestion(q); return; }
    if (q.type === "two_step_same_screen") { renderSameScreenQuestion(q); return; }

    // Text input
    if (q.type === "text_input") {
      renderTextInputQuestion(q);
      return;
    }

    // Phone input
    if (q.type === "phone_input") {
      renderPhoneInput(q.question, q.placeholder, function (val) {
        saveAnswer(q.field, val);
        advanceToNext();
      });
      return;
    }

    var options = getResolvedOptions(q);
    if (!options || options.length === 0) {
      advanceToNext();
      return;
    }

    // Multi-select
    if (q.type === "multi_select") {
      renderMultiSelectQuestion(q, options);
      return;
    }

    // Single select (default)
    renderSingleSelectQuestion(q, options);
  }

  function renderSingleSelectQuestion(q, options) {
    var frag = document.createDocumentFragment();
    var heading = el("h2", { className: "form-question" }, q.question);
    frag.appendChild(heading);
    if (q.helperText) {
      var note = el("p", { className: "form-note" }, q.helperText);
      frag.appendChild(note);
    }
    var cols = q.columns || 0;
    var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
    options.forEach(function (opt) {
      var btn = el("button", {
        className: "form-btn form-btn-option",
        onClick: function () {
          // Flash effect + auto-advance after 300ms
          btn.classList.add("flash");
          saveAnswer(q.field, opt.value);
          // Handle intent branching
          if (q.id === "intent" && opt.value === "proxy") {
            state.meta.intent = "proxy";
            setTimeout(function () {
              state.proxyIndex = 0;
              showProxy();
            }, 300);
            return;
          }
          if (q.id === "intent") {
            state.meta.intent = opt.value;
          }
          setTimeout(function () { advanceToNext(); }, 300);
        }
      }, opt.label);
      grid.appendChild(btn);
    });
    frag.appendChild(grid);
    renderCard(frag);
  }

  function renderMultiSelectQuestion(q, options) {
    var selected = new Set();
    // Pre-select if editing from review
    var existing = state.answers[q.field];
    if (Array.isArray(existing)) {
      existing.forEach(function (v) { selected.add(v); });
    }

    var frag = document.createDocumentFragment();
    var heading = el("h2", { className: "form-question" }, q.question);
    frag.appendChild(heading);
    if (q.helperText) {
      var note = el("p", { className: "form-note" }, q.helperText);
      frag.appendChild(note);
    }
    var cols = q.columns || 0;
    var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
    options.forEach(function (opt) {
      var btn = el("button", {
        className: "form-btn form-btn-option" + (selected.has(opt.value) ? " selected" : ""),
        onClick: function () {
          if (selected.has(opt.value)) {
            selected.delete(opt.value);
            btn.classList.remove("selected");
          } else {
            selected.add(opt.value);
            btn.classList.add("selected");
          }
        }
      }, opt.label);
      grid.appendChild(btn);
    });
    frag.appendChild(grid);
    var doneBtn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () {
        saveAnswer(q.field, Array.from(selected));
        advanceToNext();
      }
    }, q.doneLabel || "Done \u2713");
    frag.appendChild(doneBtn);
    renderCard(frag);
  }

  function renderTextInputQuestion(q) {
    var frag = document.createDocumentFragment();
    var heading = el("h2", { className: "form-question" }, q.question);
    frag.appendChild(heading);
    if (q.helperText) {
      var note = el("p", { className: "form-note" }, q.helperText);
      frag.appendChild(note);
    }
    var input = el("input", {
      className: "form-input form-input-single",
      type: "text",
      placeholder: q.placeholder || ""
    });
    // Pre-fill if editing
    if (state.answers[q.field]) input.value = state.answers[q.field];
    frag.appendChild(input);
    var submitText = function () {
      var val = input.value.trim();
      if (!val) {
        input.classList.add("shake");
        setTimeout(function () { input.classList.remove("shake"); }, 500);
        return;
      }
      saveAnswer(q.field, val);
      advanceToNext();
    };
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); submitText(); }
    });
    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: submitText
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
  }


  // ============== MULTI-STEP: DATE ==============

  function renderDateQuestion(q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var options = resolveStepOptions(q.step1.options, q.id);
      var cols = q.step1.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step1.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      options.forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step1.field || "_birth_year", opt.value);
            state.currentSubStep = "step2";
            setTimeout(function () { renderDateQuestion(q); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    } else if (state.currentSubStep === "step2") {
      var options = resolveStepOptions(q.step2.options, q.id);
      var cols = q.step2.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step2.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      options.forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step2.field || "_birth_month", opt.value);
            var year = state.answers[q.step1.field || "_birth_year"];
            var month = opt.value;
            var dob = year + "-" + String(month).padStart(2, "0") + "-15";
            saveAnswer(q.field, dob);
            state.currentSubStep = null;
            setTimeout(function () { advanceToNext(); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    }
  }


  // ============== MULTI-STEP: LOCATION TREE ==============

  function renderLocationQuestion(q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var step = q.step1;
      var options = Array.isArray(step.options) ? step.options : (resolveOptions(q.id, state.answers) || []);
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, step.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" });
      options.forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step1.field || "_location_type", opt.value);
            // Also save to _location_type for downstream resolvers (income, conditionals)
            if (q.id === "current_location") saveAnswer("_location_type", opt.value);
            state.currentSubStep = "step2";
            setTimeout(function () { renderLocationQuestion(q); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    } else if (state.currentSubStep === "step2") {
      var locField = q.step1.field || "_location_type";
      var isIndia = state.answers[locField] === "India";
      var step = isIndia ? q.step2India : q.step2Abroad;
      if (!step) step = isIndia ? q.step2_india : q.step2_abroad; // fallback
      var options = step.options;
      if (typeof options === "string") {
        // Resolve using V3 resolver
        if (options === "states_india") options = STATES_INDIA;
        else if (options === "states_india_full") options = STATES_INDIA_FULL;
        else if (options === "countries") options = COUNTRIES;
        else options = resolveOptions(q.id, state.answers) || [];
      }
      var cols = step.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, step.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      (options || []).forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(step.field, opt.value);
            if (isIndia) saveAnswer("country_current", "India");
            state.currentSubStep = "step3";
            setTimeout(function () { renderLocationQuestion(q); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    } else if (state.currentSubStep === "step3") {
      var step = q.step3;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, step.text);
      frag.appendChild(heading);
      var input = el("input", {
        className: "form-input form-input-single",
        type: "text",
        placeholder: step.placeholder || "City"
      });
      frag.appendChild(input);
      var submitCity = function () {
        var val = input.value.trim();
        if (!val) {
          input.classList.add("shake");
          setTimeout(function () { input.classList.remove("shake"); }, 500);
          return;
        }
        saveAnswer(step.field, val);
        state.currentSubStep = null;
        advanceToNext();
      };
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); submitCity(); }
      });
      var btn = el("button", {
        className: "form-btn form-btn-primary",
        onClick: submitCity
      }, "Continue \u2192");
      frag.appendChild(btn);
      renderCard(frag);
      setTimeout(function () { input.focus(); }, 100);
    }
  }


  // ============== MULTI-STEP: TWO-STEP LOCATION ==============

  function renderTwoStepLocationQuestion(q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var options = resolveStepOptions(q.step1.options, q.id);
      var cols = q.step1.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step1.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      (options || []).forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step1.field, opt.value);
            state.currentSubStep = "step2";
            setTimeout(function () { renderTwoStepLocationQuestion(q); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    } else if (state.currentSubStep === "step2") {
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step2.text);
      frag.appendChild(heading);
      var input = el("input", {
        className: "form-input form-input-single",
        type: "text",
        placeholder: q.step2.placeholder || "City"
      });
      frag.appendChild(input);
      var submitLoc = function () {
        var val = input.value.trim();
        if (!val) {
          input.classList.add("shake");
          setTimeout(function () { input.classList.remove("shake"); }, 500);
          return;
        }
        saveAnswer(q.step2.field, val);
        var composed = (state.answers[q.step1.field] || "") + ", " + val;
        saveAnswer(q.field, composed);
        state.currentSubStep = null;
        advanceToNext();
      };
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); submitLoc(); }
      });
      var btn = el("button", {
        className: "form-btn form-btn-primary",
        onClick: submitLoc
      }, "Continue \u2192");
      frag.appendChild(btn);
      renderCard(frag);
      setTimeout(function () { input.focus(); }, 100);
    }
  }


  // ============== MULTI-STEP: TWO-STEP RANGE ==============

  function resolveStepOptions(optionsRef, qId) {
    if (Array.isArray(optionsRef)) return optionsRef;
    if (typeof optionsRef !== "string") return [];
    // Try resolving the string reference directly via the switch in resolveOptions
    // by temporarily looking up as if it were the question's options
    var q = QUESTIONS[QUESTION_INDEX[qId]];
    var saved = q ? q.options : undefined;
    if (q) q.options = optionsRef;
    var result = resolveOptions(qId, state.answers) || [];
    if (q) q.options = saved;
    return result;
  }

  function renderTwoStepRangeQuestion(q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var options = resolveStepOptions(q.step1.options, q.id);
      var cols = q.step1.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step1.text);
      frag.appendChild(heading);

      // "Doesn't matter" button if applicable
      if (q.hasDoesntMatter) {
        var dmBtn = el("button", {
          className: "doesnt-matter-btn",
          onClick: function () {
            saveAnswer(q.step1.field, "doesnt_matter");
            saveAnswer(q.step2.field, "doesnt_matter");
            saveAnswer(q.field, "doesnt_matter");
            state.currentSubStep = null;
            advanceToNext();
          }
        }, q.doesntMatterLabel || "Doesn\u2019t matter");
        frag.appendChild(dmBtn);
      }

      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      (options || []).forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step1.field, opt.value);
            state.currentSubStep = "step2";
            setTimeout(function () { renderTwoStepRangeQuestion(q); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    } else if (state.currentSubStep === "step2") {
      var options = resolveStepOptions(q.step2.options, q.id);
      // Filter max options to be >= min
      var minVal = state.answers[q.step1.field];
      if (minVal && options.length > 0) {
        var minIdx = options.findIndex(function (o) { return o.value === minVal; });
        if (minIdx >= 0) options = options.slice(minIdx);
      }
      var cols = q.step2.columns || 0;
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, q.step2.text);
      frag.appendChild(heading);
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      (options || []).forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            saveAnswer(q.step2.field, opt.value);
            var rangeVal = state.answers[q.step1.field] + "-" + opt.value;
            saveAnswer(q.field, rangeVal);
            state.currentSubStep = null;
            setTimeout(function () { advanceToNext(); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    }
  }


  // ============== NEW: TWO-STEP SAME SCREEN ==============

  function renderSameScreenQuestion(q) {
    var frag = document.createDocumentFragment();
    var heading = el("h2", { className: "form-question" }, q.question);
    frag.appendChild(heading);

    // "Doesn't matter" button
    if (q.hasDoesntMatter) {
      var dmBtn = el("button", {
        className: "doesnt-matter-btn",
        onClick: function () {
          saveAnswer(q.step1.field, "doesnt_matter");
          saveAnswer(q.step2.field, "doesnt_matter");
          saveAnswer(q.field, "doesnt_matter");
          advanceToNext();
        }
      }, q.doesntMatterLabel || "Doesn\u2019t matter");
      frag.appendChild(dmBtn);
    }

    // Two dropdowns side by side
    var row = el("div", { className: "same-screen-row" });

    var col1 = el("div", { className: "same-screen-col" });
    var label1 = el("label", null, q.step1.text || "Min");
    col1.appendChild(label1);
    var select1 = el("select", { className: "form-select" });
    var opts1 = resolveStepOptions(q.step1.options, q.id);
    (opts1 || []).forEach(function (opt) {
      var o = el("option", { value: opt.value }, opt.label);
      select1.appendChild(o);
    });
    col1.appendChild(select1);
    row.appendChild(col1);

    var col2 = el("div", { className: "same-screen-col" });
    var label2 = el("label", null, q.step2.text || "Max");
    col2.appendChild(label2);
    var select2 = el("select", { className: "form-select" });
    var opts2 = resolveStepOptions(q.step2.options, q.id);
    (opts2 || []).forEach(function (opt) {
      var o = el("option", { value: opt.value }, opt.label);
      select2.appendChild(o);
    });
    col2.appendChild(select2);
    row.appendChild(col2);

    frag.appendChild(row);

    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () {
        var v1 = select1.value;
        var v2 = select2.value;
        saveAnswer(q.step1.field, v1);
        saveAnswer(q.step2.field, v2);
        saveAnswer(q.field, v1 + "-" + v2);
        advanceToNext();
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
  }


  // ============== SAVE ANSWER ==============

  function saveAnswer(field, value) {
    state.answers[field] = value;
    persistState();
  }


  // ============== PHASE: REVIEW ==============

  function showReview() {
    state.phase = "review";
    persistState();

    var frag = document.createDocumentFragment();
    var heading = el("h2", { className: "form-question" }, "Review your answers");
    frag.appendChild(heading);
    var note = el("p", { className: "form-note" }, "Make sure everything looks right. Tap Edit to change anything.");
    frag.appendChild(note);

    // Group answers by section
    var sectionGroups = {};
    SECTION_ORDER.forEach(function (s) { sectionGroups[s] = []; });

    // Walk the flow to get ordered, applicable questions
    var flow = state.flow.length > 0 ? state.flow : getQuestionFlow(state.answers);
    flow.forEach(function (qId) {
      var q = QUESTIONS[QUESTION_INDEX[qId]];
      if (!q) return;
      if (q.id === "intent") return; // Don't show intent in review
      var val = state.answers[q.field];
      if (val == null) return;
      var section = q.section || "setup";
      if (!sectionGroups[section]) sectionGroups[section] = [];
      sectionGroups[section].push({ qId: qId, q: q, value: val });
    });

    SECTION_ORDER.forEach(function (section) {
      var items = sectionGroups[section];
      if (!items || items.length === 0) return;
      var sectionEl = el("div", { className: "review-section" });
      var label = SECTIONS[section] ? SECTIONS[section].label : section;
      var titleEl = el("div", { className: "review-section-title" }, label);
      sectionEl.appendChild(titleEl);

      items.forEach(function (item) {
        var displayVal = Array.isArray(item.value) ? item.value.join(", ") : String(item.value);
        // Truncate long values
        if (displayVal.length > 60) displayVal = displayVal.substring(0, 57) + "...";
        var questionLabel = item.q.question || item.q.field;
        // Use first line only, max 50 chars
        var labelText = questionLabel.split("\n")[0];
        if (labelText.length > 50) labelText = labelText.substring(0, 47) + "...";

        var row = el("div", { className: "review-row" });
        row.appendChild(el("span", { className: "review-label" }, labelText));
        row.appendChild(el("span", { className: "review-value" }, displayVal));
        var editBtn = el("button", {
          className: "review-edit-btn",
          onClick: (function (qId) {
            return function () {
              var idx = state.flow.indexOf(qId);
              if (idx >= 0) {
                state.flowIndex = idx;
                state.editingFromReview = true;
                state.editingField = qId;
                state.currentSubStep = null;
                showQuestion();
              }
            };
          })(item.qId)
        }, "Edit");
        row.appendChild(editBtn);
        sectionEl.appendChild(row);
      });

      frag.appendChild(sectionEl);
    });

    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () { showClose(); }
    }, "Looks good \u2192");
    frag.appendChild(btn);
    renderCard(frag);
  }


  // ============== PHASE: CLOSE ==============

  function showClose() {
    state.phase = "close";
    var name = state.answers.preferred_name || state.answers.full_name || "";
    var text = CLOSE_MESSAGE.replace(/{name}/g, name);
    renderMessage(text, "Almost done \u2014 one last thing", function () {
      showPhone();
    });
  }


  // ============== PHASE: PHONE ==============

  function showPhone() {
    state.phase = "phone";
    persistState();
    renderPhoneInput("What\u2019s the best number to reach you?", "Phone number", function (fullPhone) {
      submitForm(fullPhone);
    });
  }


  // ============== PHASE: SUBMIT ==============

  async function submitForm(phone) {
    state.phase = "done";
    renderMessage("Submitting your answers...", "", function () {});
    var btn = container.querySelector(".form-btn");
    if (btn) btn.style.display = "none";

    var payload = {
      phone: phone,
      name: state.answers.full_name || "",
      preferred_name: state.answers.preferred_name || "",
      answers: {},
      meta: state.meta
    };

    // Iterate all questions in the flow and collect answers
    for (var i = 0; i < QUESTIONS.length; i++) {
      var q = QUESTIONS[i];
      if (!q || !q.field) continue;

      // Multi-step types: collect sub-fields
      if (q.type === "location_tree") {
        ["country_current", "state_india", "city_current", "_location_type"].forEach(function (f) {
          if (state.answers[f] != null) {
            payload.answers[f] = { value: state.answers[f], table: "users" };
          }
        });
        continue;
      }
      if (q.type === "two_step_date") {
        if (state.answers[q.field] != null) {
          payload.answers[q.field] = { value: state.answers[q.field], table: q.dbTable };
        }
        if (q.step1 && q.step1.field && state.answers[q.step1.field] != null) {
          payload.answers[q.step1.field] = { value: state.answers[q.step1.field], table: q.dbTable };
        }
        continue;
      }
      if (q.type === "two_step_location" || q.type === "two_step_range" || q.type === "two_step_same_screen") {
        if (q.step1 && q.step1.field && state.answers[q.step1.field] != null) {
          payload.answers[q.step1.field] = { value: state.answers[q.step1.field], table: q.dbTable };
        }
        if (q.step2 && q.step2.field && state.answers[q.step2.field] != null) {
          payload.answers[q.step2.field] = { value: state.answers[q.step2.field], table: q.dbTable };
        }
        if (state.answers[q.field] != null) {
          payload.answers[q.field] = { value: state.answers[q.field], table: q.dbTable };
        }
        continue;
      }

      // Standard fields
      if (state.answers[q.field] != null) {
        payload.answers[q.field] = { value: state.answers[q.field], table: q.dbTable };
      }
    }

    try {
      var resp = await fetch(API_BASE + "/api/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      showSuccess();
    } catch (err) {
      console.error("Submit error:", err);
      showError(phone);
    }
  }

  function showSuccess() {
    var key = getStorageKey();
    if (key) localStorage.removeItem(key);

    var name = state.answers.preferred_name || state.answers.full_name || "";
    var frag = document.createDocumentFragment();
    var check = el("div", { className: "success-check" }, "\u2713");
    frag.appendChild(check);
    var h = el("h2", { className: "form-question" }, "You\u2019re in, " + name + ".");
    frag.appendChild(h);
    var p = el("p", { className: "form-note" },
      "Masii is on it. When she finds someone worth your time, she\u2019ll reach out."
    );
    frag.appendChild(p);
    var link = el("a", { href: "index.html", className: "form-btn form-btn-primary" }, "Back to Masii");
    frag.appendChild(link);
    renderCard(frag);
  }

  function showError(phone) {
    state.phase = "error";
    var frag = document.createDocumentFragment();
    var h = el("h2", { className: "form-question" }, "Something went wrong.");
    frag.appendChild(h);
    var p = el("p", { className: "form-note" },
      "Your answers are saved locally. Try again or reach out on Telegram."
    );
    frag.appendChild(p);
    var btn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () { submitForm(phone); }
    }, "Try again \u2192");
    frag.appendChild(btn);
    var tg = el("a", {
      href: "https://t.me/masiiapp_bot",
      className: "form-btn form-btn-secondary",
      target: "_blank"
    }, "Open Telegram \u2192");
    frag.appendChild(tg);
    renderCard(frag);
  }


  // ============== PHASE: PROXY ==============

  function showProxy() {
    state.phase = "proxy";
    if (state.proxyIndex >= PROXY_QUESTIONS.length) {
      showProxyClose();
      return;
    }
    var pq = PROXY_QUESTIONS[state.proxyIndex];

    if (pq.type === "text_input") {
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, pq.question);
      frag.appendChild(heading);
      var input = el("input", {
        className: "form-input form-input-single",
        type: "text",
        placeholder: pq.placeholder || ""
      });
      frag.appendChild(input);
      var btn = el("button", {
        className: "form-btn form-btn-primary",
        onClick: function () {
          var val = input.value.trim();
          if (!val) {
            input.classList.add("shake");
            setTimeout(function () { input.classList.remove("shake"); }, 500);
            return;
          }
          state.meta.proxy[pq.field] = val;
          if (pq.field === "person_name") saveAnswer("full_name", val);
          state.proxyIndex++;
          showProxy();
        }
      }, "Continue \u2192");
      frag.appendChild(btn);
      renderCard(frag);
      setTimeout(function () { input.focus(); }, 100);
    } else if (pq.type === "phone_input") {
      renderPhoneInput(pq.question, pq.placeholder, function (val) {
        state.meta.proxy[pq.field] = val;
        state.proxyIndex++;
        showProxy();
      });
    } else if (pq.type === "location_tree") {
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, pq.question);
      frag.appendChild(heading);
      var input = el("input", {
        className: "form-input form-input-single",
        type: "text",
        placeholder: "City, Country"
      });
      frag.appendChild(input);
      var btn = el("button", {
        className: "form-btn form-btn-primary",
        onClick: function () {
          var val = input.value.trim();
          if (!val) {
            input.classList.add("shake");
            setTimeout(function () { input.classList.remove("shake"); }, 500);
            return;
          }
          state.meta.proxy[pq.field] = val;
          state.proxyIndex++;
          showProxy();
        }
      }, "Continue \u2192");
      frag.appendChild(btn);
      renderCard(frag);
      setTimeout(function () { input.focus(); }, 100);
    } else {
      // single_select
      var options = pq.options;
      if (typeof options === "string") {
        if (options === "birth_years") options = getBirthYears();
        else if (options === "castes_by_religion") {
          options = (typeof getCastesByReligionAndState === "function")
            ? getCastesByReligionAndState(state.meta.proxy.person_religion, null)
            : [];
        } else if (options === "religion_list") {
          // Get from first question with religion options
          var relQ = QUESTIONS[QUESTION_INDEX["religion"]];
          options = relQ ? relQ.options : [];
        } else if (options === "marital_status_list") {
          var msQ = QUESTIONS[QUESTION_INDEX["marital_status"]];
          options = msQ ? msQ.options : [];
        } else if (options === "education_level_list") {
          var edQ = QUESTIONS[QUESTION_INDEX["education_level"]];
          options = edQ ? edQ.options : [];
        } else if (options === "occupation_sector_list") {
          var ocQ = QUESTIONS[QUESTION_INDEX["occupation_sector"]];
          options = ocQ ? ocQ.options : [];
        } else {
          options = resolveOptions(pq.field, state.answers) || [];
        }
      }
      if (!options || options.length === 0) {
        state.proxyIndex++;
        showProxy();
        return;
      }
      var frag = document.createDocumentFragment();
      var heading = el("h2", { className: "form-question" }, pq.question);
      frag.appendChild(heading);
      var cols = pq.columns || 0;
      var grid = el("div", { className: "form-options" + (cols ? " cols-" + cols : "") });
      options.forEach(function (opt) {
        var btn = el("button", {
          className: "form-btn form-btn-option",
          onClick: function () {
            btn.classList.add("flash");
            state.meta.proxy[pq.field] = opt.value;
            if (pq.field === "person_gender") saveAnswer("gender", opt.value);
            state.proxyIndex++;
            setTimeout(function () { showProxy(); }, 300);
          }
        }, opt.label);
        grid.appendChild(btn);
      });
      frag.appendChild(grid);
      renderCard(frag);
    }
  }

  function showProxyClose() {
    var text = PROXY_CLOSE.replace(/{person_name}/g, state.meta.proxy.person_name || "them");
    renderMessage(text, "Done \u2192", function () {
      submitProxyForm();
    });
  }

  async function submitProxyForm() {
    state.phase = "done";
    renderMessage("Submitting...", "", function () {});
    var btn = container.querySelector(".form-btn");
    if (btn) btn.style.display = "none";

    var payload = {
      type: "proxy",
      meta: state.meta,
      proxy_data: state.meta.proxy
    };

    try {
      var resp = await fetch(API_BASE + "/api/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      showProxySuccess();
    } catch (err) {
      console.error("Proxy submit error:", err);
      showProxySuccess();
    }
  }

  function showProxySuccess() {
    var frag = document.createDocumentFragment();
    var check = el("div", { className: "success-check" }, "\u2713");
    frag.appendChild(check);
    var h = el("h2", { className: "form-question" }, "Got it! We\u2019ll take it from here.");
    frag.appendChild(h);
    var p = el("p", { className: "form-note" },
      "We\u2019ll reach out to " + (state.meta.proxy.person_name || "them") + " to complete their profile."
    );
    frag.appendChild(p);
    var link = el("a", { href: "index.html", className: "form-btn form-btn-primary" }, "Back to Masii");
    frag.appendChild(link);
    renderCard(frag);
  }


  // ============== INIT ==============

  async function init() {
    try {
      var session = await window.getSession();
      if (session && session.user) {
        currentUserId = session.user.id;
        state.meta.email = session.user.email;
        onAuthComplete();
      } else {
        showEmail();
      }
    } catch (e) {
      console.error("Auth check failed:", e);
      showEmail();
    }
  }

  // Start
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
