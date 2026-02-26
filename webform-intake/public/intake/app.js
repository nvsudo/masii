const STORAGE_KEY = 'jodi_intake_form_v1';

const SECTION_ICONS = {
  A: '🪪',
  B: '🧭',
  C: '🪔',
  D: '🎓',
  E: '🔒',
  F: '🏡',
  G: '🌿',
  H: '🎯',
  I: '💞',
  J: '⚡'
};

const NON_SCHEMA_KEYS = new Set([
  'whatsapp_country_code',
  'whatsapp_number',
  'first_name'
]);

const COUNTRY_OPTIONS = [
  'India',
  'UAE',
  'USA',
  'UK',
  'Canada',
  'Australia',
  'Singapore',
  'Germany',
  'Other'
];

const INDIA_STATES_UT = [
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chhattisgarh',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
  'Andaman and Nicobar Islands',
  'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu',
  'Delhi',
  'Jammu and Kashmir',
  'Ladakh',
  'Lakshadweep',
  'Puducherry'
];

const INDIAN_CITIES = [
  'Mumbai',
  'Delhi',
  'Bengaluru',
  'Hyderabad',
  'Ahmedabad',
  'Chennai',
  'Kolkata',
  'Pune',
  'Jaipur',
  'Surat',
  'Lucknow',
  'Kanpur',
  'Nagpur',
  'Indore',
  'Thane',
  'Bhopal',
  'Visakhapatnam',
  'Pimpri-Chinchwad',
  'Patna',
  'Vadodara',
  'Ghaziabad',
  'Ludhiana',
  'Agra',
  'Nashik',
  'Faridabad',
  'Meerut',
  'Rajkot',
  'Kalyan-Dombivli',
  'Vasai-Virar',
  'Varanasi',
  'Srinagar',
  'Aurangabad',
  'Dhanbad',
  'Amritsar',
  'Navi Mumbai',
  'Allahabad',
  'Howrah',
  'Ranchi',
  'Gwalior',
  'Jabalpur',
  'Coimbatore',
  'Vijayawada',
  'Jodhpur',
  'Madurai',
  'Raipur',
  'Kota',
  'Guwahati',
  'Chandigarh',
  'Solapur',
  'Hubli-Dharwad',
  'Bareilly',
  'Mysuru',
  'Tiruchirappalli',
  'Tiruppur',
  'Gurugram',
  'Aligarh',
  'Jalandhar',
  'Bhubaneswar',
  'Salem',
  'Warangal',
  'Guntur',
  'Bhiwandi',
  'Saharanpur',
  'Gorakhpur',
  'Bikaner',
  'Amravati',
  'Noida',
  'Jamshedpur',
  'Bhilai',
  'Cuttack',
  'Firozabad',
  'Kochi',
  'Bhavnagar',
  'Dehradun',
  'Durgapur',
  'Asansol',
  'Nanded',
  'Kolhapur',
  'Ajmer',
  'Gulbarga',
  'Jamnagar',
  'Ujjain',
  'Loni',
  'Siliguri',
  'Jhansi',
  'Ulhasnagar',
  'Nellore',
  'Jammu',
  'Sangli-Miraj-Kupwad',
  'Belagavi',
  'Mangaluru',
  'Erode',
  'Ambattur',
  'Tirunelveli',
  'Malegaon',
  'Gaya',
  'Jalgaon',
  'Udaipur',
  'Maheshtala'
];

const GLOBAL_CITIES = [
  'Dubai',
  'Abu Dhabi',
  'Doha',
  'Riyadh',
  'Jeddah',
  'Muscat',
  'Singapore',
  'London',
  'Manchester',
  'Birmingham',
  'Leeds',
  'Glasgow',
  'Edinburgh',
  'New York',
  'San Francisco',
  'Los Angeles',
  'Chicago',
  'Houston',
  'Toronto',
  'Vancouver',
  'Sydney',
  'Melbourne',
  'Perth',
  'Auckland',
  'Kuala Lumpur',
  'Johannesburg',
  'Paris',
  'Berlin',
  'Amsterdam',
  'Zurich'
];

const CITY_OPTIONS = [...new Set([...INDIAN_CITIES, ...GLOBAL_CITIES])].sort();

const WHATSAPP_CODES = [
  '+91',
  '+971',
  '+1',
  '+44',
  '+61',
  '+65',
  '+49',
  '+974',
  '+966'
];

