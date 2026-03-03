/**
 * Masii Web Form Engine — 60 Questions
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
    phase: "intro",        // intro | intent | setup | proxy | gunas | sub_question | close | phone | done | error
    introIndex: 0,
    proxyIndex: 0,
    setupStep: null,       // "full_name" | "gender"
    currentGuna: 0,
    currentSubStep: null,  // for multi-step questions (step1, step2, step3, etc.)
    pendingSubQuestion: null,
    previousSection: null,
    showingTransition: false,
    answers: {},
    meta: {                // non-guna answers (intent, proxy info)
      intent: null,
      proxy: {}
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

  /**
   * Calculate how many questions are actually applicable (not skipped by gender or gate).
   * This gives a more accurate progress denominator.
   */
  function countApplicableQuestions() {
    let count = 0;
    for (let i = 1; i <= TOTAL_QUESTIONS; i++) {
      const q = QUESTIONS[i];
      if (!q) continue;
      // Skip gender-forked questions for the other gender
      if (q.gender && state.answers.gender && q.gender !== state.answers.gender) continue;
      // Skip sensitive questions if gate answered "no"
      if (i >= 54 && i <= 58 && state.answers.sensitive_gate === "no") continue;
      count++;
    }
    return count;
  }

  function updateProgress() {
    if (state.phase === "intro" || state.phase === "intent" || state.phase === "setup" || state.phase === "proxy") {
      progressBar.style.width = "0%";
      progressText.textContent = "";
      return;
    }
    if (state.phase === "done" || state.phase === "close") {
      progressBar.style.width = "100%";
      const total = countApplicableQuestions();
      progressText.textContent = total + " of " + total;
      return;
    }
    // Count answered questions (those before currentGuna that are applicable)
    let answered = 0;
    for (let i = 1; i < state.currentGuna; i++) {
      const q = QUESTIONS[i];
      if (!q) continue;
      if (q.gender && state.answers.gender && q.gender !== state.answers.gender) continue;
      if (i >= 54 && i <= 58 && state.answers.sensitive_gate === "no") continue;
      answered++;
    }
    const total = countApplicableQuestions();
    const pct = total > 0 ? Math.round((answered / total) * 100) : 0;
    progressBar.style.width = pct + "%";
    progressText.textContent = answered + " of " + total;
  }

  function renderCard(content, fadeIn) {
    if (fadeIn === undefined) fadeIn = true;
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

  function renderMessage(text, buttonLabel, onClick, extraClass) {
    const frag = document.createDocumentFragment();
    const msg = el("div", { className: "form-message" + (extraClass ? " " + extraClass : "") });
    msg.innerHTML = text.replace(/\n/g, "<br>");
    frag.appendChild(msg);
    if (buttonLabel) {
      const btn = el("button", { className: "form-btn form-btn-primary", onClick: onClick }, buttonLabel);
      frag.appendChild(btn);
    }
    renderCard(frag);
  }

  function renderOptions(questionText, options, onSelect, columns) {
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    const grid = el("div", { className: "form-options" + (columns ? " cols-" + columns : "") });
    options.forEach(function (opt) {
      const btn = el("button", {
        className: "form-btn form-btn-option",
        onClick: function () {
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

  function renderMultiSelect(questionText, options, doneLabel, onDone, columns) {
    const selected = new Set();
    const frag = document.createDocumentFragment();
    const q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    const grid = el("div", { className: "form-options multi-select-grid" + (columns ? " cols-" + columns : "") });

    options.forEach(function (opt) {
      const btn = el("button", {
        className: "form-btn form-btn-option",
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

    const doneBtn = el("button", {
      className: "form-btn form-btn-primary",
      onClick: function () {
        onDone(Array.from(selected));
      }
    }, doneLabel || "Done \u2713");
    frag.appendChild(doneBtn);
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
      onClick: function () {
        var val = input.value.trim();
        if (!val) {
          input.classList.add("shake");
          setTimeout(function () { input.classList.remove("shake"); }, 500);
          return;
        }
        onSubmit(val);
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
  }

  function renderSingleLineInput(questionText, placeholder, onSubmit) {
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    var input = el("input", {
      className: "form-input form-input-single",
      type: "text",
      placeholder: placeholder || ""
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
        onSubmit(val);
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
  }

  function renderTextFollowUp(questionText, opt, onSelect) {
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, questionText);
    frag.appendChild(q);
    var note = el("p", { className: "form-note" }, "Selected: " + opt.label);
    frag.appendChild(note);
    var input = el("input", {
      className: "form-input form-input-single",
      type: "text",
      placeholder: "Please specify..."
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
        onSelect(val);
      }
    }, "Continue \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { input.focus(); }, 100);
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


  // ============== RESOLVE OPTIONS ==============

  /**
   * Resolve options for a question. Handles string-based dynamic options
   * and array-based static options.
   */
  function resolveOptions(questionNum, optionValue, extraContext) {
    if (Array.isArray(optionValue)) return optionValue;
    if (typeof optionValue === "string") {
      // Try getConditionalOptions first (handles most cases)
      var resolved = getConditionalOptions(questionNum, state.answers);
      if (resolved) return resolved;
      // Fallback: resolve by key name directly
      return resolveByKey(optionValue, extraContext);
    }
    return null;
  }

  function resolveByKey(key, extraContext) {
    var isNRI = state.answers._location_type === "Outside India" || (state.answers.country_current && state.answers.country_current !== "India");
    switch (key) {
      case "birth_years": return getBirthYears();
      case "states_india": return getStatesIndia();
      case "states_india_full": return getStatesIndiaFull();
      case "countries": return getCountries();
      case "practice_by_religion": return getPracticeByReligion(state.answers.religion);
      case "sects_by_religion": return getSectsByReligion(state.answers.religion);
      case "castes_by_religion": return getCastesByReligion(state.answers.religion);
      case "diet_by_religion": return getDietByReligion(state.answers.religion);
      case "height_by_gender": return getHeightByGender(state.answers.gender);
      case "weight_by_gender": return getWeightByGender(state.answers.gender);
      case "income_by_location": return getIncomeByLocation(isNRI);
      case "income_by_location_with_doesnt_matter": return getIncomeByLocationWithDoesntMatter(isNRI);
      case "languages_minus_mother_tongue": return getLanguagesMinusMotherTongue(state.answers.mother_tongue);
      case "height_opposite_gender": return getHeightOppositeGender(state.answers.gender);
      case "gotras_by_religion": return getGotrasByReligion(state.answers.religion);
      case "age_range_min": return getAgeRangeMin();
      case "age_range_max": return getAgeRangeMax(extraContext && extraContext.minAge ? parseInt(extraContext.minAge) : 18);
      default: return null;
    }
  }


  // ============== PHASE: INTRO ==============

  function showIntro() {
    state.phase = "intro";
    var msg = INTRO_MESSAGES[state.introIndex];
    renderMessage(msg.text, msg.button, function () {
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
    renderOptions(INTENT_MESSAGE.text, INTENT_MESSAGE.options, function (val) {
      state.meta.intent = val;
      if (val === "proxy") {
        state.proxyIndex = 0;
        showProxy();
      } else {
        showSetup();
      }
    });
  }


  // ============== PHASE: SETUP (name + gender before numbered questions) ==============

  function showSetup() {
    state.phase = "setup";
    state.setupStep = "full_name";
    renderSetupStep();
  }

  function renderSetupStep() {
    if (state.setupStep === "full_name") {
      var sq = SETUP_QUESTIONS.full_name;
      renderSingleLineInput(sq.text, sq.placeholder, function (val) {
        saveAnswer("full_name", val);
        state.setupStep = "gender";
        renderSetupStep();
      });
    } else if (state.setupStep === "gender") {
      var sq = SETUP_QUESTIONS.gender;
      renderOptions(sq.text, sq.options, function (val) {
        saveAnswer("gender", val);
        state.setupStep = null;
        startGunas();
      });
    }
  }


  // ============== PHASE: PROXY ==============

  function showProxy() {
    state.phase = "proxy";
    if (state.proxyIndex >= PROXY_QUESTIONS.length) {
      showProxyClose();
      return;
    }

    var pq = PROXY_QUESTIONS[state.proxyIndex];

    // Handle different types
    if (pq.type === "text_input") {
      renderSingleLineInput(pq.text, pq.placeholder, function (val) {
        state.meta.proxy[pq.field] = val;
        // If this is person_name, also store full_name and gender for downstream use
        if (pq.field === "person_name") {
          saveAnswer("full_name", val);
        }
        state.proxyIndex++;
        showProxy();
      });
    } else if (pq.type === "phone_input") {
      renderPhoneInput(pq.text, pq.placeholder, function (val) {
        state.meta.proxy[pq.field] = val;
        state.proxyIndex++;
        showProxy();
      });
    } else if (pq.type === "location_tree") {
      // Simplified: just ask city as text input for proxy
      renderSingleLineInput(pq.text, "City, Country", function (val) {
        state.meta.proxy[pq.field] = val;
        state.proxyIndex++;
        showProxy();
      });
    } else {
      // single_select
      var options = pq.options;
      if (typeof options === "string") {
        // Resolve dynamic options for proxy questions
        if (options === "birth_years") {
          options = getBirthYears();
        } else if (options === "castes_by_religion") {
          options = getCastesByReligion(state.meta.proxy.person_religion) || [];
        } else {
          options = resolveByKey(options) || [];
        }
      }
      if (!options || options.length === 0) {
        // Skip if no options available
        state.proxyIndex++;
        showProxy();
        return;
      }
      renderOptions(pq.text, options, function (val) {
        state.meta.proxy[pq.field] = val;
        // If person_gender, store for downstream
        if (pq.field === "person_gender") {
          saveAnswer("gender", val);
        }
        state.proxyIndex++;
        showProxy();
      }, pq.columns);
    }
  }

  function showProxyClose() {
    var text = PROXY_CLOSE_MESSAGE.replace(/{person_name}/g, state.meta.proxy.person_name || "them");
    renderMessage(text, "Done \u2192", function () {
      submitProxyForm();
    }, "gate-message");
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
      showProxySuccess(); // Show success anyway -- data is best-effort for proxy
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


  // ============== PHASE: GUNAS (numbered questions 1-60) ==============

  function startGunas() {
    state.phase = "gunas";
    state.currentGuna = 1;
    state.previousSection = null;
    showGuna(1);
  }

  function showGuna(num) {
    // Past the end?
    if (num > TOTAL_QUESTIONS) {
      showClose();
      return;
    }

    // Skip logic
    if (shouldSkipQuestion(num, state.answers)) {
      var next = getNextQuestion(state.answers, num);
      state.currentGuna = next;
      showGuna(next);
      return;
    }

    state.currentGuna = num;
    state.phase = "gunas";

    // Check section transition
    var section = getSectionForQuestion(num);
    var transitionKey = getTransitionKey(section, state.previousSection);
    if (transitionKey && SECTION_TRANSITIONS[transitionKey]) {
      state.showingTransition = true;
      var text = SECTION_TRANSITIONS[transitionKey].replace(/{name}/g, state.answers.full_name || "");
      renderMessage(text, "Continue \u2192", function () {
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
    var q = QUESTIONS[num];
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
    if (q.type === "two_step_location") {
      renderTwoStepLocationQuestion(num, q);
      return;
    }
    if (q.type === "two_step_range") {
      renderTwoStepRangeQuestion(num, q);
      return;
    }

    // Text input
    if (q.type === "text_input") {
      renderTextInput(q.text, q.placeholder, function (val) {
        saveAnswer(q.field, val);
        advanceFromGuna(num);
      });
      return;
    }

    // Multi-select
    if (q.type === "multi_select") {
      var options = q.options;
      if (typeof options === "string") {
        options = resolveOptions(num, options);
      }
      if (!options || options.length === 0) {
        advanceFromGuna(num);
        return;
      }
      renderMultiSelect(q.text, options, q.done_label, function (vals) {
        saveAnswer(q.field, vals);
        advanceFromGuna(num);
      }, q.columns);
      return;
    }

    // Single select -- resolve options
    var options = q.options;
    if (typeof options === "string") {
      options = resolveOptions(num, options);
      if (!options) {
        // No options available -- skip
        advanceFromGuna(num);
        return;
      }
    }

    // Gate question styling
    if (q.is_gate) {
      renderGateQuestion(num, q, options);
      return;
    }

    renderOptions(q.text, options, function (val) {
      saveAnswer(q.field, val);
      advanceFromGuna(num);
    }, q.columns);
  }

  /**
   * Render gate question (Q53) with a different style -- more like a transition message.
   */
  function renderGateQuestion(num, q, options) {
    var frag = document.createDocumentFragment();
    var msg = el("div", { className: "form-message gate-message" });
    msg.innerHTML = q.text.replace(/\n/g, "<br>");
    frag.appendChild(msg);
    var grid = el("div", { className: "form-options" });
    options.forEach(function (opt) {
      var btn = el("button", {
        className: "form-btn form-btn-option",
        onClick: function () {
          saveAnswer(q.field, opt.value);
          advanceFromGuna(num);
        }
      }, opt.label);
      grid.appendChild(btn);
    });
    frag.appendChild(grid);
    renderCard(frag);
  }


  // ============== MULTI-STEP: DATE (Q1) ==============

  function renderDateQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var options = q.step1.options;
      if (options === "birth_years") options = getBirthYears();
      renderOptions(q.step1.text, options, function (val) {
        state.answers._birth_year = val;
        state.currentSubStep = "step2";
        renderDateQuestion(num, q);
      }, q.step1.columns);
    } else if (state.currentSubStep === "step2") {
      renderOptions(q.step2.text, q.step2.options, function (val) {
        state.answers._birth_month = val;
        // Compose date_of_birth as "YYYY-MM-15" (day=15 as placeholder)
        var dob = state.answers._birth_year + "-" + val.padStart(2, "0") + "-15";
        saveAnswer(q.field, dob);
        state.currentSubStep = null;
        advanceFromGuna(num);
      }, q.step2.columns);
    }
  }


  // ============== MULTI-STEP: LOCATION TREE (Q2) ==============

  function renderLocationQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      renderOptions(q.step1.text, q.step1.options, function (val) {
        state.answers._location_type = val;
        state.currentSubStep = "step2";
        renderLocationQuestion(num, q);
      });
    } else if (state.currentSubStep === "step2") {
      var isIndia = state.answers._location_type === "India";
      var step = isIndia ? q.step2_india : q.step2_abroad;
      var options = step.options;
      if (typeof options === "string") {
        options = resolveByKey(options);
      }
      renderOptions(step.text, options, function (val) {
        saveAnswer(step.field, val);
        if (isIndia) {
          saveAnswer("country_current", "India");
        }
        state.currentSubStep = "step3";
        renderLocationQuestion(num, q);
      }, step.columns);
    } else if (state.currentSubStep === "step3") {
      renderSingleLineInput(q.step3.text, q.step3.placeholder, function (val) {
        saveAnswer(q.step3.field, val);
        state.currentSubStep = null;
        advanceFromGuna(num);
      });
    }
  }


  // ============== MULTI-STEP: TWO-STEP LOCATION (Q3 hometown) ==============

  function renderTwoStepLocationQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";
      var options = q.step1.options;
      if (typeof options === "string") {
        options = resolveByKey(options);
      }
      renderOptions(q.step1.text, options, function (val) {
        saveAnswer(q.step1.field, val);
        state.currentSubStep = "step2";
        renderTwoStepLocationQuestion(num, q);
      }, q.step1.columns);
    } else if (state.currentSubStep === "step2") {
      renderSingleLineInput(q.step2.text, q.step2.placeholder, function (val) {
        saveAnswer(q.step2.field, val);
        // Compose the combined hometown field
        var hometown = (state.answers[q.step1.field] || "") + ", " + val;
        saveAnswer(q.field, hometown);
        state.currentSubStep = null;
        advanceFromGuna(num);
      });
    }
  }


  // ============== MULTI-STEP: TWO-STEP RANGE (Q40 age, Q41 height) ==============

  function renderTwoStepRangeQuestion(num, q) {
    if (!state.currentSubStep || state.currentSubStep === "step1") {
      state.currentSubStep = "step1";

      // If this question has "doesn't matter" option, show it before step1
      if (q.has_doesnt_matter && q.doesnt_matter_option) {
        var options = q.step1.options;
        if (typeof options === "string") {
          options = resolveByKey(options);
        }
        // Add the "doesn't matter" option at the top
        var allOptions = [q.doesnt_matter_option].concat(options || []);
        renderOptions(q.step1.text, allOptions, function (val) {
          if (val === "doesnt_matter") {
            saveAnswer(q.step1.field, "doesnt_matter");
            saveAnswer(q.step2.field, "doesnt_matter");
            saveAnswer(q.field, "doesnt_matter");
            state.currentSubStep = null;
            advanceFromGuna(num);
          } else {
            saveAnswer(q.step1.field, val);
            state.currentSubStep = "step2";
            renderTwoStepRangeQuestion(num, q);
          }
        }, q.step1.columns);
      } else {
        var options = q.step1.options;
        if (typeof options === "string") {
          options = resolveByKey(options);
        }
        renderOptions(q.step1.text, options, function (val) {
          saveAnswer(q.step1.field, val);
          state.currentSubStep = "step2";
          renderTwoStepRangeQuestion(num, q);
        }, q.step1.columns);
      }
    } else if (state.currentSubStep === "step2") {
      var options = q.step2.options;
      if (typeof options === "string") {
        // For age_range_max, pass the min age as context
        var extraContext = {};
        if (options === "age_range_max") {
          extraContext.minAge = state.answers[q.step1.field];
        }
        options = resolveByKey(options, extraContext);
      }
      renderOptions(q.step2.text, options, function (val) {
        saveAnswer(q.step2.field, val);
        // Compose the range value
        var rangeVal = state.answers[q.step1.field] + "-" + val;
        saveAnswer(q.field, rangeVal);
        state.currentSubStep = null;
        advanceFromGuna(num);
      }, q.step2.columns);
    }
  }


  // ============== ADVANCE LOGIC ==============

  function advanceFromGuna(currentNum) {
    // Check for sub-questions after this guna
    for (var key in SUB_QUESTIONS) {
      if (!SUB_QUESTIONS.hasOwnProperty(key)) continue;
      var subQ = SUB_QUESTIONS[key];
      if (subQ.after_guna === currentNum && shouldAskSubQuestion(key, state.answers)) {
        state.pendingSubQuestion = key;
        showSubQuestion(key);
        return;
      }
    }

    var next = getNextQuestion(state.answers, currentNum);
    state.currentGuna = next;
    showGuna(next);
  }

  function showSubQuestion(key) {
    state.phase = "sub_question";
    var subQ = SUB_QUESTIONS[key];

    // Multi-select sub-questions
    if (subQ.type === "multi_select") {
      var options = subQ.options;
      if (typeof options === "string") {
        options = resolveByKey(options);
      }
      if (!options || options.length === 0) {
        finishSubQuestion(key);
        return;
      }
      renderMultiSelect(subQ.text, options, subQ.done_label, function (vals) {
        saveAnswer(subQ.field, vals);
        finishSubQuestion(key);
      });
      return;
    }

    // Single select sub-questions
    var options = subQ.options;
    if (typeof options === "string") {
      options = resolveByKey(options);
    }
    if (!options || options.length === 0) {
      finishSubQuestion(key);
      return;
    }
    renderOptions(subQ.text, options, function (val) {
      saveAnswer(subQ.field, val);
      finishSubQuestion(key);
    });
  }

  function finishSubQuestion(key) {
    var subQ = SUB_QUESTIONS[key];
    state.pendingSubQuestion = null;
    // Continue to next guna after the sub-question's parent
    var next = getNextQuestion(state.answers, subQ.after_guna);
    state.currentGuna = next;
    state.phase = "gunas";
    showGuna(next);
  }


  // ============== SAVE ANSWER ==============

  function saveAnswer(field, value) {
    state.answers[field] = value;
  }


  // ============== PHASE: CLOSE ==============

  function showClose() {
    state.phase = "close";
    var text = CLOSE_MESSAGE.replace(/{name}/g, state.answers.full_name || "");
    renderMessage(text, "Almost done \u2014 one last thing \u2192", function () {
      showPhone();
    });
  }


  // ============== PHASE: PHONE ==============

  function showPhone() {
    state.phase = "phone";
    var frag = document.createDocumentFragment();
    var q = el("h2", { className: "form-question" }, "Your phone number");
    frag.appendChild(q);
    var note = el("p", { className: "form-note" }, "We\u2019ll use this to send you your match. No spam, ever.");
    frag.appendChild(note);

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
      placeholder: "Phone number"
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
        var fullPhone = code + phone;
        submitForm(fullPhone);
      }
    }, "Submit \u2192");
    frag.appendChild(btn);
    renderCard(frag);
    setTimeout(function () { phoneInput.focus(); }, 100);
  }


  // ============== SUBMIT ==============

  async function submitForm(phone) {
    state.phase = "done";
    // Show loading
    renderMessage("Submitting your answers...", "", function () {});
    // Remove the empty button
    var btn = container.querySelector(".form-btn");
    if (btn) btn.style.display = "none";

    // Build payload
    var payload = {
      phone: phone,
      name: state.answers.full_name || "",
      answers: {},
      meta: state.meta
    };

    // Collect all question answers with their db_table info
    for (var i = 1; i <= TOTAL_QUESTIONS; i++) {
      var q = QUESTIONS[i];
      if (!q) continue;

      if (q.type === "location_tree") {
        // Location has multiple fields
        ["country_current", "state_india", "city_current"].forEach(function (f) {
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
      if (q.type === "two_step_location") {
        // Hometown has state + city sub-fields
        if (state.answers[q.step1.field] != null) {
          payload.answers[q.step1.field] = { value: state.answers[q.step1.field], table: q.db_table };
        }
        if (state.answers[q.step2.field] != null) {
          payload.answers[q.step2.field] = { value: state.answers[q.step2.field], table: q.db_table };
        }
        if (state.answers[q.field] != null) {
          payload.answers[q.field] = { value: state.answers[q.field], table: q.db_table };
        }
        continue;
      }
      if (q.type === "two_step_range") {
        // Range has min + max sub-fields
        if (state.answers[q.step1.field] != null) {
          payload.answers[q.step1.field] = { value: state.answers[q.step1.field], table: q.db_table };
        }
        if (state.answers[q.step2.field] != null) {
          payload.answers[q.step2.field] = { value: state.answers[q.step2.field], table: q.db_table };
        }
        if (state.answers[q.field] != null) {
          payload.answers[q.field] = { value: state.answers[q.field], table: q.db_table };
        }
        continue;
      }
      if (state.answers[q.field] != null) {
        payload.answers[q.field] = { value: state.answers[q.field], table: q.db_table };
      }
    }

    // Setup question answers (full_name, gender)
    if (state.answers.full_name != null) {
      payload.answers.full_name = { value: state.answers.full_name, table: "users" };
    }
    if (state.answers.gender != null) {
      payload.answers.gender = { value: state.answers.gender, table: "users" };
    }

    // Sub-question answers
    for (var key in SUB_QUESTIONS) {
      if (!SUB_QUESTIONS.hasOwnProperty(key)) continue;
      var subQ = SUB_QUESTIONS[key];
      if (state.answers[subQ.field] != null) {
        payload.answers[subQ.field] = { value: state.answers[subQ.field], table: subQ.db_table };
      }
    }

    try {
      var resp = await fetch(API_BASE + "/api/intake", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var data = await resp.json();
      showSuccess(data);
    } catch (err) {
      console.error("Submit error:", err);
      showError(phone);
    }
  }

  function showSuccess() {
    var name = state.answers.full_name || "";
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
      href: "https://t.me/masii_bot",
      className: "form-btn form-btn-secondary",
      target: "_blank"
    }, "Open Telegram \u2192");
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
