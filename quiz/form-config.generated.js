/**
 * Masii Form Configuration — GENERATED
 * DO NOT EDIT. Source: masii-questions.yaml v3
 * Generated: 2026-03-09 17:22 | Questions: 81
 * Regenerate: python3 generate-form-config.py
 */
"use strict";

const META = Object.freeze({
  version: 3,
  updated: "2026-03",
  totalQuestions: 81,
  nameField: "preferred_name",
  complexionPolicy: "photo_only"
});

const SECTIONS = Object.freeze({
  setup: { label: "Setup", subtitle: "Intent, Name, Gender", transition: null },
  basics: { label: "Basics", subtitle: "Parichay", transition: "{name}, let's start simple. The stuff any masi would ask first." },
  background: { label: "Background", subtitle: "Dharam", transition: "{name}, I need to understand where you come from. Not to judge — to find someone who fits." },
  partner_bg: { label: "Partner Background", subtitle: "Partner Preferences", transition: "Now the other side — what matters to you in their background, {name}?" },
  education: { label: "Education & Career", subtitle: "Vidya", transition: "Work and education, {name}. What you do and what you studied." },
  family: { label: "Family", subtitle: "Parivar", transition: "Family. You know this is the part I care about most, {name}." },
  lifestyle: { label: "Lifestyle", subtitle: "Jeevan Shaili", transition: "How you live, {name}. The everyday stuff that makes or breaks it." },
  marriage: { label: "Marriage & Living", subtitle: "Shaadi", transition: "The big picture, {name}. What does married life actually look like for you?" },
  partner_physical: { label: "Partner Physical", subtitle: "Physical Preferences", transition: "A few preferences, {name}. Be honest — I don't judge." },
  household: { label: "Household & Expectations", subtitle: "Household", transition: "Real talk, {name}. Who cooks. Who cleans. How money works. No right answers — just honest ones." },
  sensitive: { label: "Sensitive", subtitle: "Traditional", transition: "A few questions that traditional matchmakers ask. If any don't apply, just say 'Prefer not to say.' Your answers are never shared — not even with your match." },
  personality: { label: "Personality", subtitle: "Who You Are", transition: "Last stretch, {name}. A few about the kind of person you are — not what you do, but how you are." }
});

// Convenience: transitions keyed by section name
const SECTION_TRANSITIONS = Object.freeze(
  Object.fromEntries(Object.entries(SECTIONS).filter(([k, v]) => v.transition).map(([k, v]) => [k, v.transition]))
);

const INTRO = {
  text: "This takes about 10 minutes.\n\nI'll ask about your life, your values, your\nfamily, and what you're looking for.\n\nBe honest — the better I know you,\nthe better the match.\n\nEverything stays between us.",
  button: "Let's go →"
};

const CLOSE_MESSAGE = "{name}, that's everything. You've been honest, and that's exactly what I need.\n\nI'm going to work on this. When I find someone worth your time — someone who actually fits — I'll tell you why I think so.\n\nSit tight. Good things take a little time.\n\n— Masii";

const ERROR_MESSAGES = {
  button_expected: "Just tap one of the options above.",
  sticker_during_buttons: "Save that energy — just pick an option for now.",
  invalid_input: "That doesn't look right. Please try again.",
  network_error: "Something went wrong on my end. Let me try that again."
};

const RESUME_PROMPT = "Hey {name}, we were getting through your profile — want to pick up where we left off?\n\nProgress: {section_name} • {current} of {total} questions";
const RESUME_BUTTONS = ["Resume", "Start over"];

// ═══ QUESTIONS (81) ═══