const SECT_OPTIONS = {
  Hindu: [
    'Shaivite',
    'Vaishnavite',
    'Shakta',
    'Smarta',
    'Arya Samaj',
    'Lingayat',
    'Other',
    'Prefer not to say'
  ],
  Muslim: ['Sunni', 'Shia', 'Sufi', 'Ahmadiyya', 'Other', 'Prefer not to say'],
  Christian: [
    'Catholic',
    'Protestant',
    'Orthodox',
    'Evangelical',
    'Other',
    'Prefer not to say'
  ],
  Sikh: ['Amritdhari', 'Keshdhari', 'Sehajdhari', 'Nihang', 'Other', 'Prefer not to say'],
  Jain: ['Digambar', 'Shwetambar', 'Sthanakvasi', 'Terapanthi', 'Other', 'Prefer not to say'],
  Buddhist: ['Theravada', 'Mahayana', 'Vajrayana', 'Navayana', 'Other', 'Prefer not to say']
};

const CASTE_OPTIONS = {
  Hindu: [
    'Brahmin',
    'Kshatriya',
    'Vaishya',
    'SC',
    'ST',
    'OBC',
    'Kayastha',
    'Other',
    'Prefer not to say'
  ],
  Jain: [
    'Digambar',
    'Shwetambar',
    'Sthanakvasi',
    'Terapanthi',
    'General',
    'Other',
    'Prefer not to say'
  ],
  Sikh: ['Jat', 'Khatri', 'Ramgarhia', 'Arora', 'Mazhabi', 'General', 'Other', 'Prefer not to say'],
  Buddhist: ['General', 'Navayana', 'Theravada', 'Mahayana', 'Other', 'Prefer not to say']
};

const CASTE_ELIGIBLE_RELIGIONS = new Set(['Hindu', 'Jain', 'Sikh', 'Buddhist']);
const MANGLIK_ELIGIBLE_RELIGIONS = new Set(['Hindu', 'Jain']);

const SENSITIVE_FIELDS = new Set([
  'religion',
  'sect_denomination',
  'caste_community',
  'sub_caste',
  'manglik_status',
  'complexion',
  'disability_status',
  'annual_income',
  'income_currency',
  'net_worth_range',
  'property_ownership',
  'financial_dependents',
  'pref_complexion',
  'pref_income_range',
  'pref_disability_ok'
]);

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
];

let schema = null;
let cachedScreens = [];
let autoAdvanceTimer = null;

const state = {
  started: false,
  screenIndex: 0,
  answers: {},
  optionCursor: 0,
  openWhyField: null,
  completionError: '',
  submitted: false,
  submitting: false
};

async function boot() {
  try {
    const response = await fetch('/intake/schema.json');
    schema = await response.json();
  } catch (error) {
    document.getElementById('app').innerHTML = `
      <div class="flow-wrap">
        <section class="card">
          <h1 class="question-title">Could not load the form schema</h1>
          <p class="lead">Please make sure <code>schema.json</code> is available with the site files.</p>
        </section>
      </div>
    `;
    return;
  }

  hydrateState();
  render();
  document.addEventListener('keydown', onKeyDown);
}

function hydrateState() {
  const raw = sessionStorage.getItem(STORAGE_KEY);
  if (!raw) {
    state.answers.whatsapp_country_code = '+91';
    return;
  }

  try {
    const parsed = JSON.parse(raw);
    state.started = Boolean(parsed.started);
    state.screenIndex = Number.isInteger(parsed.screenIndex) ? parsed.screenIndex : 0;
    state.answers = parsed.answers && typeof parsed.answers === 'object' ? parsed.answers : {};
    state.optionCursor = Number.isInteger(parsed.optionCursor) ? parsed.optionCursor : 0;
    state.openWhyField = typeof parsed.openWhyField === 'string' ? parsed.openWhyField : null;
    state.submitted = Boolean(parsed.submitted);
    state.submitting = Boolean(parsed.submitting);
    if (!state.answers.whatsapp_country_code) {
      state.answers.whatsapp_country_code = '+91';
    }
  } catch (_error) {
    state.answers.whatsapp_country_code = '+91';
  }
}

function saveState() {
  sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      started: state.started,
      screenIndex: state.screenIndex,
      answers: state.answers,
      optionCursor: state.optionCursor,
      openWhyField: state.openWhyField,
      submitted: state.submitted,
      submitting: state.submitting
    })
  );
}

function getVisibleFields() {
  return schema.fields.filter((field) => shouldShowField(field, state.answers));
}

function shouldShowField(field, answers) {
  const residency = normalizeValue(answers.residency_type);
  const religion = answers.religion;

  switch (field.field_name) {
    case 'children_existing':
      return Boolean(answers.marital_status) && answers.marital_status !== 'Never married';
    case 'country_current':
      return Boolean(answers.residency_type) && residency !== normalizeValue('Indian citizen (in India)');
    case 'state_india':
      return residency === normalizeValue('Indian citizen (in India)');
    case 'settling_country': {
      if (!answers.residency_type) return false;
      const compact = normalizeValue(answers.residency_type).replace(/\s*\/\s*/g, '/');
      return compact === 'nri' || compact === 'oci/pio';
    }
    case 'sect_denomination':
      return Boolean(religion);
    case 'caste_community':
      return CASTE_ELIGIBLE_RELIGIONS.has(religion);
    case 'sub_caste':
      return Boolean(answers.caste_community);
    case 'manglik_status':
      return MANGLIK_ELIGIBLE_RELIGIONS.has(religion);
    case 'income_currency':
      return Boolean(answers.residency_type) && residency !== normalizeValue('Indian citizen (in India)');
    case 'children_timeline':
      return Boolean(answers.children_intent) && answers.children_intent !== 'Definitely not';
    default:
      return true;
  }
}

function pruneHiddenAnswers(visibleFields) {
  const allowedFields = new Set(visibleFields.map((field) => field.field_name));
  for (const key of Object.keys(state.answers)) {
    if (allowedFields.has(key) || NON_SCHEMA_KEYS.has(key)) {
      continue;
    }
    delete state.answers[key];
  }
}

function buildScreens(visibleFields) {
  const bySection = new Map();
  for (const field of visibleFields) {
    if (!bySection.has(field.section_code)) {
      bySection.set(field.section_code, []);
    }
    bySection.get(field.section_code).push(field);
  }

  const screens = [];
  for (const section of schema.sections) {
    const sectionFields = bySection.get(section.code);
    if (!sectionFields || !sectionFields.length) continue;
    screens.push({ type: 'section', section });
    sectionFields.forEach((field) => screens.push({ type: 'question', field }));
  }
  screens.push({ type: 'completion' });
  return screens;
}

function getProgress(visibleFields, currentScreen) {
  const total = visibleFields.length;
  if (!total) {
    return { percent: 0, detail: '0 / 0' };
  }

  const answered = visibleFields.filter((field) => hasValue(field.field_name)).length;
  let percent = Math.round((answered / total) * 100);

  if (currentScreen && currentScreen.type !== 'completion') {
    percent = Math.min(percent, 99);
  }

  if (currentScreen && currentScreen.type === 'completion') {
    percent = 100;
  }

  return {
    percent,
    detail: `${Math.min(answered, total)} / ${total}`
  };
}

function hasValue(fieldName) {
  if (isOptionalField(fieldName)) {
    return Object.prototype.hasOwnProperty.call(state.answers, fieldName);
  }

  const value = state.answers[fieldName];
  if (value === undefined || value === null) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') {
    return Boolean(value.day && value.month && value.year);
  }
  return String(value).trim().length > 0;
}

function render() {
  if (!schema) return;

  const app = document.getElementById('app');

  if (!state.started) {
    app.innerHTML = renderShell({
      showProgress: false,
      progressPercent: 0,
      progressDetail: '0 / 77',
      canGoBack: false,
      body: renderWelcome()
    });
    wireCommonEvents();
    wireWelcomeEvents();
    saveState();
    return;
  }

  const visibleFields = getVisibleFields();
  pruneHiddenAnswers(visibleFields);

  cachedScreens = buildScreens(visibleFields);

  if (state.screenIndex >= cachedScreens.length) {
    state.screenIndex = cachedScreens.length - 1;
  }
  if (state.screenIndex < 0) {
    state.screenIndex = 0;
  }

  const currentScreen = cachedScreens[state.screenIndex];
  const progress = getProgress(visibleFields, currentScreen);

  const privateCard =
    currentScreen.type === 'question' &&
    (currentScreen.field.filter_type === 'Private' || currentScreen.field.section_code === 'E');

  let body = '';
  if (currentScreen.type === 'section') {
    body = renderSectionIntro(currentScreen.section);
  } else if (currentScreen.type === 'question') {
    body = renderQuestion(currentScreen.field);
  } else {
    body = renderCompletion();
  }

  app.innerHTML = renderShell({
    showProgress: true,
    progressPercent: progress.percent,
    progressDetail: progress.detail,
    canGoBack: state.screenIndex > 0,
    body,
    privateCard
  });

  wireCommonEvents();

  if (currentScreen.type === 'section') {
    wireSectionEvents();
  }
  if (currentScreen.type === 'question') {
    wireQuestionEvents(currentScreen.field);
  }
  if (currentScreen.type === 'completion') {
    wireCompletionEvents();
  }

  updateOptionCursorVisual();
  saveState();
}