const QUESTIONS = [
  {
    id: "intent",
    section: "setup",
    field: "intent",
    dbTable: "meta",
    question: "Are you filling this for yourself or someone else?",
    type: "single_select",
    notes: "If 'proxy' → jump to proxy flow",
    options: [
    { label: "For myself", value: "self" },
    { label: "For someone else", value: "proxy" }
  ]
  },

  {
    id: "full_name",
    section: "setup",
    field: "full_name",
    dbTable: "users",
    question: "What's your full name?",
    type: "text_input",
    placeholder: "First and last name",
    notes: "For records only. Not used for personalization."
  },

  {
    id: "preferred_name",
    section: "setup",
    field: "preferred_name",
    dbTable: "users",
    question: "What should I call you?",
    type: "text_input",
    placeholder: "e.g. Nik, Priya, Ravi",
    notes: "Used as {name} throughout. Auto-fill first word of full_name."
  },

  {
    id: "gender",
    section: "setup",
    field: "gender",
    dbTable: "users",
    question: "Are you male or female?",
    type: "single_select",
    helperText: "More options coming soon — we see you.",
    gate: "hard",
    gateLogic: "Must be opposite gender. Male matches Female only.",
    notes: "Gates gendered question variants downstream.",
    options: [
    { label: "Male", value: "Male" },
    { label: "Female", value: "Female" }
  ]
  },

  {
    id: "date_of_birth",
    section: "basics",
    field: "date_of_birth",
    dbTable: "users",
    question: "When were you born?",
    type: "two_step_date",
    responseTemplate: "{age} — got it ✓",
    step1:     {
      text: "What year were you born?",
      field: "birth_year",
      columns: 3,
      options: "birth_years"
    },
    step2:     {
      text: "Which month?",
      field: "birth_month",
      columns: 2,
      options: [
    { label: "January", value: "1" },
    { label: "February", value: "2" },
    { label: "March", value: "3" },
    { label: "April", value: "4" },
    { label: "May", value: "5" },
    { label: "June", value: "6" },
    { label: "July", value: "7" },
    { label: "August", value: "8" },
    { label: "September", value: "9" },
    { label: "October", value: "10" },
    { label: "November", value: "11" },
    { label: "December", value: "12" }
  ]
    },
    scoring: {
      rule: "Age compared against partner's Q40 age range. Within range = 1.0.",
      note: "Q40 is a hard gate, so this score is redundant but included for completeness."
    }
  },

  {
    id: "current_location",
    section: "basics",
    field: "current_location",
    dbTable: "users",
    question: "Where do you live right now?",
    type: "location_tree",
    notes: "Sets _location_type and _location_country for downstream logic (income brackets, currency).",
    followUps: ["pref_current_location"],
    step1:     {
      text: "Where do you live right now?",
      field: "location_type",
      options: [
    { label: "India", value: "India" },
    { label: "Outside India", value: "Outside India" }
  ]
    },
    step3:     {
      text: "Which city?",
      field: "city_current",
      type: "text_input",
      placeholder: "e.g. Mumbai, Dubai, Toronto..."
    },
    step2India:     {
      text: "Which state?",
      field: "state_india",
      columns: 2,
      options: "states_india"
    },
    step2Abroad:     {
      text: "Which country?",
      field: "country_current",
      columns: 2,
      options: "countries"
    },
    scoring: {
      rule: "Matched against Q2-pref (hard gate). Pass gate = 1.0."
    }
  },

  {
    id: "pref_current_location",
    section: "basics",
    field: "pref_current_location",
    dbTable: "preferences",
    question: "Where should your partner currently live?",
    type: "single_select",
    gate: "hard",
    gateLogic: "Candidate's current location (Q2) must match stated preference. 'Anywhere' passes everyone. 'Specific countries' = candidate must be in selected list.",
    notes: "Immediately follows Q2.",
    options: [
    { label: "Same city as me", value: "Same city as me" },
    { label: "Same state as me", value: "Same state as me" },
    { label: "Same country as me", value: "Same country as me" },
    { label: "Anywhere", value: "Anywhere" },
    { label: "Specific countries...", value: "Specific countries", triggers: "pref_location_countries" }
  ]
  },

  {
    id: "raised_in",
    section: "basics",
    field: "raised_in",
    dbTable: "users",
    question: "Where did you grow up?",
    type: "location_tree",
    notes: "KEY CONTEXT NODE. raised_in_state drives downstream: caste list, language suggestions, diet defaults, income context.",
    followUps: ["pref_raised_in"],
    step1:     {
      text: "Where did you grow up?",
      field: "raised_in_type",
      options: [
    { label: "India", value: "India" },
    { label: "Outside India", value: "Outside India" }
  ]
    },
    step3:     {
      text: "Which city or town?",
      field: "raised_in_city",
      type: "text_input",
      placeholder: "e.g. Ahmedabad, Jaipur, Lucknow..."
    },
    step2India:     {
      text: "Which state?",
      field: "raised_in_state",
      columns: 2,
      options: "states_india_full"
    },
    step2Abroad:     {
      text: "Which country?",
      field: "raised_in_country",
      columns: 2,
      options: "countries"
    },
    scoring: {
      rule: "Matched against Q3-pref (hard gate). Pass gate = 1.0."
    }
  },

  {
    id: "pref_raised_in",
    section: "basics",
    field: "pref_raised_in",
    dbTable: "preferences",
    question: "Where should your partner have been raised?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Same country' + different country = eliminated. 'Same state' + different state = eliminated. 'Doesn't matter' passes everyone.",
    notes: "Options vary by user's location_type.",
    optionsConditional: {
  "if_outside_india": [
    {
      "label": "Same country as me",
      "value": "Same country as me"
    },
    {
      "label": "Raised abroad (any country)",
      "value": "Raised abroad (any country)"
    },
    {
      "label": "Raised in India is fine too",
      "value": "Raised in India is fine too"
    },
    {
      "label": "Doesn't matter",
      "value": "Doesn't matter"
    }
  ],
  "if_in_india": [
    {
      "label": "Same state",
      "value": "Same state"
    },
    {
      "label": "Nearby states",
      "value": "Nearby states"
    },
    {
      "label": "Any state in India",
      "value": "Any state in India"
    },
    {
      "label": "Abroad is fine too",
      "value": "Abroad is fine too"
    },
    {
      "label": "Doesn't matter",
      "value": "Doesn't matter"
    }
  ]
}
  },

  {
    id: "mother_tongue",
    section: "basics",
    field: "mother_tongue",
    dbTable: "users",
    question: "What is your mother tongue?",
    type: "single_select",
    stateContext: "Auto-suggest based on raised_in_state. E.g., Tamil Nadu → Tamil first.",
    notes: "Expanded from 16 to 21 languages.",
    columns: 3,
    options: [
    { label: "Hindi", value: "Hindi" },
    { label: "Gujarati", value: "Gujarati" },
    { label: "Marathi", value: "Marathi" },
    { label: "Tamil", value: "Tamil" },
    { label: "Telugu", value: "Telugu" },
    { label: "Kannada", value: "Kannada" },
    { label: "Malayalam", value: "Malayalam" },
    { label: "Bengali", value: "Bengali" },
    { label: "Punjabi", value: "Punjabi" },
    { label: "Urdu", value: "Urdu" },
    { label: "Odia", value: "Odia" },
    { label: "Assamese", value: "Assamese" },
    { label: "Sindhi", value: "Sindhi" },
    { label: "Konkani", value: "Konkani" },
    { label: "Tulu", value: "Tulu" },
    { label: "Rajasthani", value: "Rajasthani" },
    { label: "Bhojpuri", value: "Bhojpuri" },
    { label: "Maithili", value: "Maithili" },
    { label: "Dogri", value: "Dogri" },
    { label: "Kashmiri", value: "Kashmiri" },
    { label: "Other", value: "Other" }
  ],
    scoring: {
      rule: "Same mother tongue = 1.0. Different but share non-English language (from Q5) = 0.8. Only English in common = 0.5. No shared language = 0.0."
    }
  },

  {
    id: "languages_spoken",
    section: "basics",
    field: "languages_spoken",
    dbTable: "users",
    question: "What other languages do you speak?",
    type: "multi_select",
    doneLabel: "Done ✓",
    columns: 3,
    options: "languages_minus_mother_tongue",
    scoring: {
      rule: "Not scored independently. Feeds into mother_tongue scoring (shared language check)."
    }
  },

  {
    id: "marital_status",
    section: "basics",
    field: "marital_status",
    dbTable: "users",
    question: "What's your current marital status?",
    type: "single_select",
    gate: "hard",
    gateLogic: "Candidate's marital_status must be in partner's accepted list (Q6-pref).",
    followUps: ["pref_marital_status", "children_existing", "pref_children_existing"],
    options: [
    { label: "Never married", value: "Never married" },
    { label: "Divorced", value: "Divorced" },
    { label: "Widowed", value: "Widowed" },
    { label: "Awaiting divorce", value: "Awaiting divorce" }
  ]
  },

  {
    id: "pref_marital_status",
    section: "basics",
    field: "pref_marital_status",
    dbTable: "preferences",
    question: "What marital status are you open to in a partner?",
    type: "multi_select",
    gate: "hard",
    gateLogic: "Candidate's marital_status (Q6) must be in accepted list. 'Any' passes everyone.",
    doneLabel: "Done ✓",
    options: [
    { label: "Never married", value: "Never married" },
    { label: "Divorced", value: "Divorced" },
    { label: "Widowed", value: "Widowed" },
    { label: "Awaiting divorce", value: "Awaiting divorce" },
    { label: "Any", value: "Any" }
  ]
  },

  {
    id: "children_existing",
    section: "basics",
    field: "children_existing",
    dbTable: "users",
    question: "Do you have children?",
    type: "single_select",
    skipIf: "marital_status == 'Never married'",
    options: [
    { label: "No", value: "No" },
    { label: "Yes, they live with me", value: "Yes, they live with me" },
    { label: "Yes, they don't live with me", value: "Yes, they don't live with me" }
  ]
  },

  {
    id: "pref_children_existing",
    section: "basics",
    field: "pref_children_existing",
    dbTable: "preferences",
    question: "Are you open to a partner who has children?",
    type: "single_select",
    skipIf: "marital_status == 'Never married'",
    gate: "hard",
    gateLogic: "'No' + candidate has children = eliminated. 'Only if they don't live with them' + kids live with them = eliminated.",
    options: [
    { label: "Yes", value: "Yes" },
    { label: "Only if they don't live with them", value: "Only if they don't live with them" },
    { label: "No", value: "No" }
  ]
  },

  {
    id: "height",
    section: "basics",
    field: "height_cm",
    dbTable: "users",
    question: "How tall are you?",
    type: "single_select",
    columns: 2,
    optionsConditional: {
  "if_female": [
    {
      "label": "Below 5'2\" (157 cm)",
      "value": "155"
    },
    {
      "label": "5'2\" (157 cm)",
      "value": "157"
    },
    {
      "label": "5'3\" (160 cm)",
      "value": "160"
    },
    {
      "label": "5'4\" (163 cm)",
      "value": "163"
    },
    {
      "label": "5'5\" (165 cm)",
      "value": "165"
    },
    {
      "label": "5'6\" (168 cm)",
      "value": "168"
    },
    {
      "label": "5'7\" (170 cm)",
      "value": "170"
    },
    {
      "label": "Above 5'7\" (173 cm)",
      "value": "173"
    }
  ],
  "if_male": [
    {
      "label": "Below 5'5\" (165 cm)",
      "value": "163"
    },
    {
      "label": "5'5\" (165 cm)",
      "value": "165"
    },
    {
      "label": "5'6\" (168 cm)",
      "value": "168"
    },
    {
      "label": "5'7\" (170 cm)",
      "value": "170"
    },
    {
      "label": "5'8\" (173 cm)",
      "value": "173"
    },
    {
      "label": "5'9\" (175 cm)",
      "value": "175"
    },
    {
      "label": "5'10\" (178 cm)",
      "value": "178"
    },
    {
      "label": "5'11\" (180 cm)",
      "value": "180"
    },
    {
      "label": "6'0\" (183 cm)",
      "value": "183"
    },
    {
      "label": "6'1\" (185 cm)",
      "value": "185"
    },
    {
      "label": "6'2\" (188 cm)",
      "value": "188"
    },
    {
      "label": "6'3\" (191 cm)",
      "value": "191"
    },
    {
      "label": "Above 6'3\" (193 cm)",
      "value": "193"
    }
  ]
},
    scoring: {
      rule: "Matched via Q41 hard gate. Pass gate = 1.0."
    }
  },

  {
    id: "weight",
    section: "basics",
    field: "weight_kg",
    dbTable: "users",
    question: "What is your weight?",
    type: "single_select",
    columns: 2,
    optionsConditional: {
  "if_female": [
    {
      "label": "Below 45 kg (99 lbs)",
      "value": "42"
    },
    {
      "label": "45-50 kg (99-110 lbs)",
      "value": "47"
    },
    {
      "label": "50-55 kg (110-121 lbs)",
      "value": "52"
    },
    {
      "label": "55-60 kg (121-132 lbs)",
      "value": "57"
    },
    {
      "label": "60-65 kg (132-143 lbs)",
      "value": "62"
    },
    {
      "label": "65-70 kg (143-154 lbs)",
      "value": "67"
    },
    {
      "label": "70-75 kg (154-165 lbs)",
      "value": "72"
    },
    {
      "label": "75-80 kg (165-176 lbs)",
      "value": "77"
    },
    {
      "label": "Above 80 kg (176 lbs)",
      "value": "85"
    }
  ],
  "if_male": [
    {
      "label": "Below 60 kg (132 lbs)",
      "value": "57"
    },
    {
      "label": "60-65 kg (132-143 lbs)",
      "value": "62"
    },
    {
      "label": "65-70 kg (143-154 lbs)",
      "value": "67"
    },
    {
      "label": "70-75 kg (154-165 lbs)",
      "value": "72"
    },
    {
      "label": "75-80 kg (165-176 lbs)",
      "value": "77"
    },
    {
      "label": "80-85 kg (176-187 lbs)",
      "value": "82"
    },
    {
      "label": "85-90 kg (187-198 lbs)",
      "value": "87"
    },
    {
      "label": "90-100 kg (198-220 lbs)",
      "value": "95"
    },
    {
      "label": "Above 100 kg (220 lbs)",
      "value": "105"
    }
  ]
},
    scoring: {
      rule: "BMI calculated from height + weight. Same BMI range = 1.0, one step = 0.5, two steps = 0.25, three steps = 0.0."
    }
  },

  {
    id: "religion",
    section: "background",
    field: "religion",
    dbTable: "users",
    question: "What is your religion?",
    type: "single_select",
    notes: "Gates downstream: practice, caste, manglik, diet defaults.",
    columns: 2,
    options: [
    { label: "Hindu", value: "Hindu" },
    { label: "Muslim", value: "Muslim" },
    { label: "Sikh", value: "Sikh" },
    { label: "Jain", value: "Jain" },
    { label: "Christian", value: "Christian" },
    { label: "Buddhist", value: "Buddhist" },
    { label: "Parsi", value: "Parsi" },
    { label: "No religion", value: "No religion" },
    { label: "Other", value: "Other" }
  ],
    scoring: {
      rule: "Same religion = 1.0. Different = 0.0. Hard gate Q13 handles elimination."
    }
  },

  {
    id: "religious_practice",
    section: "background",
    field: "religious_practice",
    dbTable: "preferences",
    question: "How would you describe your religious practice?",
    type: "single_select",
    skipIf: "religion in ['Buddhist', 'No religion', 'Other', 'Parsi']",
    optionsConditional: {
  "Hindu": [
    {
      "label": "Very religious — daily puja, regular fasting, temple every week",
      "value": "Very religious"
    },
    {
      "label": "Religious — puja most days, major festivals, temple visits",
      "value": "Religious"
    },
    {
      "label": "Moderately religious — festivals and family rituals, occasional temple",
      "value": "Moderately religious"
    },
    {
      "label": "Not religious — cultural Hindu, don't practice actively",
      "value": "Not religious"
    }
  ],
  "Muslim": [
    {
      "label": "Very religious — five daily prayers, Ramadan, regular mosque",
      "value": "Very religious"
    },
    {
      "label": "Religious — Friday prayers, Ramadan, Eid celebrations",
      "value": "Religious"
    },
    {
      "label": "Moderately religious — Eid and major occasions, occasional prayer",
      "value": "Moderately religious"
    },
    {
      "label": "Not religious — cultural Muslim, don't practice actively",
      "value": "Not religious"
    }
  ],
  "Sikh": [
    {
      "label": "Very religious (Amritdhari) — Amrit chhaka, 5 Ks, daily Nitnem",
      "value": "Very religious (Amritdhari)"
    },
    {
      "label": "Religious (Keshdhari) — unshorn hair, regular Gurdwara, Nitnem",
      "value": "Religious (Keshdhari)"
    },
    {
      "label": "Moderate (Sahajdhari) — Gurdwara on occasions, flexible on 5 Ks",
      "value": "Moderate (Sahajdhari)"
    },
    {
      "label": "Not religious — cultural Sikh, don't practice actively",
      "value": "Not religious"
    }
  ],
  "Jain": [
    {
      "label": "Very religious — strict dietary rules, regular temple, Paryushana fasting",
      "value": "Very religious"
    },
    {
      "label": "Religious — temple regularly, dietary discipline, major festivals",
      "value": "Religious"
    },
    {
      "label": "Moderately religious — festivals and family rituals, flexible on diet",
      "value": "Moderately religious"
    },
    {
      "label": "Not religious — cultural Jain, don't practice actively",
      "value": "Not religious"
    }
  ],
  "Christian": [
    {
      "label": "Very religious — church every Sunday, Bible study, active in parish",
      "value": "Very religious"
    },
    {
      "label": "Religious — regular church, Christmas/Easter, prayer life",
      "value": "Religious"
    },
    {
      "label": "Moderately religious — church on occasions, celebrates festivals",
      "value": "Moderately religious"
    },
    {
      "label": "Not religious — cultural Christian, don't practice actively",
      "value": "Not religious"
    }
  ]
},
    scoring: {
      rule: "Same practice level = 1.0. One step apart = 0.5. Two steps = 0.25. Opposite ends = 0.0.",
      note: "Scored independently from religion. Two 'not religious' people of different faiths can match well."
    }
  },

  {
    id: "caste_community",
    section: "background",
    field: "caste_community",
    dbTable: "preferences",
    question: "What is your caste or community?",
    type: "single_select",
    skipIf: "religion in ['Muslim', 'Christian', 'Buddhist', 'Parsi', 'No religion', 'Other']",
    stateContext: "Top castes for raised_in_state shown first, then remaining for religion, then Other / Prefer not to say.",
    columns: 3,
    followUps: ["caste_importance"],
    options: "castes_by_religion_and_state",
    scoring: {
      rule: "Scoring driven by caste_importance (Q12a)."
    }
  },

  {
    id: "caste_importance",
    section: "background",
    field: "caste_importance",
    dbTable: "preferences",
    question: "How important is caste in your partner?",
    type: "single_select",
    skipIf: "caste_community == 'Prefer not to say'",
    gate: "hard",
    gateLogic: "'Must be same caste' + different caste = eliminated.",
    options: [
    { label: "Must be same caste", value: "Must be same caste" },
    { label: "Prefer same, open to others", value: "Prefer same, open to others" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "'Must be same' + same = 1.0. 'Prefer same' + same = 1.0, different = 0.5. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "pref_religion",
    section: "partner_bg",
    field: "pref_religion",
    dbTable: "preferences",
    question: "Does your partner's religion matter to you?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Same religion only' = must match Q9. 'Open, but not...' triggers exclude list. 'Open to all' passes everyone. Bidirectional.",
    followUps: ["pref_religion_exclude"],
    options: [
    { label: "Same religion only", value: "Same religion only" },
    { label: "Open to all", value: "Open to all" },
    { label: "Open, but not...", value: "Open, but not..." }
  ]
  },

  {
    id: "pref_religion_exclude",
    section: "partner_bg",
    field: "pref_religion_exclude",
    dbTable: "preferences",
    question: "Which religions would you NOT want to match with?",
    type: "multi_select",
    skipIf: "pref_religion != 'Open, but not...'",
    gate: "hard",
    gateLogic: "Candidate's religion in exclude list = eliminated.",
    doneLabel: "Done ✓",
    columns: 2,
    options: [
    { label: "Hindu", value: "Hindu" },
    { label: "Muslim", value: "Muslim" },
    { label: "Sikh", value: "Sikh" },
    { label: "Jain", value: "Jain" },
    { label: "Christian", value: "Christian" },
    { label: "Buddhist", value: "Buddhist" },
    { label: "Parsi", value: "Parsi" },
    { label: "No religion", value: "No religion" }
  ]
  },

  {
    id: "pref_caste",
    section: "partner_bg",
    field: "pref_caste",
    dbTable: "preferences",
    question: "What about caste — does it matter?",
    type: "single_select",
    skipIf: "religion in ['Muslim', 'Christian', 'Buddhist', 'Parsi', 'No religion', 'Other']",
    gate: "hard",
    gateLogic: "'Same caste only' = must match Q12. 'Open, but not...' triggers exclude list.",
    followUps: ["pref_caste_exclude"],
    options: [
    { label: "Same caste only", value: "Same caste only" },
    { label: "Same community, any caste", value: "Same community, any caste" },
    { label: "Open to all", value: "Open to all" },
    { label: "Open, but not...", value: "Open, but not..." }
  ]
  },

  {
    id: "pref_caste_exclude",
    section: "partner_bg",
    field: "pref_caste_exclude",
    dbTable: "preferences",
    question: "Which castes would you NOT want to match with?",
    type: "multi_select",
    skipIf: "pref_caste != 'Open, but not...'",
    gate: "hard",
    gateLogic: "Candidate's caste in exclude list = eliminated.",
    stateContext: "Same state-aware caste list as Q12. Top castes for user's raised_in_state shown first.",
    doneLabel: "Done ✓",
    columns: 3,
    options: "castes_by_religion_and_state"
  },

  {
    id: "pref_mother_tongue",
    section: "partner_bg",
    field: "pref_mother_tongue",
    dbTable: "preferences",
    question: "Does language matter? Should they speak your mother tongue?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Same language only' + mismatch = eliminated. 'Same or Hindi' + neither = eliminated.",
    options: [
    { label: "Same language only", value: "Same language only" },
    { label: "Same or Hindi", value: "Same or Hindi" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ]
  },

  {
    id: "education_level",
    section: "education",
    field: "education_level",
    dbTable: "users",
    question: "What is your highest education?",
    type: "single_select",
    columns: 2,
    options: [
    { label: "High school", value: "High school" },
    { label: "Diploma", value: "Diploma" },
    { label: "Bachelor's", value: "Bachelor's" },
    { label: "Master's", value: "Master's" },
    { label: "Doctorate / PhD", value: "Doctorate / PhD" },
    { label: "Professional (CA, CS, MBBS, LLB)", value: "Professional" }
  ],
    scoring: {
      rule: "Matched against Q20 (partner min education). Meets or exceeds = 1.0. Below = 0.0."
    }
  },

  {
    id: "education_field",
    section: "education",
    field: "education_field",
    dbTable: "users",
    question: "What did you study?",
    type: "single_select",
    columns: 2,
    followUps: ["pref_education_field"],
    options: [
    { label: "Engineering / IT", value: "Engineering / IT" },
    { label: "Medicine / Healthcare", value: "Medicine / Healthcare" },
    { label: "Business / MBA", value: "Business / MBA" },
    { label: "Law", value: "Law" },
    { label: "Finance / CA / CS", value: "Finance / CA / CS" },
    { label: "Arts / Humanities", value: "Arts / Humanities" },
    { label: "Science", value: "Science" },
    { label: "Design / Architecture", value: "Design / Architecture" },
    { label: "Government / Civil Services", value: "Government / Civil Services" },
    { label: "Other", value: "Other" }
  ]
  },

  {
    id: "pref_education_field",
    section: "education",
    field: "pref_education_field",
    dbTable: "preferences",
    question: "Does your partner's field of study matter?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "Same as mine", value: "Same as mine" },
    { label: "Doesn't matter", value: "Doesn't matter" },
    { label: "Specific fields...", value: "Specific fields", triggers: "education_field_multi" }
  ],
    scoring: {
      rule: "'Same as mine' + match = 1.0, no match = 0.0. 'Specific fields' + in list = 1.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "occupation_sector",
    section: "education",
    field: "occupation_sector",
    dbTable: "users",
    question: "What sector do you work in?",
    type: "single_select",
    columns: 3,
    followUps: ["company_name"],
    options: [
    { label: "Tech / IT", value: "Tech / IT" },
    { label: "Finance / Banking", value: "Finance / Banking" },
    { label: "Consulting", value: "Consulting" },
    { label: "Healthcare", value: "Healthcare" },
    { label: "Manufacturing", value: "Manufacturing" },
    { label: "Media / Entertainment", value: "Media / Entertainment" },
    { label: "Education", value: "Education" },
    { label: "Government / Public sector", value: "Government / Public sector" },
    { label: "Professional (Doctor, Lawyer, CA)", value: "Professional" },
    { label: "Business / Self-employed", value: "Business / Self-employed" },
    { label: "Startup", value: "Startup" },
    { label: "Retail / Hospitality", value: "Retail / Hospitality" },
    { label: "Not working", value: "Not working" },
    { label: "Student", value: "Student" },
    { label: "Other", value: "Other" }
  ],
    scoring: {
      rule: "Same sector = 1.0. Different = 0.0."
    }
  },

  {
    id: "company_name",
    section: "education",
    field: "company_name",
    dbTable: "users",
    question: "Which company?",
    type: "text_input",
    placeholder: "e.g. TCS, Infosys, family business...",
    skipIf: "occupation_sector in ['Not working', 'Student']",
    notes: "Free text. Not used in matching directly — signal for match brief."
  },

  {
    id: "annual_income",
    section: "education",
    field: "annual_income",
    dbTable: "users",
    question: "What is your annual income? This is only used for matching — never displayed.",
    type: "single_select",
    notes: "All brackets labeled '/year'. See income_brackets reference data.",
    columns: 2,
    options: "income_by_location",
    scoring: {
      rule: "Matched against Q21 (partner min income). Meets or exceeds = 1.0. Below = 0.0."
    }
  },

  {
    id: "pref_education_min",
    section: "education",
    field: "pref_education_min",
    dbTable: "preferences",
    question: "Minimum education you'd want in a partner?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "Doesn't matter", value: "Doesn't matter" },
    { label: "At least Bachelor's", value: "At least Bachelor's" },
    { label: "At least Master's", value: "At least Master's" },
    { label: "At least Professional degree", value: "At least Professional degree" }
  ],
    scoring: {
      rule: "Candidate meets or exceeds = 1.0. Below = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "pref_income_min",
    section: "education",
    field: "pref_income_min",
    dbTable: "preferences",
    question: "Minimum annual income you'd want in a partner?",
    type: "single_select",
    gate: "scored",
    columns: 2,
    options: "income_by_location_with_doesnt_matter",
    scoring: {
      rule: "Candidate meets or exceeds = 1.0. Below = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "family_type",
    section: "family",
    field: "family_type",
    dbTable: "users",
    question: "What kind of family setup did you grow up in?",
    type: "single_select",
    followUps: ["pref_family_type"],
    options: [
    { label: "Nuclear (parents live separately from extended family)", value: "Nuclear" },
    { label: "Joint (everyone under one roof)", value: "Joint" },
    { label: "Extended (same building or compound, separate households)", value: "Extended" },
    { label: "Parents nearby (same city, separate homes)", value: "Parents nearby" }
  ]
  },

  {
    id: "pref_family_type",
    section: "family",
    field: "pref_family_type",
    dbTable: "preferences",
    question: "Do you prefer your partner to be from a similar family setup?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "Same as mine", value: "Same as mine" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "'Same as mine' + match = 1.0, no match = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "family_status",
    section: "family",
    field: "family_status",
    dbTable: "users",
    question: "How would you describe your family's financial status?",
    type: "single_select",
    optionsConditional: {
  "if_india": [
    {
      "label": "Less than ₹10 lakh annual income",
      "value": "tier_1"
    },
    {
      "label": "₹10-30 lakh annual income + some assets",
      "value": "tier_2"
    },
    {
      "label": "₹30-70 lakh annual income + assets",
      "value": "tier_3"
    },
    {
      "label": "₹70 lakh+ annual income + significant assets",
      "value": "tier_4"
    },
    {
      "label": "Assets over ₹10 crore",
      "value": "tier_5"
    },
    {
      "label": "Prefer not to say",
      "value": "Prefer not to say"
    }
  ],
  "if_outside_india": [
    {
      "label": "Middle class",
      "value": "tier_2"
    },
    {
      "label": "Upper middle class",
      "value": "tier_3"
    },
    {
      "label": "Affluent",
      "value": "tier_4"
    },
    {
      "label": "Wealthy",
      "value": "tier_5"
    },
    {
      "label": "Prefer not to say",
      "value": "Prefer not to say"
    }
  ]
},
    scoring: {
      rule: "Matched against Q50 (partner family status pref). 'Same or higher' compares tiers."
    }
  },

  {
    id: "father_occupation",
    section: "family",
    field: "father_occupation",
    dbTable: "users",
    question: "Father's occupation?",
    type: "single_select",
    options: [
    { label: "Business / Self-employed", value: "Business / Self-employed" },
    { label: "Service / Salaried", value: "Service / Salaried" },
    { label: "Professional (Doctor, Lawyer, CA)", value: "Professional" },
    { label: "Government", value: "Government" },
    { label: "Retired", value: "Retired" },
    { label: "Late", value: "Late" },
    { label: "Prefer not to say", value: "Prefer not to say" }
  ],
    scoring: {
      rule: "Same category = 1.0. Different = 0.0. 'Late' and 'Prefer not to say' = skip, no penalty."
    }
  },

  {
    id: "mother_occupation",
    section: "family",
    field: "mother_occupation",
    dbTable: "users",
    question: "Mother's occupation?",
    type: "single_select",
    options: [
    { label: "Homemaker", value: "Homemaker" },
    { label: "Working professional", value: "Working professional" },
    { label: "Business", value: "Business" },
    { label: "Government", value: "Government" },
    { label: "Retired", value: "Retired" },
    { label: "Late", value: "Late" },
    { label: "Prefer not to say", value: "Prefer not to say" }
  ],
    scoring: {
      rule: "Same category = 1.0. Different = 0.0. 'Late' and 'Prefer not to say' = skip, no penalty."
    }
  },

  {
    id: "siblings",
    section: "family",
    field: "siblings",
    dbTable: "users",
    question: "Do you have siblings?",
    type: "single_select",
    followUps: ["pref_siblings"],
    options: [
    { label: "Only child", value: "Only child" },
    { label: "1 sibling", value: "1 sibling" },
    { label: "2 siblings", value: "2 siblings" },
    { label: "3+ siblings", value: "3+ siblings" }
  ]
  },

  {
    id: "pref_siblings",
    section: "family",
    field: "pref_siblings",
    dbTable: "preferences",
    question: "Do you have a preference about your partner's siblings?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "Must have siblings", value: "Must have siblings" },
    { label: "Single child is fine", value: "Single child is fine" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "'Must have siblings' + only child = 0.0, has siblings = 1.0. Others = 1.0 always."
    }
  },

  {
    id: "diet",
    section: "lifestyle",
    field: "diet",
    dbTable: "signals",
    question: "What is your diet?",
    type: "single_select",
    notes: "Universal options. Not religion-specific.",
    columns: 2,
    options: [
    { label: "Strict vegetarian (no onion/garlic)", value: "Strict vegetarian" },
    { label: "Vegetarian", value: "Vegetarian" },
    { label: "Eggetarian", value: "Eggetarian" },
    { label: "Occasionally non-veg", value: "Occasionally non-veg" },
    { label: "Non-veg", value: "Non-veg" },
    { label: "Vegan", value: "Vegan" },
    { label: "Jain", value: "Jain" },
    { label: "Halal only", value: "Halal only" },
    { label: "Other", value: "Other" }
  ],
    scoring: {
      rule: "Matched against Q33 (partner diet pref, hard gate). Pass gate = 1.0."
    }
  },

  {
    id: "drinking",
    section: "lifestyle",
    field: "drinking",
    dbTable: "signals",
    question: "Do you drink alcohol?",
    type: "single_select",
    options: [
    { label: "Never", value: "Never" },
    { label: "Socially / Occasionally", value: "Socially / Occasionally" },
    { label: "Regularly", value: "Regularly" }
  ],
    scoring: {
      rule: "Same habit = 1.0. Adjacent = 0.5. Far apart = 0.25."
    }
  },

  {
    id: "smoking",
    section: "lifestyle",
    field: "smoking",
    dbTable: "signals",
    question: "Do you smoke?",
    type: "single_select",
    options: [
    { label: "Never", value: "Never" },
    { label: "Socially / Occasionally", value: "Socially / Occasionally" },
    { label: "Regularly", value: "Regularly" }
  ],
    scoring: {
      rule: "Same habit = 1.0. Adjacent = 0.5. Far apart = 0.0."
    }
  },

  {
    id: "fitness_frequency",
    section: "lifestyle",
    field: "fitness_frequency",
    dbTable: "signals",
    question: "How often do you exercise or play sports?",
    type: "single_select",
    gate: "wow",
    options: [
    { label: "Daily", value: "Daily" },
    { label: "3-5 times a week", value: "3-5 times a week" },
    { label: "1-2 times a week", value: "1-2 times a week" },
    { label: "Rarely", value: "Rarely" },
    { label: "Never", value: "Never" }
  ],
    scoring: {
      rule: "Same level = 1.5 (WOW). One step = 1.0. Two steps = 0.5. Far apart = 0.0."
    }
  },

  {
    id: "pref_diet",
    section: "lifestyle",
    field: "pref_diet",
    dbTable: "preferences",
    question: "How important is diet in your partner?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Same as mine' = must match Q29 exactly. 'Any vegetarian' = eliminates non-veg and occasionally non-veg. 'Vegetarian only' = must be veg or stricter. 'Doesn't matter' passes everyone.",
    options: [
    { label: "Same as mine", value: "Same as mine" },
    { label: "Any vegetarian (no non-veg)", value: "Any vegetarian" },
    { label: "Vegetarian only", value: "Vegetarian only" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ]
  },

  {
    id: "pref_drinking",
    section: "lifestyle",
    field: "pref_drinking",
    dbTable: "preferences",
    question: "Is drinking a dealbreaker for you?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Must not drink' + candidate 'Regularly' = eliminated.",
    options: [
    { label: "Must not drink", value: "Must not drink" },
    { label: "Social drinking OK", value: "Social drinking OK" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ]
  },

  {
    id: "pref_smoking",
    section: "lifestyle",
    field: "pref_smoking",
    dbTable: "preferences",
    question: "Is smoking a dealbreaker?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Must not smoke' + candidate 'Regularly' = eliminated.",
    options: [
    { label: "Must not smoke", value: "Must not smoke" },
    { label: "Social smoking OK", value: "Social smoking OK" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ]
  },

  {
    id: "marriage_timeline",
    section: "marriage",
    field: "marriage_timeline",
    dbTable: "preferences",
    question: "How soon are you looking to get married?",
    type: "single_select",
    gate: "hard",
    gateLogic: "Must be within 1 step. 'Within 1 year' + '2-3 years' = eliminated.",
    options: [
    { label: "Within 1 year", value: "Within 1 year" },
    { label: "1-2 years", value: "1-2 years" },
    { label: "2-3 years", value: "2-3 years" },
    { label: "Just exploring", value: "Just exploring" }
  ],
    scoring: {
      rule: "Same timeline = 1.0. One step apart (passes gate) = 0.5."
    }
  },

  {
    id: "children_intent",
    section: "marriage",
    field: "children_intent",
    dbTable: "preferences",
    question: "Do you want children?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'Yes' vs 'No' = eliminated. 'Maybe' compatible with both. Bidirectional.",
    followUps: ["children_timeline", "pref_children_timeline"],
    options: [
    { label: "Yes", value: "Yes" },
    { label: "Maybe / Open to it", value: "Maybe / Open to it" },
    { label: "No", value: "No" }
  ]
  },

  {
    id: "children_timeline",
    section: "marriage",
    field: "children_timeline",
    dbTable: "preferences",
    question: "When would you want children?",
    type: "single_select",
    skipIf: "children_intent == 'No'",
    options: [
    { label: "Soon after marriage", value: "Soon after marriage" },
    { label: "After 2-3 years", value: "After 2-3 years" },
    { label: "After 4+ years", value: "After 4+ years" }
  ]
  },

  {
    id: "pref_children_timeline",
    section: "marriage",
    field: "pref_children_timeline",
    dbTable: "preferences",
    question: "When would you want your partner to be open to having children?",
    type: "single_select",
    skipIf: "children_intent == 'No'",
    gate: "scored",
    options: [
    { label: "Soon after marriage", value: "Soon after marriage" },
    { label: "After 2-3 years", value: "After 2-3 years" },
    { label: "After 4+ years", value: "After 4+ years" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "Match = 1.0. No match = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "living_arrangement",
    section: "marriage",
    field: "living_arrangement",
    dbTable: "preferences",
    question: "After marriage, where would you want to live?",
    type: "single_select",
    followUps: ["pref_living_arrangement"],
    options: [
    { label: "With parents (joint family)", value: "With parents (joint family)" },
    { label: "Near parents but separate", value: "Near parents but separate" },
    { label: "Independent — wherever life takes us", value: "Independent" },
    { label: "Open to discussion", value: "Open to discussion" }
  ]
  },

  {
    id: "pref_living_arrangement",
    section: "marriage",
    field: "pref_living_arrangement",
    dbTable: "preferences",
    question: "What living arrangement would you need your partner to be open to?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "With parents (joint family)", value: "With parents (joint family)" },
    { label: "Near parents but separate", value: "Near parents but separate" },
    { label: "Independent — wherever life takes us", value: "Independent" },
    { label: "Open to discussion", value: "Open to discussion" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "Match = 1.0. No match = 0.0. 'Doesn't matter' or 'Open to discussion' = 1.0."
    }
  },

  {
    id: "relocation_willingness",
    section: "marriage",
    field: "relocation_willingness",
    dbTable: "preferences",
    question: "Would you relocate for the right match?",
    type: "single_select",
    gate: "hard",
    gateLogic: "Only eliminates when BOTH say 'No, I'm settled' AND different countries. If at least one willing, pair passes.",
    followUps: ["relocation_countries"],
    options: [
    { label: "Yes, anywhere", value: "Yes, anywhere" },
    { label: "Yes, within India", value: "Yes, within India" },
    { label: "Yes, within my state/country", value: "Yes, within my state/country" },
    { label: "Only abroad", value: "Only abroad" },
    { label: "No, I'm settled where I am", value: "No, I'm settled where I am" }
  ]
  },

  {
    id: "relocation_countries",
    section: "marriage",
    field: "relocation_countries",
    dbTable: "preferences",
    question: "Which countries?",
    type: "multi_select",
    skipIf: "relocation_willingness not in ['Only abroad', 'Yes, anywhere']",
    doneLabel: "Done ✓",
    columns: 2,
    options: "countries"
  },

  {
    id: "pref_age_range",
    section: "partner_physical",
    field: "pref_age_range",
    dbTable: "preferences",
    question: "What age range are you looking for?",
    type: "two_step_range",
    gate: "hard",
    gateLogic: "Candidate's age must fall within stated range. No buffer.",
    step1:     {
      text: "Partner's minimum age?",
      field: "pref_age_min",
      columns: 3,
      options: "age_range_min"
    },
    step2:     {
      text: "Partner's maximum age?",
      field: "pref_age_max",
      columns: 3,
      options: "age_range_max"
    }
  },

  {
    id: "pref_height_range",
    section: "partner_physical",
    field: "pref_height_range",
    dbTable: "preferences",
    question: "Any height preference?",
    type: "two_step_same_screen",
    gate: "hard",
    gateLogic: "Candidate's height outside min/max range = eliminated. 'Doesn't matter' passes everyone.",
    notes: "Same-screen layout: two dropdowns side by side.",
    hasDoesntMatter: true,
    doesntMatterLabel: "Doesn't matter",
    step1:     {
      text: "Min height",
      field: "pref_height_min",
      options: "height_opposite_gender"
    },
    step2:     {
      text: "Max height",
      field: "pref_height_max",
      options: "height_opposite_gender"
    }
  },

  {
    id: "cooking_contribution_m",
    section: "household",
    field: "cooking_contribution",
    dbTable: "signals",
    question: "How often are you willing to cook?",
    type: "single_select",
    gender: "Male",
    followUps: ["pref_partner_cooking_freq_m", "pref_partner_can_cook_m"],
    options: [
    { label: "Most days (10+ meals/week)", value: "Most days" },
    { label: "A few times a week (4-7 meals)", value: "A few times a week" },
    { label: "Occasionally (1-3 meals)", value: "Occasionally" },
    { label: "Rarely or never", value: "Rarely or never" }
  ]
  },

  {
    id: "pref_partner_cooking_freq_m",
    section: "household",
    field: "pref_partner_cooking_freq",
    dbTable: "preferences",
    question: "How often would you want your partner to cook?",
    type: "single_select",
    gender: "Male",
    gate: "scored",
    options: [
    { label: "Most days", value: "Most days" },
    { label: "A few times a week", value: "A few times a week" },
    { label: "Occasionally", value: "Occasionally" },
    { label: "Doesn't matter — we'll figure it out", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "Matched against her cooking_contribution (Q43F). Meets or exceeds = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0."
    }
  },

  {
    id: "pref_partner_can_cook_m",
    section: "household",
    field: "pref_partner_can_cook",
    dbTable: "preferences",
    question: "Is it important that your partner knows how to cook?",
    type: "single_select",
    gender: "Male",
    gate: "scored",
    options: [
    { label: "Yes, regularly", value: "Yes, regularly" },
    { label: "Some cooking is enough", value: "Some cooking is enough" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "Matched against her do_you_cook (Q42F). 'Yes, regularly' + she cooks regularly = 1.0. + she says 'Not my thing' = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "household_contribution_m",
    section: "household",
    field: "household_contribution",
    dbTable: "signals",
    question: "How do you see household responsibilities?",
    type: "single_select",
    gender: "Male",
    options: [
    { label: "Shared equally", value: "Shared equally" },
    { label: "Mostly outsourced (cook/maid)", value: "Mostly outsourced" },
    { label: "Flexible — whatever works", value: "Flexible" },
    { label: "She would handle most of it", value: "Mostly her" }
  ],
    scoring: {
      rule: "Cross-matched against her pref_partner_household (Q45F). Match = 1.0. 'Flexible' = 1.0 with anything."
    }
  },

  {
    id: "partner_working_m",
    section: "household",
    field: "partner_working",
    dbTable: "preferences",
    question: "What's your view on your partner working?",
    type: "single_select",
    gender: "Male",
    options: [
    { label: "A career is important to me", value: "Career important" },
    { label: "I'm flexible — whatever she wants", value: "Her choice" },
    { label: "I'd prefer a homemaker", value: "Prefer homemaker" }
  ],
    scoring: {
      rule: "Cross-matched against her career_after_marriage (Q46F). Aligned = 1.0. Misaligned = 0.0. 'Her choice' = 1.0 with anything."
    }
  },

  {
    id: "do_you_cook_f",
    section: "household",
    field: "do_you_cook",
    dbTable: "signals",
    question: "How's your cooking?",
    type: "single_select",
    gender: "Female",
    options: [
    { label: "I cook often", value: "I cook often" },
    { label: "Sometimes", value: "Sometimes" },
    { label: "Learning", value: "Learning" },
    { label: "Not my thing", value: "Not my thing" }
  ]
  },

  {
    id: "cooking_contribution_f",
    section: "household",
    field: "cooking_contribution",
    dbTable: "signals",
    question: "How often are you willing to cook?",
    type: "single_select",
    gender: "Female",
    options: [
    { label: "Most days (10+ meals/week)", value: "Most days" },
    { label: "A few times a week (4-7 meals)", value: "A few times a week" },
    { label: "Occasionally (1-3 meals)", value: "Occasionally" },
    { label: "Rarely or never", value: "Rarely or never" }
  ]
  },

  {
    id: "pref_partner_cooking_f",
    section: "household",
    field: "pref_partner_cooking",
    dbTable: "preferences",
    question: "How often would you want your partner to cook?",
    type: "single_select",
    gender: "Female",
    gate: "scored",
    options: [
    { label: "Most days", value: "Most days" },
    { label: "A few times a week", value: "A few times a week" },
    { label: "Occasionally", value: "Occasionally" },
    { label: "Doesn't matter — we'll figure it out", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "Matched against his cooking_contribution (Q42M). Meets or exceeds = 1.0. Exceeds by 2+ levels = 1.5 (WOW). Below = 0.0."
    }
  },

  {
    id: "pref_partner_household_f",
    section: "household",
    field: "pref_partner_household",
    dbTable: "preferences",
    question: "How much do you need your partner to contribute at home?",
    type: "single_select",
    gender: "Female",
    gate: "scored",
    options: [
    { label: "Equal share", value: "Equal share" },
    { label: "Significant help", value: "Significant help" },
    { label: "Some help", value: "Some help" },
    { label: "Not needed — I'll manage or outsource", value: "Not needed" }
  ],
    scoring: {
      rule: "Matched against his household_contribution (Q43M). 'Equal share' + 'Shared equally' = 1.0. 'Equal share' + 'Mostly her' = 0.0. 'Not needed' = 1.0 with anything."
    }
  },

  {
    id: "career_after_marriage_f",
    section: "household",
    field: "career_after_marriage",
    dbTable: "signals",
    question: "What does your career look like after marriage?",
    type: "single_select",
    gender: "Female",
    options: [
    { label: "Full steam ahead", value: "Full steam ahead" },
    { label: "Open to a pause for family", value: "Open to a pause" },
    { label: "Still figuring it out", value: "Undecided" },
    { label: "Prefer to focus on home", value: "Prefer homemaking" }
  ],
    scoring: {
      rule: "Cross-matched against his partner_working (Q44M). Aligned = 1.0. Misaligned = 0.0."
    }
  },

  {
    id: "live_with_inlaws_f",
    section: "household",
    field: "live_with_inlaws",
    dbTable: "signals",
    question: "Would you be OK living with his parents?",
    type: "single_select",
    gender: "Female",
    options: [
    { label: "Yes, happy to", value: "Yes, happy to" },
    { label: "For some time, not permanently", value: "For some time" },
    { label: "Prefer not to", value: "Prefer not to" },
    { label: "Depends on the situation", value: "Depends" }
  ],
    scoring: {
      rule: "Cross-matched against his living_arrangement (Q38). Joint + happy = 1.0. Joint + prefer not = 0.0. Independent = 1.0 regardless. 'Depends' = 0.5 with joint, 1.0 otherwise."
    }
  },

  {
    id: "financial_planning",
    section: "household",
    field: "financial_planning",
    dbTable: "signals",
    question: "How should finances work in a marriage?",
    type: "single_select",
    options: [
    { label: "Fully joint", value: "Fully joint" },
    { label: "Joint for household, separate for personal", value: "Joint for household, separate for personal" },
    { label: "Mostly separate", value: "Mostly separate" }
  ],
    scoring: {
      rule: "Same = 1.0. Different = 0.0."
    }
  },

  {
    id: "manglik_status",
    section: "sensitive",
    field: "manglik_status",
    dbTable: "signals",
    question: "Are you Manglik?",
    type: "single_select",
    skipIf: "religion not in ['Hindu', 'Jain']",
    followUps: ["pref_manglik"],
    options: [
    { label: "Yes", value: "Yes" },
    { label: "No", value: "No" },
    { label: "Don't know", value: "Don't know" },
    { label: "Not applicable", value: "Not applicable" },
    { label: "Prefer not to say", value: "Prefer not to say" }
  ]
  },

  {
    id: "pref_manglik",
    section: "sensitive",
    field: "pref_manglik",
    dbTable: "preferences",
    question: "Is Manglik status important in your partner?",
    type: "single_select",
    skipIf: "manglik_status not in ['Yes', 'No']",
    gate: "hard",
    gateLogic: "'Must match' = candidate's manglik must be same. Others pass everyone.",
    options: [
    { label: "Must match", value: "Must match" },
    { label: "Prefer, but flexible", value: "Prefer, but flexible" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ]
  },

  {
    id: "pref_family_status",
    section: "sensitive",
    field: "pref_family_status",
    dbTable: "preferences",
    question: "Does your partner's family financial status matter?",
    type: "single_select",
    gate: "scored",
    options: [
    { label: "Same or higher", value: "Same or higher" },
    { label: "Doesn't matter", value: "Doesn't matter" }
  ],
    scoring: {
      rule: "'Same or higher' compares Q23 tiers. Candidate same/higher = 1.0. Lower = 0.0. 'Doesn't matter' = 1.0 always."
    }
  },

  {
    id: "known_conditions",
    section: "sensitive",
    field: "known_conditions",
    dbTable: "users",
    question: "Do you have any known medical conditions? (e.g. diabetes, asthma, thyroid)",
    type: "single_select",
    followUps: ["pref_conditions"],
    options: [
    { label: "No", value: "No" },
    { label: "Yes", value: "Yes" },
    { label: "Prefer not to say", value: "Prefer not to say" }
  ]
  },

  {
    id: "disability",
    section: "sensitive",
    field: "disability",
    dbTable: "users",
    question: "Do you have a disability?",
    type: "single_select",
    followUps: ["pref_disability"],
    options: [
    { label: "No", value: "No" },
    { label: "Yes", value: "Yes" },
    { label: "Prefer not to say", value: "Prefer not to say" }
  ]
  },

  {
    id: "pref_conditions",
    section: "sensitive",
    field: "pref_conditions",
    dbTable: "preferences",
    question: "Are you open to a partner with a medical condition?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'No' + candidate has condition = eliminated.",
    options: [
    { label: "Yes", value: "Yes" },
    { label: "Depends on the condition", value: "Depends" },
    { label: "No", value: "No" }
  ]
  },

  {
    id: "pref_disability",
    section: "sensitive",
    field: "pref_disability",
    dbTable: "preferences",
    question: "Are you open to a partner with a disability?",
    type: "single_select",
    gate: "hard",
    gateLogic: "'No' + candidate has disability = eliminated.",
    options: [
    { label: "Yes", value: "Yes" },
    { label: "Depends", value: "Depends" },
    { label: "No", value: "No" }
  ]
  },

  {
    id: "social_style",
    section: "personality",
    field: "social_style",
    dbTable: "signals",
    question: "How social are you?",
    type: "single_select",
    gate: "wow",
    options: [
    { label: "Love big gatherings — the more people the better", value: "Very social" },
    { label: "Enjoy going out but need my downtime", value: "Social" },
    { label: "Prefer small groups and close friends", value: "Introverted" },
    { label: "Homebody — happiest at home", value: "Very introverted" }
  ],
    scoring: {
      rule: "Same style = 1.5 (WOW). One step = 1.0. Two steps = 0.5. Extremes = 0.0."
    }
  },

  {
    id: "conflict_style",
    section: "personality",
    field: "conflict_style",
    dbTable: "signals",
    question: "How do you handle disagreements?",
    type: "single_select",
    gate: "wow",
    options: [
    { label: "Address it right away", value: "Address immediately" },
    { label: "Give it a day, then talk", value: "Give it time" },
    { label: "Let most things go", value: "Let it go" },
    { label: "Need time alone before I can discuss", value: "Need space" }
  ],
    scoring: {
      rule: "Scored as compatibility matrix, not ordinal distance.",
      note: "'Give it time' and 'Need space' are compatible (both need processing time). 'Address immediately' and 'Let it go' are less compatible.",
      type: "matrix",
      matrix: {
        "Address immediately": [
                1.5,
                1.0,
                0.5,
                0.5
        ],
        "Give it time": [
                1.0,
                1.5,
                1.0,
                1.0
        ],
        "Let it go": [
                0.5,
                1.0,
                1.5,
                1.0
        ],
        "Need space": [
                0.5,
                1.0,
                1.0,
                1.5
        ]
}
    }
  },

  {
    id: "weekend_style",
    section: "personality",
    field: "weekend_style",
    dbTable: "signals",
    question: "What does your ideal weekend look like?",
    type: "single_select",
    gate: "wow",
    options: [
    { label: "Out and about — restaurants, events, travel", value: "Out and about" },
    { label: "Mix of plans and downtime", value: "Mix" },
    { label: "Quiet at home — cook, read, recharge", value: "Quiet at home" },
    { label: "Depends on the week", value: "Depends" }
  ],
    scoring: {
      rule: "Same style = 1.5 (WOW). One step = 1.0. 'Depends' = 1.0 with anything."
    }
  },

  {
    id: "communication_style",
    section: "personality",
    field: "communication_style",
    dbTable: "signals",
    question: "How do you stay connected with people you care about?",
    type: "single_select",
    gate: "wow",
    options: [
    { label: "Talk or call often — daily check-ins", value: "Daily check-ins" },
    { label: "Regular texts and voice notes", value: "Regular texts" },
    { label: "Quality time over quantity — less frequent but deeper", value: "Quality over quantity" },
    { label: "I'm not great at staying in touch but I show up when it matters", value: "Show up when it matters" }
  ],
    scoring: {
      rule: "Same style = 1.5 (WOW). One step = 1.0. Two steps = 0.5. Extremes = 0.0."
    }
  }
];

// ═══ QUESTION INDEX ═══
const QUESTION_INDEX = Object.freeze({
  "intent": 0,
  "full_name": 1,
  "preferred_name": 2,
  "gender": 3,
  "date_of_birth": 4,
  "current_location": 5,
  "pref_current_location": 6,
  "raised_in": 7,
  "pref_raised_in": 8,
  "mother_tongue": 9,
  "languages_spoken": 10,
  "marital_status": 11,
  "pref_marital_status": 12,
  "children_existing": 13,
  "pref_children_existing": 14,
  "height": 15,
  "weight": 16,
  "religion": 17,
  "religious_practice": 18,
  "caste_community": 19,
  "caste_importance": 20,
  "pref_religion": 21,
  "pref_religion_exclude": 22,
  "pref_caste": 23,
  "pref_caste_exclude": 24,
  "pref_mother_tongue": 25,
  "education_level": 26,
  "education_field": 27,
  "pref_education_field": 28,
  "occupation_sector": 29,
  "company_name": 30,
  "annual_income": 31,
  "pref_education_min": 32,
  "pref_income_min": 33,
  "family_type": 34,
  "pref_family_type": 35,
  "family_status": 36,
  "father_occupation": 37,
  "mother_occupation": 38,
  "siblings": 39,
  "pref_siblings": 40,
  "diet": 41,
  "drinking": 42,
  "smoking": 43,
  "fitness_frequency": 44,
  "pref_diet": 45,
  "pref_drinking": 46,
  "pref_smoking": 47,
  "marriage_timeline": 48,
  "children_intent": 49,
  "children_timeline": 50,
  "pref_children_timeline": 51,
  "living_arrangement": 52,
  "pref_living_arrangement": 53,
  "relocation_willingness": 54,
  "relocation_countries": 55,
  "pref_age_range": 56,
  "pref_height_range": 57,
  "cooking_contribution_m": 58,
  "pref_partner_cooking_freq_m": 59,
  "pref_partner_can_cook_m": 60,
  "household_contribution_m": 61,
  "partner_working_m": 62,
  "do_you_cook_f": 63,
  "cooking_contribution_f": 64,
  "pref_partner_cooking_f": 65,
  "pref_partner_household_f": 66,
  "career_after_marriage_f": 67,
  "live_with_inlaws_f": 68,
  "financial_planning": 69,
  "manglik_status": 70,
  "pref_manglik": 71,
  "pref_family_status": 72,
  "known_conditions": 73,
  "disability": 74,
  "pref_conditions": 75,
  "pref_disability": 76,
  "social_style": 77,
  "conflict_style": 78,
  "weekend_style": 79,
  "communication_style": 80,
});

const SECTION_ORDER = ["setup", "basics", "background", "partner_bg", "education", "family", "lifestyle", "marriage", "partner_physical", "household", "sensitive", "personality"];

// ═══ REFERENCE DATA ═══

const COUNTRIES = [
    { label: "USA", value: "USA" },
    { label: "UK", value: "UK" },
    { label: "Canada", value: "Canada" },
    { label: "Australia", value: "Australia" },
    { label: "UAE", value: "UAE" },
    { label: "Singapore", value: "Singapore" },
    { label: "Germany", value: "Germany" },
    { label: "New Zealand", value: "New Zealand" },
    { label: "Saudi Arabia", value: "Saudi Arabia" },
    { label: "Qatar", value: "Qatar" },
    { label: "Kuwait", value: "Kuwait" },
    { label: "Oman", value: "Oman" },
    { label: "Bahrain", value: "Bahrain" },
    { label: "Malaysia", value: "Malaysia" },
    { label: "South Africa", value: "South Africa" },
    { label: "Kenya", value: "Kenya" },
    { label: "Netherlands", value: "Netherlands" },
    { label: "Ireland", value: "Ireland" },
    { label: "Other →", value: "Other", requires_text: true }
  ];

const STATES_INDIA = [
    { label: "Maharashtra", value: "Maharashtra" },
    { label: "Delhi NCR", value: "Delhi NCR" },
    { label: "Karnataka", value: "Karnataka" },
    { label: "Tamil Nadu", value: "Tamil Nadu" },
    { label: "Gujarat", value: "Gujarat" },
    { label: "Rajasthan", value: "Rajasthan" },
    { label: "Uttar Pradesh", value: "Uttar Pradesh" },
    { label: "West Bengal", value: "West Bengal" },
    { label: "Kerala", value: "Kerala" },
    { label: "Telangana", value: "Telangana" },
    { label: "Punjab", value: "Punjab" },
    { label: "Haryana", value: "Haryana" },
    { label: "Madhya Pradesh", value: "Madhya Pradesh" },
    { label: "Bihar", value: "Bihar" },
    { label: "Andhra Pradesh", value: "Andhra Pradesh" },
    { label: "Other →", value: "Other", requires_text: true }
  ];

const STATES_INDIA_FULL = [
    { label: "Andhra Pradesh", value: "Andhra Pradesh" },
    { label: "Arunachal Pradesh", value: "Arunachal Pradesh" },
    { label: "Assam", value: "Assam" },
    { label: "Bihar", value: "Bihar" },
    { label: "Chhattisgarh", value: "Chhattisgarh" },
    { label: "Delhi NCR", value: "Delhi NCR" },
    { label: "Goa", value: "Goa" },
    { label: "Gujarat", value: "Gujarat" },
    { label: "Haryana", value: "Haryana" },
    { label: "Himachal Pradesh", value: "Himachal Pradesh" },
    { label: "Jammu & Kashmir", value: "Jammu & Kashmir" },
    { label: "Jharkhand", value: "Jharkhand" },
    { label: "Karnataka", value: "Karnataka" },
    { label: "Kerala", value: "Kerala" },
    { label: "Madhya Pradesh", value: "Madhya Pradesh" },
    { label: "Maharashtra", value: "Maharashtra" },
    { label: "Manipur", value: "Manipur" },
    { label: "Meghalaya", value: "Meghalaya" },
    { label: "Mizoram", value: "Mizoram" },
    { label: "Nagaland", value: "Nagaland" },
    { label: "Odisha", value: "Odisha" },
    { label: "Punjab", value: "Punjab" },
    { label: "Rajasthan", value: "Rajasthan" },
    { label: "Sikkim", value: "Sikkim" },
    { label: "Tamil Nadu", value: "Tamil Nadu" },
    { label: "Telangana", value: "Telangana" },
    { label: "Tripura", value: "Tripura" },
    { label: "Uttar Pradesh", value: "Uttar Pradesh" },
    { label: "Uttarakhand", value: "Uttarakhand" },
    { label: "West Bengal", value: "West Bengal" },
    { label: "Chandigarh", value: "Chandigarh" },
    { label: "Puducherry", value: "Puducherry" },
    { label: "Ladakh", value: "Ladakh" }
  ];

const LANGUAGES_ALL = [
    { label: "Hindi", value: "Hindi" },
    { label: "English", value: "English" },
    { label: "Gujarati", value: "Gujarati" },
    { label: "Marathi", value: "Marathi" },
    { label: "Tamil", value: "Tamil" },
    { label: "Telugu", value: "Telugu" },
    { label: "Kannada", value: "Kannada" },
    { label: "Malayalam", value: "Malayalam" },
    { label: "Bengali", value: "Bengali" },
    { label: "Punjabi", value: "Punjabi" },
    { label: "Urdu", value: "Urdu" },
    { label: "Odia", value: "Odia" },
    { label: "Assamese", value: "Assamese" },
    { label: "Sindhi", value: "Sindhi" },
    { label: "Konkani", value: "Konkani" },
    { label: "Tulu", value: "Tulu" },
    { label: "Rajasthani", value: "Rajasthani" },
    { label: "Bhojpuri", value: "Bhojpuri" },
    { label: "Maithili", value: "Maithili" },
    { label: "Dogri", value: "Dogri" },
    { label: "Kashmiri", value: "Kashmiri" }
  ];

const LANGUAGE_BY_STATE = {
  "Tamil Nadu": "Tamil",
  "Kerala": "Malayalam",
  "Karnataka": "Kannada",
  "Andhra Pradesh": "Telugu",
  "Telangana": "Telugu",
  "Maharashtra": "Marathi",
  "Gujarat": "Gujarati",
  "West Bengal": "Bengali",
  "Punjab": "Punjabi",
  "Haryana": "Hindi",
  "Rajasthan": "Rajasthani",
  "Bihar": "Hindi",
  "Uttar Pradesh": "Hindi",
  "Odisha": "Odia",
  "Assam": "Assamese",
  "Delhi NCR": "Hindi",
  "Goa": "Konkani",
  "Jammu & Kashmir": "Kashmiri",
  "Madhya Pradesh": "Hindi",
  "Chhattisgarh": "Hindi",
  "Jharkhand": "Hindi",
  "Himachal Pradesh": "Hindi",
  "Uttarakhand": "Hindi"
};

const INCOME_BRACKETS = {
  "INR": {
    currencySymbol: "₹",
    countryMatch: ["India"],
    brackets: [
    { label: "Under ₹5 lakh/year", value: "INR_1", tier: 1 },
    { label: "₹5-10 lakh/year", value: "INR_2", tier: 2 },
    { label: "₹10-20 lakh/year", value: "INR_3", tier: 3 },
    { label: "₹20-35 lakh/year", value: "INR_4", tier: 4 },
    { label: "₹35-50 lakh/year", value: "INR_5", tier: 5 },
    { label: "₹50-75 lakh/year", value: "INR_6", tier: 6 },
    { label: "₹75 lakh - ₹1 crore/year", value: "INR_7", tier: 7 },
    { label: "₹1-2 crore/year", value: "INR_8", tier: 8 },
    { label: "Above ₹2 crore/year", value: "INR_9", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "USD": {
    currencySymbol: "$",
    countryMatch: ["USA"],
    brackets: [
    { label: "Under $30K/year", value: "USD_1", tier: 1 },
    { label: "$30-50K/year", value: "USD_2", tier: 2 },
    { label: "$50-75K/year", value: "USD_3", tier: 3 },
    { label: "$75-100K/year", value: "USD_4", tier: 4 },
    { label: "$100-150K/year", value: "USD_5", tier: 5 },
    { label: "$150-250K/year", value: "USD_6", tier: 7 },
    { label: "Above $250K/year", value: "USD_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "GBP": {
    currencySymbol: "£",
    countryMatch: ["UK"],
    brackets: [
    { label: "Under £25K/year", value: "GBP_1", tier: 1 },
    { label: "£25-40K/year", value: "GBP_2", tier: 2 },
    { label: "£40-60K/year", value: "GBP_3", tier: 3 },
    { label: "£60-80K/year", value: "GBP_4", tier: 4 },
    { label: "£80-120K/year", value: "GBP_5", tier: 5 },
    { label: "£120-200K/year", value: "GBP_6", tier: 7 },
    { label: "Above £200K/year", value: "GBP_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "CAD": {
    currencySymbol: "C$",
    countryMatch: ["Canada"],
    brackets: [
    { label: "Under C$40K/year", value: "CAD_1", tier: 1 },
    { label: "C$40-60K/year", value: "CAD_2", tier: 2 },
    { label: "C$60-90K/year", value: "CAD_3", tier: 3 },
    { label: "C$90-120K/year", value: "CAD_4", tier: 4 },
    { label: "C$120-180K/year", value: "CAD_5", tier: 5 },
    { label: "C$180-300K/year", value: "CAD_6", tier: 7 },
    { label: "Above C$300K/year", value: "CAD_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "AED": {
    currencySymbol: "AED",
    countryMatch: ["UAE"],
    brackets: [
    { label: "Under AED 100K/year", value: "AED_1", tier: 1 },
    { label: "AED 100-200K/year", value: "AED_2", tier: 2 },
    { label: "AED 200-350K/year", value: "AED_3", tier: 3 },
    { label: "AED 350-500K/year", value: "AED_4", tier: 4 },
    { label: "AED 500-750K/year", value: "AED_5", tier: 5 },
    { label: "AED 750K-1M/year", value: "AED_6", tier: 7 },
    { label: "Above AED 1M/year", value: "AED_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "SGD": {
    currencySymbol: "S$",
    countryMatch: ["Singapore"],
    brackets: [
    { label: "Under S$40K/year", value: "SGD_1", tier: 1 },
    { label: "S$40-70K/year", value: "SGD_2", tier: 2 },
    { label: "S$70-100K/year", value: "SGD_3", tier: 3 },
    { label: "S$100-150K/year", value: "SGD_4", tier: 4 },
    { label: "S$150-250K/year", value: "SGD_5", tier: 5 },
    { label: "S$250-400K/year", value: "SGD_6", tier: 7 },
    { label: "Above S$400K/year", value: "SGD_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "SAR": {
    currencySymbol: "SAR",
    countryMatch: ["Saudi Arabia"],
    brackets: [
    { label: "Under SAR 80K/year", value: "SAR_1", tier: 1 },
    { label: "SAR 80-150K/year", value: "SAR_2", tier: 2 },
    { label: "SAR 150-250K/year", value: "SAR_3", tier: 3 },
    { label: "SAR 250-400K/year", value: "SAR_4", tier: 4 },
    { label: "SAR 400-600K/year", value: "SAR_5", tier: 5 },
    { label: "SAR 600K-1M/year", value: "SAR_6", tier: 7 },
    { label: "Above SAR 1M/year", value: "SAR_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "QAR": {
    currencySymbol: "QAR",
    countryMatch: ["Qatar"],
    brackets: [
    { label: "Under QAR 100K/year", value: "QAR_1", tier: 1 },
    { label: "QAR 100-200K/year", value: "QAR_2", tier: 2 },
    { label: "QAR 200-350K/year", value: "QAR_3", tier: 3 },
    { label: "QAR 350-500K/year", value: "QAR_4", tier: 4 },
    { label: "QAR 500-750K/year", value: "QAR_5", tier: 5 },
    { label: "QAR 750K-1.2M/year", value: "QAR_6", tier: 7 },
    { label: "Above QAR 1.2M/year", value: "QAR_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "AUD": {
    currencySymbol: "A$",
    countryMatch: ["Australia", "New Zealand"],
    brackets: [
    { label: "Under A$40K/year", value: "AUD_1", tier: 1 },
    { label: "A$40-70K/year", value: "AUD_2", tier: 2 },
    { label: "A$70-100K/year", value: "AUD_3", tier: 3 },
    { label: "A$100-150K/year", value: "AUD_4", tier: 4 },
    { label: "A$150-250K/year", value: "AUD_5", tier: 5 },
    { label: "A$250-400K/year", value: "AUD_6", tier: 7 },
    { label: "Above A$400K/year", value: "AUD_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "EUR": {
    currencySymbol: "€",
    countryMatch: ["Germany", "Netherlands", "Ireland"],
    brackets: [
    { label: "Under €30K/year", value: "EUR_1", tier: 1 },
    { label: "€30-50K/year", value: "EUR_2", tier: 2 },
    { label: "€50-75K/year", value: "EUR_3", tier: 3 },
    { label: "€75-100K/year", value: "EUR_4", tier: 4 },
    { label: "€100-150K/year", value: "EUR_5", tier: 5 },
    { label: "€150-250K/year", value: "EUR_6", tier: 7 },
    { label: "Above €250K/year", value: "EUR_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
  "DEFAULT": {
    currencySymbol: "$",
    countryMatch: [],
    brackets: [
    { label: "Under $30K/year", value: "DEF_1", tier: 1 },
    { label: "$30-50K/year", value: "DEF_2", tier: 2 },
    { label: "$50-75K/year", value: "DEF_3", tier: 3 },
    { label: "$75-100K/year", value: "DEF_4", tier: 4 },
    { label: "$100-150K/year", value: "DEF_5", tier: 5 },
    { label: "$150-250K/year", value: "DEF_6", tier: 7 },
    { label: "Above $250K/year", value: "DEF_7", tier: 9 },
    { label: "Prefer not to say", value: "prefer_not_to_say", tier: null }
  ]
  },
};

const COUNTRY_CURRENCY_MAP = {
  "India": "INR",
  "USA": "USD",
  "UK": "GBP",
  "Canada": "CAD",
  "UAE": "AED",
  "Singapore": "SGD",
  "Saudi Arabia": "SAR",
  "Qatar": "QAR",
  "Australia": "AUD",
  "New Zealand": "AUD",
  "Germany": "EUR",
  "Netherlands": "EUR",
  "Ireland": "EUR",
  "Kuwait": "AED",
  "Oman": "AED",
  "Bahrain": "AED",
  "Malaysia": "DEFAULT",
  "South Africa": "DEFAULT",
  "Kenya": "DEFAULT",
  "_default": "DEFAULT"
};

const CASTES = {
  "Hindu": {
    master: ["Brahmin", "Agarwal", "Baniya", "Jat", "Kayastha", "Kshatriya", "Maratha", "Patel", "Rajput", "Reddy", "Nair", "Iyer", "Iyengar", "Gupta", "Khatri", "Arora", "Sindhi", "Lingayat", "Yadav", "Nadar", "Thevar", "Gounder", "Mudaliar", "Pillai", "Vanniyar", "Chettiar", "Namboodiri", "Menon", "Ezhava", "Vokkaliga", "Gowda", "Kamma", "Kapu", "Velama", "Naidu", "Vysya", "Kunbi", "Mali", "Bhumihar", "Kurmi", "Mahishya", "Baidya", "Saini", "Gurjar", "Meena", "Lohana", "Scheduled Caste", "Scheduled Tribe", "Other", "Prefer not to say"],
    byState: {
      "Tamil Nadu": ["Brahmin", "Iyer", "Iyengar", "Nadar", "Thevar", "Gounder", "Mudaliar", "Pillai", "Vanniyar", "Chettiar", "Yadav", "Scheduled Caste", "Scheduled Tribe"],
      "Kerala": ["Nair", "Namboodiri", "Menon", "Ezhava", "Brahmin", "Pillai", "Scheduled Caste", "Scheduled Tribe"],
      "Karnataka": ["Brahmin", "Lingayat", "Vokkaliga", "Gowda", "Reddy", "Scheduled Caste", "Scheduled Tribe"],
      "Andhra Pradesh": ["Reddy", "Kamma", "Kapu", "Brahmin", "Velama", "Naidu", "Vysya", "Yadav", "Scheduled Caste", "Scheduled Tribe"],
      "Telangana": ["Reddy", "Kamma", "Velama", "Brahmin", "Naidu", "Vysya", "Yadav", "Scheduled Caste", "Scheduled Tribe"],
      "Maharashtra": ["Maratha", "Brahmin", "Kunbi", "Mali", "Baniya", "Scheduled Caste", "Scheduled Tribe"],
      "Gujarat": ["Patel", "Brahmin", "Baniya", "Rajput", "Lohana", "Kshatriya", "Scheduled Caste", "Scheduled Tribe"],
      "Rajasthan": ["Rajput", "Brahmin", "Baniya", "Jat", "Agarwal", "Meena", "Gurjar", "Yadav", "Scheduled Caste", "Scheduled Tribe"],
      "Punjab": ["Jat", "Khatri", "Arora", "Brahmin", "Yadav", "Saini", "Scheduled Caste"],
      "Haryana": ["Jat", "Brahmin", "Yadav", "Rajput", "Baniya", "Gurjar", "Saini", "Scheduled Caste"],
      "Delhi NCR": ["Brahmin", "Agarwal", "Baniya", "Jat", "Khatri", "Arora", "Yadav", "Gupta", "Kayastha", "Rajput", "Sindhi", "Scheduled Caste"],
      "Uttar Pradesh": ["Brahmin", "Yadav", "Rajput", "Bhumihar", "Kayastha", "Kurmi", "Baniya", "Jat", "Gupta", "Scheduled Caste", "Scheduled Tribe"],
      "Bihar": ["Brahmin", "Yadav", "Rajput", "Bhumihar", "Kayastha", "Kurmi", "Baniya", "Scheduled Caste", "Scheduled Tribe"],
      "West Bengal": ["Brahmin", "Kayastha", "Baidya", "Mahishya", "Baniya", "Scheduled Caste", "Scheduled Tribe"],
      "Madhya Pradesh": ["Brahmin", "Rajput", "Yadav", "Baniya", "Scheduled Caste", "Scheduled Tribe"],
      "Odisha": ["Brahmin", "Kshatriya", "Baniya", "Scheduled Caste", "Scheduled Tribe"],
      "Jharkhand": ["Brahmin", "Yadav", "Rajput", "Kurmi", "Scheduled Caste", "Scheduled Tribe"],
      "Chhattisgarh": ["Brahmin", "Yadav", "Rajput", "Scheduled Caste", "Scheduled Tribe"],
      "Goa": ["Brahmin", "Kshatriya", "Baniya", "Scheduled Caste"],
      "Assam": ["Brahmin", "Kayastha", "Scheduled Caste", "Scheduled Tribe"],
      "Uttarakhand": ["Brahmin", "Rajput", "Baniya", "Scheduled Caste"],
      "Himachal Pradesh": ["Brahmin", "Rajput", "Scheduled Caste"],
      "Jammu & Kashmir": ["Brahmin", "Rajput", "Scheduled Caste"],
    },
    default: ["Brahmin", "Agarwal", "Baniya", "Jat", "Kayastha", "Kshatriya", "Maratha", "Patel", "Rajput", "Reddy", "Nair", "Iyer", "Iyengar", "Gupta", "Khatri", "Arora", "Sindhi", "Lingayat", "Yadav", "Scheduled Caste", "Scheduled Tribe"]
  },
  "Jain": {
    master: ["Agarwal", "Baniya", "Oswal", "Porwal", "Shrimal", "Khandelwal", "Other", "Prefer not to say"],
    byState: {},
    default: ["Agarwal", "Baniya", "Oswal", "Porwal", "Shrimal", "Khandelwal"]
  },
  "Sikh": {
    master: ["Jat Sikh", "Khatri Sikh", "Arora Sikh", "Ramgarhia", "Saini", "Ravidasia", "Mazhabi", "Other", "Prefer not to say"],
    byState: {},
    default: ["Jat Sikh", "Khatri Sikh", "Arora Sikh", "Ramgarhia", "Saini", "Ravidasia", "Mazhabi"]
  },
};

const HEIGHT_OPTIONS = {
  "Female": [
    {
      "label": "Below 5'2\" (157 cm)",
      "value": "155"
    },
    {
      "label": "5'2\" (157 cm)",
      "value": "157"
    },
    {
      "label": "5'3\" (160 cm)",
      "value": "160"
    },
    {
      "label": "5'4\" (163 cm)",
      "value": "163"
    },
    {
      "label": "5'5\" (165 cm)",
      "value": "165"
    },
    {
      "label": "5'6\" (168 cm)",
      "value": "168"
    },
    {
      "label": "5'7\" (170 cm)",
      "value": "170"
    },
    {
      "label": "Above 5'7\" (173 cm)",
      "value": "173"
    }
  ],
  "Male": [
    {
      "label": "Below 5'5\" (165 cm)",
      "value": "163"
    },
    {
      "label": "5'5\" (165 cm)",
      "value": "165"
    },
    {
      "label": "5'6\" (168 cm)",
      "value": "168"
    },
    {
      "label": "5'7\" (170 cm)",
      "value": "170"
    },
    {
      "label": "5'8\" (173 cm)",
      "value": "173"
    },
    {
      "label": "5'9\" (175 cm)",
      "value": "175"
    },
    {
      "label": "5'10\" (178 cm)",
      "value": "178"
    },
    {
      "label": "5'11\" (180 cm)",
      "value": "180"
    },
    {
      "label": "6'0\" (183 cm)",
      "value": "183"
    },
    {
      "label": "6'1\" (185 cm)",
      "value": "185"
    },
    {
      "label": "6'2\" (188 cm)",
      "value": "188"
    },
    {
      "label": "6'3\" (191 cm)",
      "value": "191"
    },
    {
      "label": "Above 6'3\" (193 cm)",
      "value": "193"
    }
  ]
};

const WEIGHT_OPTIONS = {
  "Female": [
    {
      "label": "Below 45 kg (99 lbs)",
      "value": "42"
    },
    {
      "label": "45-50 kg (99-110 lbs)",
      "value": "47"
    },
    {
      "label": "50-55 kg (110-121 lbs)",
      "value": "52"
    },
    {
      "label": "55-60 kg (121-132 lbs)",
      "value": "57"
    },
    {
      "label": "60-65 kg (132-143 lbs)",
      "value": "62"
    },
    {
      "label": "65-70 kg (143-154 lbs)",
      "value": "67"
    },
    {
      "label": "70-75 kg (154-165 lbs)",
      "value": "72"
    },
    {
      "label": "75-80 kg (165-176 lbs)",
      "value": "77"
    },
    {
      "label": "Above 80 kg (176 lbs)",
      "value": "85"
    }
  ],
  "Male": [
    {
      "label": "Below 60 kg (132 lbs)",
      "value": "57"
    },
    {
      "label": "60-65 kg (132-143 lbs)",
      "value": "62"
    },
    {
      "label": "65-70 kg (143-154 lbs)",
      "value": "67"
    },
    {
      "label": "70-75 kg (154-165 lbs)",
      "value": "72"
    },
    {
      "label": "75-80 kg (165-176 lbs)",
      "value": "77"
    },
    {
      "label": "80-85 kg (176-187 lbs)",
      "value": "82"
    },
    {
      "label": "85-90 kg (187-198 lbs)",
      "value": "87"
    },
    {
      "label": "90-100 kg (198-220 lbs)",
      "value": "95"
    },
    {
      "label": "Above 100 kg (220 lbs)",
      "value": "105"
    }
  ]
};

const DIET_OPTIONS = [
    { label: "Strict vegetarian (no onion/garlic)", value: "Strict vegetarian" },
    { label: "Vegetarian", value: "Vegetarian" },
    { label: "Eggetarian", value: "Eggetarian" },
    { label: "Occasionally non-veg", value: "Occasionally non-veg" },
    { label: "Non-veg", value: "Non-veg" },
    { label: "Vegan", value: "Vegan" },
    { label: "Jain", value: "Jain" },
    { label: "Halal only", value: "Halal only" },
    { label: "Other", value: "Other" }
  ];

const DIET_HIERARCHY = ["Jain", "Strict vegetarian", "Vegan", "Vegetarian", "Eggetarian", "Occasionally non-veg", "Halal only", "Non-veg", "Other"];

const DIET_GATE_RULES = {
  "Same as mine": "must_match_exact",
  "Any vegetarian": "eliminates: [Non-veg, Occasionally non-veg, Halal only]",
  "Vegetarian only": "allows: [Jain, Strict vegetarian, Vegan, Vegetarian]",
  "Doesn't matter": "passes_all"
};

const FAMILY_STATUS_BRACKETS = {
  "India": [
    {
      "label": "Less than ₹10 lakh annual income",
      "value": "tier_1",
      "tier": 1
    },
    {
      "label": "₹10-30 lakh annual income + some assets",
      "value": "tier_2",
      "tier": 2
    },
    {
      "label": "₹30-70 lakh annual income + assets",
      "value": "tier_3",
      "tier": 3
    },
    {
      "label": "₹70 lakh+ annual income + significant assets",
      "value": "tier_4",
      "tier": 4
    },
    {
      "label": "Assets over ₹10 crore",
      "value": "tier_5",
      "tier": 5
    },
    {
      "label": "Prefer not to say",
      "value": "Prefer not to say",
      "tier": null
    }
  ],
  "outside_india": [
    {
      "label": "Middle class",
      "value": "tier_2",
      "tier": 2
    },
    {
      "label": "Upper middle class",
      "value": "tier_3",
      "tier": 3
    },
    {
      "label": "Affluent",
      "value": "tier_4",
      "tier": 4
    },
    {
      "label": "Wealthy",
      "value": "tier_5",
      "tier": 5
    },
    {
      "label": "Prefer not to say",
      "value": "Prefer not to say",
      "tier": null
    }
  ]
};

const EDUCATION_LEVELS = [
    { label: "High school", value: "High school" },
    { label: "Diploma", value: "Diploma" },
    { label: "Bachelor's", value: "Bachelor's" },
    { label: "Master's", value: "Master's" },
    { label: "Doctorate / PhD", value: "Doctorate / PhD" },
    { label: "Professional (CA, CS, MBBS, LLB)", value: "Professional" }
  ];

const EDUCATION_FIELDS = ["Engineering / IT", "Medicine / Healthcare", "Business / MBA", "Law", "Finance / CA / CS", "Arts / Humanities", "Science", "Design / Architecture", "Government / Civil Services", "Other"];

const OCCUPATION_SECTORS = ["Tech / IT", "Finance / Banking", "Consulting", "Healthcare", "Manufacturing", "Media / Entertainment", "Education", "Government / Public sector", "Professional (Doctor, Lawyer, CA)", "Business / Self-employed", "Startup", "Retail / Hospitality", "Not working", "Student", "Other"];

const RELIGION_LIST = ["Hindu", "Muslim", "Sikh", "Jain", "Christian", "Buddhist", "Parsi", "No religion", "Other"];
const RELIGIONS_WITH_CASTE = ["Hindu", "Jain", "Sikh"];
const RELIGIONS_WITH_PRACTICE = ["Hindu", "Muslim", "Sikh", "Jain", "Christian"];
const RELIGIONS_WITH_MANGLIK = ["Hindu", "Jain"];

const BMI_CATEGORIES = [{"label": "Underweight", "max": 18.5}, {"label": "Normal", "max": 24.9}, {"label": "Overweight", "max": 29.9}, {"label": "Obese", "max": 999}];
const BMI_SCORING = {
  "same_category": 1.0,
  "one_step": 0.5,
  "two_steps": 0.25,
  "three_steps": 0.0
};

const BIRTH_YEARS = {
  "min": 1970,
  "max": 2006
};
const AGE_RANGE = {
  "min_floor": 18,
  "min_ceiling": 50,
  "max_ceiling": 55
};

// ═══ RUNTIME RESOLVERS ═══
// These functions resolve dynamic option references at runtime.

function getCastesByReligionAndState(religion, raisedInState) {
  const religionData = CASTES[religion];
  if (!religionData) return null;

  // Get state-priority castes or default
  const stateCastes = (religionData.byState && religionData.byState[raisedInState])
    || religionData.default;

  // Build ordered list: state priority first, then remaining master entries
  const seen = new Set(stateCastes);
  const remaining = religionData.master.filter(c => !seen.has(c) && c !== "Other" && c !== "Prefer not to say");
  const ordered = [...stateCastes, ...remaining, "Other", "Prefer not to say"];

  return ordered.map(c => ({ label: c, value: c }));
}

function getIncomeBrackets(country) {
  const currency = COUNTRY_CURRENCY_MAP[country] || COUNTRY_CURRENCY_MAP._default || "DEFAULT";
  return INCOME_BRACKETS[currency]?.brackets || INCOME_BRACKETS.DEFAULT.brackets;
}

function getIncomeBracketsWithDoesntMatter(country) {
  const brackets = getIncomeBrackets(country);
  return [{ label: "Doesn't matter", value: "Doesn't matter", tier: null }, ...brackets.filter(b => b.value !== "prefer_not_to_say")];
}

function getLanguagesSuggested(raisedInState) {
  const suggested = LANGUAGE_BY_STATE[raisedInState];
  if (!suggested) return LANGUAGES_ALL;
  // Put suggested language first
  const reordered = [
    LANGUAGES_ALL.find(l => l.value === suggested),
    ...LANGUAGES_ALL.filter(l => l.value !== suggested)
  ].filter(Boolean);
  return reordered;
}

function getLanguagesMinusMother(motherTongue) {
  return LANGUAGES_ALL.filter(l => l.value !== motherTongue);
}

function getHeightForGender(gender) {
  return (HEIGHT_OPTIONS[gender] || HEIGHT_OPTIONS.Male).map(h => ({ label: h.label, value: h.value }));
}

function getHeightOppositeGender(gender) {
  const opp = gender === "Male" ? "Female" : "Male";
  return (HEIGHT_OPTIONS[opp] || HEIGHT_OPTIONS.Female).map(h => ({ label: h.label, value: h.value }));
}

function getWeightForGender(gender) {
  return (WEIGHT_OPTIONS[gender] || WEIGHT_OPTIONS.Male).map(w => ({ label: w.label, value: w.value }));
}

function getFamilyStatusBrackets(locationType) {
  return locationType === "Outside India"
    ? FAMILY_STATUS_BRACKETS.outside_india
    : FAMILY_STATUS_BRACKETS.India;
}

function getBirthYears() {
  const years = [];
  for (let y = BIRTH_YEARS.max; y >= BIRTH_YEARS.min; y--) {
    years.push({ label: String(y), value: String(y) });
  }
  return years;
}

function getAgeRangeMin() {
  const ages = [];
  for (let a = AGE_RANGE.min_floor; a <= AGE_RANGE.min_ceiling; a++) {
    ages.push({ label: String(a), value: String(a) });
  }
  return ages;
}

function getAgeRangeMax(minAge) {
  const start = minAge || AGE_RANGE.min_floor;
  const ages = [];
  for (let a = start; a <= AGE_RANGE.max_ceiling; a++) {
    ages.push({ label: String(a), value: String(a) });
  }
  return ages;
}

/**
 * Resolve dynamic options for a question based on current answers.
 * Returns the options array, or null if the question should use its
 * static options or be skipped.
 */
function resolveOptions(questionId, answers) {
  const q = QUESTIONS[QUESTION_INDEX[questionId]];
  if (!q) return null;

  const religion = answers.religion;
  const gender = answers.gender;
  const state = answers.raised_in_state;
  const locationType = answers._location_type;
  const country = answers.country_current;

  // Dynamic option references
  const opts = q.options;
  if (typeof opts !== "string") return null; // static options, no resolution needed

  switch (opts) {
    case "birth_years":            return getBirthYears();
    case "states_india":           return STATES_INDIA;
    case "states_india_full":      return STATES_INDIA_FULL;
    case "countries":              return COUNTRIES;
    case "languages_minus_mother_tongue": return getLanguagesMinusMother(answers.mother_tongue);
    case "height_by_gender":       return getHeightForGender(gender);
    case "weight_by_gender":       return getWeightForGender(gender);
    case "height_opposite_gender": return getHeightOppositeGender(gender);
    case "castes_by_religion_and_state": return getCastesByReligionAndState(religion, state);
    case "income_by_location":     return getIncomeBrackets(country || (locationType === "India" ? "India" : "_default"));
    case "income_by_location_with_doesnt_matter": return getIncomeBracketsWithDoesntMatter(country || (locationType === "India" ? "India" : "_default"));
    case "age_range_min":          return getAgeRangeMin();
    case "age_range_max":          return getAgeRangeMax(parseInt(answers.pref_age_min));
    case "conditional":            return resolveConditionalOptions(questionId, answers);
    default:
      console.warn(`Unknown dynamic option reference: ${opts}`);
      return null;
  }
}

/**
 * Resolve conditional options (options that depend on prior answers).
 */
function resolveConditionalOptions(questionId, answers) {
  const q = QUESTIONS[QUESTION_INDEX[questionId]];
  if (!q || !q.optionsConditional) return null;

  const cond = q.optionsConditional;
  const gender = answers.gender;
  const locationType = answers._location_type;
  const religion = answers.religion;

  // Gender conditionals
  if (cond.if_female && gender === "Female") return cond.if_female;
  if (cond.if_male && gender === "Male") return cond.if_male;

  // Location conditionals
  if (cond.if_outside_india && locationType === "Outside India") return cond.if_outside_india;
  if (cond.if_in_india && (locationType === "India" || !locationType)) return cond.if_in_india;
  if (cond.if_india && (locationType === "India" || !locationType)) return cond.if_india;

  // Religion conditionals (e.g., practice levels)
  if (cond[religion]) return cond[religion];

  return null;
}

/**
 * Determine if a question should be skipped based on current answers.
 */
function shouldSkip(questionId, answers) {
  const q = QUESTIONS[QUESTION_INDEX[questionId]];
  if (!q) return true;

  // Gender gate
  if (q.gender && answers.gender && q.gender !== answers.gender) return true;

  // Skip-if condition
  if (!q.skipIf) return false;

  const expr = q.skipIf;
  // Evaluate common patterns
  try {
    // "field == 'value'"
    const eqMatch = expr.match(/^(\w+)\s*==\s*'([^']*)'$/);
    if (eqMatch) return answers[eqMatch[1]] === eqMatch[2];

    // "field != 'value'"
    const neqMatch = expr.match(/^(\w+)\s*!=\s*'([^']*)'$/);
    if (neqMatch) return answers[neqMatch[1]] !== neqMatch[2];

    // "field in ['a', 'b', 'c']"
    const inMatch = expr.match(/^(\w+)\s+in\s+\[(.+)\]$/);
    if (inMatch) {
      const vals = inMatch[2].split(",").map(s => s.trim().replace(/'/g, ""));
      return vals.includes(answers[inMatch[1]]);
    }

    // "field not in ['a', 'b', 'c']"
    const notInMatch = expr.match(/^(\w+)\s+not\s+in\s+\[(.+)\]$/);
    if (notInMatch) {
      const vals = notInMatch[2].split(",").map(s => s.trim().replace(/'/g, ""));
      return !vals.includes(answers[notInMatch[1]]);
    }
  } catch (e) {
    console.warn(`Failed to evaluate skip_if for ${questionId}: ${expr}`, e);
  }

  return false;
}

/**
 * Get the flow of question IDs in order, respecting skip logic and follow-ups.
 * Returns a flat array of question IDs representing the actual path for this user.
 */
function getQuestionFlow(answers) {
  const flow = [];
  const visited = new Set();

  function addQuestion(qId) {
    if (visited.has(qId)) return;
    visited.add(qId);

    if (shouldSkip(qId, answers)) return;

    flow.push(qId);

    // Add follow-ups immediately after
    const q = QUESTIONS[QUESTION_INDEX[qId]];
    if (q && q.followUps) {
      for (const fuId of q.followUps) {
        addQuestion(fuId);
      }
    }
  }

  // Walk questions in order, but skip those that are follow-ups
  // (they get added by their parent)
  const followUpIds = new Set();
  for (const q of QUESTIONS) {
    if (q.followUps) {
      for (const fu of q.followUps) {
        followUpIds.add(fu);
      }
    }
  }

  for (const q of QUESTIONS) {
    if (!followUpIds.has(q.id)) {
      addQuestion(q.id);
    }
  }

  return flow;
}

// ═══ PROXY FLOW ═══
const PROXY_QUESTIONS = [
  { field: "proxy_relation", question: "What's your relationship to them?", type: "single_select", options: [
    { label: "Parent", value: "Parent" },
    { label: "Sibling", value: "Sibling" },
    { label: "Relative", value: "Relative" },
    { label: "Friend", value: "Friend" }
  ] },
  { field: "person_name", question: "What's their name?", type: "text_input", placeholder: "Their first name" },
  { field: "person_gender", question: "Male or female?", type: "single_select", options: [
    { label: "Male", value: "Male" },
    { label: "Female", value: "Female" }
  ] },
  { field: "person_phone", question: "What's their phone number? (I'll send them a message to complete their profile.)", type: "phone_input" },
  { field: "person_age", question: "How old are they?", type: "single_select", options: "birth_years" },
  { field: "person_location", question: "Where do they live?", type: "location_tree" },
  { field: "person_religion", question: "What's their religion?", type: "single_select", options: "religion_list" },
  { field: "person_caste", question: "What's their caste/community?", type: "single_select", options: "castes_by_religion" },
  { field: "person_marital_status", question: "Marital status?", type: "single_select", options: "marital_status_list" },
  { field: "person_education", question: "Highest education?", type: "single_select", options: "education_level_list" },
  { field: "person_occupation", question: "What do they do?", type: "single_select", options: "occupation_sector_list" }
];

const PROXY_CLOSE = "Thanks! I'll send {person_name} a message at their number to complete the rest. Their answers will be private — you won't see them. I'll let you know when their profile is ready.\n\n— Masii";

// ═══ EXPORTS ═══
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    META, SECTIONS, SECTION_TRANSITIONS, SECTION_ORDER,
    INTRO, CLOSE_MESSAGE, ERROR_MESSAGES, RESUME_PROMPT, RESUME_BUTTONS,
    QUESTIONS, QUESTION_INDEX,
    COUNTRIES, STATES_INDIA, STATES_INDIA_FULL, LANGUAGES_ALL, LANGUAGE_BY_STATE,
    INCOME_BRACKETS, COUNTRY_CURRENCY_MAP, CASTES,
    HEIGHT_OPTIONS, WEIGHT_OPTIONS, DIET_OPTIONS, DIET_HIERARCHY, DIET_GATE_RULES,
    FAMILY_STATUS_BRACKETS, EDUCATION_LEVELS, EDUCATION_FIELDS, OCCUPATION_SECTORS,
    RELIGION_LIST, RELIGIONS_WITH_CASTE, RELIGIONS_WITH_PRACTICE, RELIGIONS_WITH_MANGLIK,
    BMI_CATEGORIES, BMI_SCORING, BIRTH_YEARS, AGE_RANGE,
    PROXY_QUESTIONS, PROXY_CLOSE,
    // Runtime functions
    getCastesByReligionAndState, getIncomeBrackets, getIncomeBracketsWithDoesntMatter,
    getLanguagesSuggested, getLanguagesMinusMother,
    getHeightForGender, getHeightOppositeGender, getWeightForGender,
    getFamilyStatusBrackets, getBirthYears, getAgeRangeMin, getAgeRangeMax,
    resolveOptions, resolveConditionalOptions, shouldSkip, getQuestionFlow
  };
}