function renderShell({ showProgress, progressPercent, progressDetail, canGoBack, body, privateCard = false }) {
  return `
    <div class="flow-wrap">
      <div class="progress-wrap" ${showProgress ? '' : 'style="visibility:hidden"'}>
        <div class="progress-track">
          <div class="progress-fill" style="width:${progressPercent}%"></div>
        </div>
        <div class="progress-text">${escapeHtml(String(progressPercent))}%</div>
      </div>
      <section class="card ${privateCard ? 'private-card' : ''}">
        <div class="card-header">
          ${
            canGoBack
              ? '<button class="back-btn" id="back-btn" type="button">← Back</button>'
              : '<span></span>'
          }
          <span class="step-kicker">${escapeHtml(progressDetail)}</span>
        </div>
        ${body}
      </section>
    </div>
  `;
}

function renderWelcome() {
  return `
    <h1 class="logo">Jodi</h1>
    <h2 class="tagline">Let's find your person.</h2>
    <p class="lead">Answer a few questions - it takes about 8 minutes. No sign-up needed.</p>
    <button class="primary-btn" id="start-btn" type="button">Let's Begin →</button>
    <p class="footer-note">Your answers are private and encrypted. We'll never share your data.</p>
  `;
}

function renderSectionIntro(section) {
  const icon = SECTION_ICONS[section.code] || '✨';
  return `
    <div class="meta-row">
      <span class="section-icon" aria-hidden="true">${icon}</span>
      <span class="filter-chip">Section ${escapeHtml(section.code)}</span>
    </div>
    <h1 class="section-title">${escapeHtml(section.title)}</h1>
    <p class="section-splash">${escapeHtml(section.description)}</p>
    <button class="primary-btn" id="section-continue" type="button">Continue →</button>
    <p class="helper-row">Press Enter to continue</p>
  `;
}

function renderQuestion(field) {
  const label = field.label;
  const type = field.question_type;
  const options = getOptions(field);
  const value = state.answers[field.field_name];
  const optional = isOptionalField(field.field_name);
  const chip = field.filter_type || 'Field';
  const showWhy = Boolean(field.why_this_matters);
  const showPrivateCopy = field.filter_type === 'Private';
  const hasSensitiveContext = SENSITIVE_FIELDS.has(field.field_name) || showPrivateCopy;

  let inputBlock = '';

  if (type === 'single_select') {
    inputBlock = `
      <div class="options-grid" id="options-grid">
        ${options
          .map((option, index) => {
            const selected = value === option;
            return `
              <button
                class="option-btn ${selected ? 'is-selected' : ''}"
                type="button"
                data-option-index="${index}"
              >
                <span class="option-index">${index + 1}</span>
                <span>${escapeHtml(option)}</span>
                <span class="option-check">✓</span>
              </button>
            `;
          })
          .join('')}
      </div>
    `;
  }

  if (type === 'multi_select') {
    const selected = Array.isArray(value) ? value : [];
    inputBlock = `
      <div class="options-grid" id="options-grid">
        ${options
          .map((option, index) => {
            const isOn = selected.includes(option);
            return `
              <button
                class="option-btn ${isOn ? 'is-selected' : ''}"
                aria-pressed="${String(isOn)}"
                type="button"
                data-option-index="${index}"
              >
                <span class="option-index">${index + 1}</span>
                <span>${escapeHtml(option)}</span>
                <span class="option-check">✓</span>
              </button>
            `;
          })
          .join('')}
      </div>
      <button
        class="primary-btn"
        id="multi-next"
        type="button"
        ${selected.length ? '' : 'disabled'}
      >
        Done / Next →
      </button>
    `;
  }

  if (type === 'city_autocomplete') {
    const cityValue = typeof value === 'string' ? value : '';
    const suggestions = getCitySuggestions(cityValue);
    inputBlock = `
      <div class="form-row">
        <input
          id="city-input"
          class="field-input"
          type="text"
          value="${escapeHtml(cityValue)}"
          placeholder="Start typing your city"
          autocomplete="off"
        />
        <div class="autocomplete-list" id="city-suggestions">
          ${suggestions
            .map(
              (city) =>
                `<button class="autocomplete-item" data-city="${escapeHtml(city)}" type="button">${escapeHtml(city)}</button>`
            )
            .join('')}
        </div>
        <button class="primary-btn" id="city-next" type="button" ${cityValue.trim() ? '' : 'disabled'}>Next →</button>
      </div>
    `;
  }

  if (type === 'date_of_birth') {
    const current = normalizeDateValue(value);

    const years = [];
    const thisYear = new Date().getFullYear();
    for (let year = thisYear - 18; year >= 1945; year -= 1) {
      years.push(year);
    }

    inputBlock = `
      <div class="date-grid">
        <select class="field-select" id="dob-day">
          <option value="">Day</option>
          ${Array.from({ length: 31 }, (_, idx) => idx + 1)
            .map(
              (day) =>
                `<option value="${day}" ${String(current.day) === String(day) ? 'selected' : ''}>${day}</option>`
            )
            .join('')}
        </select>
        <select class="field-select" id="dob-month">
          <option value="">Month</option>
          ${MONTHS.map(
            (month, idx) =>
              `<option value="${idx + 1}" ${String(current.month) === String(idx + 1) ? 'selected' : ''}>${escapeHtml(
                month
              )}</option>`
          ).join('')}
        </select>
        <select class="field-select" id="dob-year">
          <option value="">Year</option>
          ${years
            .map(
              (year) =>
                `<option value="${year}" ${String(current.year) === String(year) ? 'selected' : ''}>${year}</option>`
            )
            .join('')}
        </select>
      </div>
      <button class="primary-btn" id="dob-next" type="button" ${hasValue(field.field_name) ? '' : 'disabled'}>Next →</button>
    `;
  }

  if (type === 'text') {
    const textValue = typeof value === 'string' ? value : '';
    inputBlock = `
      <div class="form-row">
        <input
          id="text-input"
          class="field-input"
          type="text"
          value="${escapeHtml(textValue)}"
          placeholder="e.g., Agarwal, Iyer, Jat..."
          autocomplete="off"
        />
        <button class="primary-btn" id="text-next" type="button" ${optional || textValue.trim() ? '' : 'disabled'}>
          ${optional ? 'Skip / Next →' : 'Next →'}
        </button>
      </div>
    `;
  }

  return `
    <div class="meta-row">
      <span class="filter-chip">${escapeHtml(chip)}</span>
      ${showPrivateCopy ? '<span class="filter-chip">🔒 Private</span>' : '<span></span>'}
    </div>
    <h1 class="question-title">${escapeHtml(label)}</h1>
    ${
      showPrivateCopy
        ? "<p class=\"private-note\">This won't be shown to matches. It helps us find better-quality matches for you.</p>"
        : ''
    }
    ${
      showWhy
        ? `
          <div class="why-wrap">
            <button class="inline-btn" id="why-toggle" type="button">Why we ask</button>
            ${
              state.openWhyField === field.field_name
                ? `<div class="why-popover">${escapeHtml(field.why_this_matters)}</div>`
                : ''
            }
          </div>
        `
        : ''
    }
    ${inputBlock}
    <p class="helper-row">
      ${hasSensitiveContext ? 'We ask this to improve match quality and avoid mismatches.' : ''}
      <span>Use number keys or arrow keys to select. Press Enter to continue.</span>
    </p>
  `;
}

function renderCompletion() {
  const countryCode = state.answers.whatsapp_country_code || '+91';
  const number = state.answers.whatsapp_number || '';
  const firstName = state.answers.first_name || '';

  return `
    <h1 class="question-title">You're all set! 🎉</h1>
    <p class="lead">We've captured what matters to you. When we find someone who's an 87%+ match, we'll introduce you - for free.</p>

    <div class="form-row">
      <label for="wa-number" class="step-kicker">Your WhatsApp number</label>
      <div class="whatsapp-row">
        <select id="wa-code" class="field-select">
          ${WHATSAPP_CODES.map(
            (code) => `<option value="${code}" ${countryCode === code ? 'selected' : ''}>${code}</option>`
          ).join('')}
        </select>
        <input
          id="wa-number"
          class="field-input"
          type="tel"
          inputmode="numeric"
          value="${escapeHtml(String(number))}"
          placeholder="Phone number"
          autocomplete="tel"
        />
      </div>

      <label for="first-name" class="step-kicker">Your first name</label>
      <input
        id="first-name"
        class="field-input"
        type="text"
        value="${escapeHtml(String(firstName))}"
        placeholder="First name"
        autocomplete="given-name"
      />

      <button class="primary-btn" id="final-submit" type="button" ${state.submitting ? 'disabled' : ''}>
        ${state.submitting ? 'Saving...' : 'Notify me on WhatsApp →'}
      </button>
      ${state.completionError ? `<p class="error-text">${escapeHtml(state.completionError)}</p>` : ''}
      ${state.submitted ? '<p class="success-note">Done. We will only reach out for genuine matches.</p>' : ''}
    </div>

    <p class="footer-note">We'll only message you when there's a genuine match. No spam, ever.</p>
  `;
}

function wireCommonEvents() {
  const backButton = document.getElementById('back-btn');
  if (backButton) {
    backButton.addEventListener('click', () => {
      if (state.screenIndex > 0) {
        state.screenIndex -= 1;
        state.optionCursor = 0;
        render();
      }
    });
  }
}

function wireWelcomeEvents() {
  const startButton = document.getElementById('start-btn');
  if (!startButton) return;
  startButton.addEventListener('click', startFlow);
}

function startFlow() {
  state.started = true;
  state.screenIndex = 0;
  state.optionCursor = 0;
  state.submitted = false;
  state.completionError = '';
  render();
}

function wireSectionEvents() {
  const continueButton = document.getElementById('section-continue');
  if (!continueButton) return;
  continueButton.addEventListener('click', () => {
    nextScreen();
  });
}

function wireQuestionEvents(field) {
  const whyButton = document.getElementById('why-toggle');
  if (whyButton) {
    whyButton.addEventListener('click', () => {
      state.openWhyField = state.openWhyField === field.field_name ? null : field.field_name;
      render();
    });
  }

  if (field.question_type === 'single_select') {
    const optionButtons = Array.from(document.querySelectorAll('.option-btn[data-option-index]'));
    optionButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const index = Number(button.dataset.optionIndex);
        selectSingleOption(field, index, true);
      });
    });
    return;
  }

  if (field.question_type === 'multi_select') {
    const optionButtons = Array.from(document.querySelectorAll('.option-btn[data-option-index]'));
    optionButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const index = Number(button.dataset.optionIndex);
        toggleMultiOption(field, index);
      });
    });

    const nextButton = document.getElementById('multi-next');
    if (nextButton) {
      nextButton.addEventListener('click', () => {
        if (hasValue(field.field_name)) {
          nextScreen();
        }
      });
    }
    return;
  }

  if (field.question_type === 'city_autocomplete') {
    const cityInput = document.getElementById('city-input');
    const cityNext = document.getElementById('city-next');
    const suggestionContainer = document.getElementById('city-suggestions');

    const syncSuggestions = () => {
      const inputValue = cityInput.value.trim();
      state.answers[field.field_name] = inputValue;
      if (cityNext) {
        cityNext.disabled = !inputValue;
      }
      const suggestions = getCitySuggestions(inputValue);
      suggestionContainer.innerHTML = suggestions
        .map(
          (city) =>
            `<button class="autocomplete-item" data-city="${escapeHtml(city)}" type="button">${escapeHtml(city)}</button>`
        )
        .join('');
      suggestionContainer.querySelectorAll('[data-city]').forEach((node) => {
        node.addEventListener('click', () => {
          const city = node.dataset.city || '';
          cityInput.value = city;
          state.answers[field.field_name] = city;
          if (cityNext) cityNext.disabled = !city;
          saveState();
        });
      });
      saveState();
    };

    if (cityInput) {
      cityInput.addEventListener('input', syncSuggestions);
    }

    suggestionContainer.querySelectorAll('[data-city]').forEach((node) => {
      node.addEventListener('click', () => {
        const city = node.dataset.city || '';
        cityInput.value = city;
        state.answers[field.field_name] = city;
        if (cityNext) cityNext.disabled = !city;
        saveState();
      });
    });

    if (cityNext) {
      cityNext.addEventListener('click', () => {
        if (hasValue(field.field_name)) {
          nextScreen();
        }
      });
    }
    return;
  }

  if (field.question_type === 'date_of_birth') {
    const day = document.getElementById('dob-day');
    const month = document.getElementById('dob-month');
    const year = document.getElementById('dob-year');
    const nextButton = document.getElementById('dob-next');

    const syncDate = () => {
      const dateObj = {
        day: day.value,
        month: month.value,
        year: year.value
      };
      state.answers[field.field_name] = dateObj;
      if (nextButton) {
        nextButton.disabled = !(dateObj.day && dateObj.month && dateObj.year);
      }
      saveState();
    };

    [day, month, year].forEach((node) => {
      node.addEventListener('change', syncDate);
    });

    if (nextButton) {
      nextButton.addEventListener('click', () => {
        if (hasValue(field.field_name)) {
          nextScreen();
        }
      });
    }
    return;
  }

  if (field.question_type === 'text') {
    const input = document.getElementById('text-input');
    const nextButton = document.getElementById('text-next');
    const optional = isOptionalField(field.field_name);
    if (input) {
      input.addEventListener('input', () => {
        state.answers[field.field_name] = input.value.trim();
        if (nextButton) {
          nextButton.disabled = !optional && !input.value.trim();
        }
        saveState();
      });
    }

    if (nextButton) {
      nextButton.addEventListener('click', () => {
        state.answers[field.field_name] = input ? input.value.trim() : '';
        if (optional || hasValue(field.field_name)) {
          nextScreen();
        }
      });
    }
  }
}

function wireCompletionEvents() {
  const codeSelect = document.getElementById('wa-code');
  const numberInput = document.getElementById('wa-number');
  const nameInput = document.getElementById('first-name');
  const submitButton = document.getElementById('final-submit');

  if (codeSelect) {
    codeSelect.addEventListener('change', () => {
      state.answers.whatsapp_country_code = codeSelect.value;
      saveState();
    });
  }

  if (numberInput) {
    numberInput.addEventListener('input', () => {
      state.answers.whatsapp_number = numberInput.value.trim();
      if (state.completionError) {
        state.completionError = '';
        render();
      }
      saveState();
    });
  }

  if (nameInput) {
    nameInput.addEventListener('input', () => {
      state.answers.first_name = nameInput.value.trim();
      if (state.completionError) {
        state.completionError = '';
        render();
      }
      saveState();
    });
  }

  if (submitButton) {
    submitButton.addEventListener('click', submitFinal);
  }
}

async function submitFinal() {
  const phoneRaw = String(state.answers.whatsapp_number || '').replace(/\s+/g, '');
  const nameRaw = String(state.answers.first_name || '').trim();

  if (!nameRaw) {
    state.completionError = 'Please add your first name.';
    render();
    return;
  }

  if (!/^\d{7,15}$/.test(phoneRaw)) {
    state.completionError = 'Please enter a valid WhatsApp number.';
    render();
    return;
  }

  const payload = { ...state.answers };

  // Keep final payload stable for API handoff later.
  if (payload.date_of_birth && typeof payload.date_of_birth === 'object') {
    const date = payload.date_of_birth;
    if (date.year && date.month && date.day) {
      const mm = String(date.month).padStart(2, '0');
      const dd = String(date.day).padStart(2, '0');
      payload.date_of_birth = `${date.year}-${mm}-${dd}`;
    }
  }

  console.log('Jodi intake payload:', payload);

  state.submitting = true;
  render();

  try {
    await fetch('/api/intake', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    console.warn('Could not POST intake payload to local API:', error);
  }

  state.submitting = false;
  state.submitted = true;
  state.completionError = '';
  saveState();
  sessionStorage.removeItem(STORAGE_KEY);
  render();
}

function nextScreen() {
  if (state.screenIndex < cachedScreens.length - 1) {
    state.screenIndex += 1;
    state.optionCursor = 0;
    state.openWhyField = null;
    render();
  }
}

function selectSingleOption(field, index, autoAdvance = false) {
  const options = getOptions(field);
  if (index < 0 || index >= options.length) return;

  const value = options[index];
  state.answers[field.field_name] = value;
  state.optionCursor = index;
  saveState();

  const selectedNode = document.querySelector(`.option-btn[data-option-index="${index}"]`);
  if (selectedNode) {
    document.querySelectorAll('.option-btn').forEach((btn) => btn.classList.remove('is-selected'));
    selectedNode.classList.add('is-selected');
  }

  if (!autoAdvance) {
    return;
  }

  if (autoAdvanceTimer) {
    clearTimeout(autoAdvanceTimer);
  }

  autoAdvanceTimer = setTimeout(() => {
    nextScreen();
  }, 400);
}

function toggleMultiOption(field, index) {
  const options = getOptions(field);
  if (index < 0 || index >= options.length) return;

  const value = options[index];
  const selected = Array.isArray(state.answers[field.field_name]) ? [...state.answers[field.field_name]] : [];

  const foundIndex = selected.indexOf(value);
  if (foundIndex >= 0) {
    selected.splice(foundIndex, 1);
  } else {
    selected.push(value);
  }

  state.answers[field.field_name] = selected;
  saveState();

  const button = document.querySelector(`.option-btn[data-option-index="${index}"]`);
  if (button) {
    const nowOn = selected.includes(value);
    button.classList.toggle('is-selected', nowOn);
    button.setAttribute('aria-pressed', String(nowOn));
  }

  const nextButton = document.getElementById('multi-next');
  if (nextButton) {
    nextButton.disabled = selected.length === 0;
  }
}

function getOptions(field) {
  switch (field.field_name) {
    case 'country_current':
      return COUNTRY_OPTIONS;
    case 'state_india':
    case 'hometown_state':
      return INDIA_STATES_UT;
    case 'languages_spoken': {
      const motherTongueField = schema.fields.find((item) => item.field_name === 'mother_tongue');
      const options = motherTongueField ? motherTongueField.options : [];
      return [...new Set(options.concat(['Other']))];
    }
    case 'sect_denomination': {
      const religion = state.answers.religion;
      return SECT_OPTIONS[religion] || ['None / Prefer not to say'];
    }
    case 'caste_community': {
      const religion = state.answers.religion;
      return CASTE_OPTIONS[religion] || ['General', 'Prefer not to say'];
    }
    case 'pref_age_range':
      return [
        'Same as me (±2yr)',
        'Younger (up to 5yr)',
        'Older (up to 5yr)',
        'Wide range OK',
        'No preference'
      ];
    default:
      return field.options.map((option) =>
        option
          .replace(/^\[Conditional dropdown.*?\]\s*/i, '')
          .replace(/^\[Conditional dropdown based on religion\]\s*/i, '')
          .replace(/^\[Min-Max slider\]\s*or\s*/i, '')
          .trim()
      );
  }
}

function getCitySuggestions(input) {
  const query = input.trim().toLowerCase();
  if (!query) {
    return CITY_OPTIONS.slice(0, 8);
  }
  return CITY_OPTIONS.filter((city) => city.toLowerCase().includes(query)).slice(0, 8);
}

function normalizeDateValue(value) {
  if (!value || typeof value !== 'object') {
    return { day: '', month: '', year: '' };
  }
  return {
    day: value.day || '',
    month: value.month || '',
    year: value.year || ''
  };
}

function normalizeValue(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

function onKeyDown(event) {
  if (!schema) return;

  const activeTag = document.activeElement ? document.activeElement.tagName : '';
  const isInputFocused = ['INPUT', 'SELECT', 'TEXTAREA'].includes(activeTag);

  if (!state.started) {
    if (event.key === 'Enter') {
      event.preventDefault();
      startFlow();
    }
    return;
  }

  const currentScreen = cachedScreens[state.screenIndex];
  if (!currentScreen) return;

  if (event.key === 'Escape' && state.openWhyField) {
    state.openWhyField = null;
    render();
    return;
  }

  if (currentScreen.type === 'section') {
    if (event.key === 'Enter') {
      event.preventDefault();
      nextScreen();
    }
    return;
  }

  if (currentScreen.type === 'completion') {
    if (event.key === 'Enter' && !isInputFocused) {
      event.preventDefault();
      submitFinal();
    }
    return;
  }

  const field = currentScreen.field;
  const options = getOptions(field);

  if (field.question_type === 'single_select') {
    const digitIndex = getDigitIndex(event.key, options.length);
    if (digitIndex !== null) {
      event.preventDefault();
      selectSingleOption(field, digitIndex, true);
      return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      event.preventDefault();
      state.optionCursor = (state.optionCursor + 1) % options.length;
      updateOptionCursorVisual();
      return;
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      event.preventDefault();
      state.optionCursor = (state.optionCursor - 1 + options.length) % options.length;
      updateOptionCursorVisual();
      return;
    }

    if (event.key === 'Enter') {
      event.preventDefault();
      selectSingleOption(field, state.optionCursor, true);
    }
    return;
  }

  if (field.question_type === 'multi_select') {
    const digitIndex = getDigitIndex(event.key, options.length);
    if (digitIndex !== null) {
      event.preventDefault();
      toggleMultiOption(field, digitIndex);
      return;
    }

    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
      event.preventDefault();
      state.optionCursor = (state.optionCursor + 1) % options.length;
      updateOptionCursorVisual();
      return;
    }

    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
      event.preventDefault();
      state.optionCursor = (state.optionCursor - 1 + options.length) % options.length;
      updateOptionCursorVisual();
      return;
    }

    if ((event.key === ' ' || event.key === 'Spacebar') && !isInputFocused) {
      event.preventDefault();
      toggleMultiOption(field, state.optionCursor);
      return;
    }

    if (event.key === 'Enter' && hasValue(field.field_name)) {
      event.preventDefault();
      nextScreen();
      return;
    }
  }

  if (isInputFocused && event.key === 'Enter') {
    if (field.question_type === 'text') {
      if (isOptionalField(field.field_name) && !Object.prototype.hasOwnProperty.call(state.answers, field.field_name)) {
        state.answers[field.field_name] = '';
      }
      if (isOptionalField(field.field_name) || hasValue(field.field_name)) {
        event.preventDefault();
        nextScreen();
      }
      return;
    }

    if (field.question_type === 'city_autocomplete' || field.question_type === 'date_of_birth') {
      if (hasValue(field.field_name)) {
        event.preventDefault();
        nextScreen();
      }
    }
  }
}

function getDigitIndex(key, optionCount) {
  if (/^[1-9]$/.test(key)) {
    const idx = Number(key) - 1;
    if (idx < optionCount) return idx;
  }
  if (key === '0' && optionCount >= 10) {
    return 9;
  }
  return null;
}

function isOptionalField(fieldName) {
  return fieldName === 'sub_caste';
}

function updateOptionCursorVisual() {
  const buttons = Array.from(document.querySelectorAll('.option-btn[data-option-index]'));
  if (!buttons.length) return;

  const maxIndex = buttons.length - 1;
  if (state.optionCursor > maxIndex) {
    state.optionCursor = 0;
  }

  buttons.forEach((button) => {
    const idx = Number(button.dataset.optionIndex);
    button.classList.toggle('is-cursor', idx === state.optionCursor);
  });
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

boot();
