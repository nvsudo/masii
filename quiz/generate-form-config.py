#!/usr/bin/env python3
"""
Masii — YAML → form-config.js Generator

Reads:
  masii-questions.yaml       → question definitions, sections, transitions, copy
  masii-reference-data.yaml  → castes, income brackets, languages, countries, etc.

Outputs:
  form-config.generated.js   → drop-in replacement for form-config.js

Usage:
  python3 generate-form-config.py
  python3 generate-form-config.py --out ./web/form-config.js

Zero drift guarantee:
  If it's not in the YAML, it doesn't exist in the output.
  Run this after every YAML edit. Commit the output alongside the YAMLs.
"""

import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime

DEFAULT_QUESTIONS = "masii-questions.yaml"
DEFAULT_REFERENCE = "masii-reference-data.yaml"
DEFAULT_OUTPUT = "form-config.generated.js"


# ─── Helpers ────────────────────────────────────────────

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def js(val):
    """Python value → JS literal string."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, str):
        return json.dumps(val, ensure_ascii=False)
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False, indent=2)
    return json.dumps(val, ensure_ascii=False)


def opts_to_js(options):
    """Convert option list to JS array-of-objects string."""
    if isinstance(options, str):
        # Dynamic reference resolved at runtime
        return f'"{options}"'
    lines = []
    for o in options:
        if isinstance(o, str):
            lines.append(f'    {{ label: {js(o)}, value: {js(o)} }}')
        elif isinstance(o, dict):
            parts = [f'label: {js(o["label"])}', f'value: {js(o["value"])}']
            if o.get("requires_text"):
                parts.append("requires_text: true")
            if o.get("triggers"):
                parts.append(f'triggers: {js(o["triggers"])}')
            if o.get("tier") is not None:
                parts.append(f'tier: {o["tier"]}')
            elif "tier" in o:
                parts.append("tier: null")
            lines.append("    { " + ", ".join(parts) + " }")
    return "[\n" + ",\n".join(lines) + "\n  ]"


def step_to_js(step, indent=4):
    """Convert a step (step1, step2, etc.) to JS object string."""
    pad = " " * indent
    parts = []
    for key in ["text", "field", "type", "placeholder"]:
        if key in step:
            parts.append(f'{pad}  {key}: {js(step[key])}')
    if "columns" in step:
        parts.append(f'{pad}  columns: {step["columns"]}')
    if "options" in step:
        parts.append(f'{pad}  options: {opts_to_js(step["options"])}')
    return f'{pad}{{\n' + ",\n".join(parts) + f'\n{pad}}}'


# ─── Main Generation ───────────────────────────────────

def generate(questions_path, reference_path, output_path):
    q_data = load(questions_path)
    ref = load(reference_path)

    questions = q_data["questions"]
    sections = q_data["sections"]
    meta = q_data["meta"]
    intro = q_data["intro"]
    close_msg = q_data["close"]
    errors = q_data["errors"]
    resume = q_data["resume"]
    proxy = q_data.get("proxy_flow", {})
    g = q_data.get("global", {})

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(questions)

    out = []

    # ═══ Header ═══
    out.append(f"""/**
 * Masii Form Configuration — GENERATED
 * DO NOT EDIT. Source: masii-questions.yaml v{meta['version']}
 * Generated: {now} | Questions: {total}
 * Regenerate: python3 generate-form-config.py
 */
"use strict";
""")

    # ═══ Meta ═══
    out.append(f"""const META = Object.freeze({{
  version: {meta['version']},
  updated: {js(meta['updated'])},
  totalQuestions: {total},
  nameField: {js(g.get('name_field', 'preferred_name'))},
  complexionPolicy: {js(g.get('complexion', 'photo_only'))}
}});
""")

    # ═══ Sections ═══
    sec_lines = []
    for key, sec in sections.items():
        sec_lines.append(f'  {key}: {{ label: {js(sec["label"])}, subtitle: {js(sec["subtitle"])}, transition: {js(sec.get("transition"))} }}')
    out.append("const SECTIONS = Object.freeze({\n" + ",\n".join(sec_lines) + "\n});\n")

    # Derive SECTION_TRANSITIONS for convenience
    out.append("// Convenience: transitions keyed by section name")
    out.append("const SECTION_TRANSITIONS = Object.freeze(")
    out.append("  Object.fromEntries(Object.entries(SECTIONS).filter(([k, v]) => v.transition).map(([k, v]) => [k, v.transition]))")
    out.append(");\n")

    # ═══ Intro ═══
    out.append(f"""const INTRO = {{
  text: {js(intro['text'].strip())},
  button: {js(intro['button'])}
}};
""")

    # ═══ Close ═══
    out.append(f"const CLOSE_MESSAGE = {js(close_msg['text'].strip())};\n")

    # ═══ Errors ═══
    err_lines = [f'  {k}: {js(v)}' for k, v in errors.items()]
    out.append("const ERROR_MESSAGES = {\n" + ",\n".join(err_lines) + "\n};\n")

    # ═══ Resume ═══
    out.append(f"const RESUME_PROMPT = {js(resume['text'])};")
    out.append(f"const RESUME_BUTTONS = {js(resume['buttons'])};\n")

    # ═══ Questions ═══
    out.append(f"// ═══ QUESTIONS ({total}) ═══\n")
    q_strs = []
    for q in questions:
        lines = []
        lines.append(f'    id: {js(q["id"])}')
        lines.append(f'    section: {js(q["section"])}')
        lines.append(f'    field: {js(q["field"])}')
        lines.append(f'    dbTable: {js(q["db_table"])}')
        lines.append(f'    question: {js(q["question"])}')
        lines.append(f'    type: {js(q["type"])}')

        for key in ["gender", "placeholder", "helper_text", "skip_if", "gate",
                     "gate_logic", "state_context", "response_template", "done_label", "notes"]:
            if q.get(key):
                camel = key.replace("_", " ").title().replace(" ", "")
                camel = camel[0].lower() + camel[1:]
                lines.append(f'    {camel}: {js(q[key])}')

        if q.get("columns"):
            lines.append(f'    columns: {q["columns"]}')

        if q.get("has_doesnt_matter"):
            lines.append(f'    hasDoesntMatter: true')
            if q.get("doesnt_matter_label"):
                lines.append(f'    doesntMatterLabel: {js(q["doesnt_matter_label"])}')

        if q.get("follow_ups"):
            lines.append(f'    followUps: {js(q["follow_ups"])}')

        # Options
        if "options" in q:
            lines.append(f'    options: {opts_to_js(q["options"])}')
        elif "options_conditional" in q:
            lines.append(f'    optionsConditional: {js(q["options_conditional"])}')

        # Steps (multi-step questions)
        for sk in ["step1", "step2", "step3", "step1_india", "step2_india", "step2_abroad"]:
            if sk in q:
                camel_sk = sk.replace("_", " ").title().replace(" ", "")
                camel_sk = camel_sk[0].lower() + camel_sk[1:]
                lines.append(f'    {camel_sk}: {step_to_js(q[sk])}')

        # Scoring
        if q.get("scoring"):
            s = q["scoring"]
            s_lines = []
            if "rule" in s:
                s_lines.append(f'      rule: {js(s["rule"])}')
            if "note" in s:
                s_lines.append(f'      note: {js(s["note"])}')
            if "type" in s:
                s_lines.append(f'      type: {js(s["type"])}')
            if "matrix" in s:
                s_lines.append(f'      matrix: {json.dumps(s["matrix"], ensure_ascii=False, indent=8)}')
            lines.append("    scoring: {\n" + ",\n".join(s_lines) + "\n    }")

        q_strs.append("  {\n" + ",\n".join(lines) + "\n  }")

    out.append("const QUESTIONS = [\n" + ",\n\n".join(q_strs) + "\n];\n")

    # ═══ Question index (id → position) ═══
    out.append("// ═══ QUESTION INDEX ═══")
    out.append("const QUESTION_INDEX = Object.freeze({")
    for i, q in enumerate(questions):
        out.append(f'  {js(q["id"])}: {i},')
    out.append("});\n")

    # ═══ Section order ═══
    sec_keys = list(sections.keys())
    out.append(f"const SECTION_ORDER = {js(sec_keys)};\n")

    # ═══ Reference data ═══
    out.append("// ═══ REFERENCE DATA ═══\n")

    # Countries
    out.append(f"const COUNTRIES = {opts_to_js(ref['countries'])};\n")

    # States
    out.append(f"const STATES_INDIA = {opts_to_js(ref['states_india'])};\n")
    out.append(f"const STATES_INDIA_FULL = {opts_to_js(ref['states_india_full'])};\n")

    # Languages
    out.append(f"const LANGUAGES_ALL = {opts_to_js(ref['languages_all'])};\n")

    # Language by state
    out.append(f"const LANGUAGE_BY_STATE = {js(ref['language_by_state'])};\n")

    # Income brackets
    out.append("const INCOME_BRACKETS = {")
    for currency, info in ref["income_brackets"].items():
        out.append(f'  {js(currency)}: {{')
        out.append(f'    currencySymbol: {js(info["currency_symbol"])},')
        out.append(f'    countryMatch: {js(info["country_match"])},')
        out.append(f'    brackets: {opts_to_js(info["brackets"])}')
        out.append('  },')
    out.append("};\n")

    # Country → currency map
    out.append(f"const COUNTRY_CURRENCY_MAP = {js(ref['country_currency_map'])};\n")

    # Castes
    out.append("const CASTES = {")
    for religion, caste_data in ref["castes"].items():
        out.append(f'  {js(religion)}: {{')
        out.append(f'    master: {js(caste_data["master"])},')
        if caste_data.get("by_state"):
            out.append(f'    byState: {{')
            for state, castes_list in caste_data["by_state"].items():
                out.append(f'      {js(state)}: {js(castes_list)},')
            out.append(f'    }},')
        else:
            out.append(f'    byState: {{}},')
        out.append(f'    default: {js(caste_data["default"])}')
        out.append('  },')
    out.append("};\n")

    # Height/weight
    out.append(f"const HEIGHT_OPTIONS = {js(ref['height_options'])};\n")
    out.append(f"const WEIGHT_OPTIONS = {js(ref['weight_options'])};\n")

    # Diet
    out.append(f"const DIET_OPTIONS = {opts_to_js(ref['diet_options'])};\n")
    out.append(f"const DIET_HIERARCHY = {js(ref['diet_hierarchy'])};\n")
    out.append(f"const DIET_GATE_RULES = {js(ref['diet_gate_rules'])};\n")

    # Family status
    out.append(f"const FAMILY_STATUS_BRACKETS = {js(ref['family_status_brackets'])};\n")

    # Education & occupation
    out.append(f"const EDUCATION_LEVELS = {opts_to_js(ref['education_levels'])};\n")
    out.append(f"const EDUCATION_FIELDS = {js(ref['education_fields'])};\n")
    out.append(f"const OCCUPATION_SECTORS = {js(ref['occupation_sectors'])};\n")

    # Religion reference
    out.append(f"const RELIGION_LIST = {js(ref['religion_list'])};")
    out.append(f"const RELIGIONS_WITH_CASTE = {js(ref['religions_with_caste'])};")
    out.append(f"const RELIGIONS_WITH_PRACTICE = {js(ref['religions_with_practice'])};")
    out.append(f"const RELIGIONS_WITH_MANGLIK = {js(ref['religions_with_manglik'])};\n")

    # BMI
    out.append(f"const BMI_CATEGORIES = {js(ref['bmi_categories'])};")
    out.append(f"const BMI_SCORING = {js(ref['bmi_scoring'])};\n")

    # Birth years / age range
    out.append(f"const BIRTH_YEARS = {js(ref['birth_years'])};")
    out.append(f"const AGE_RANGE = {js(ref['age_range'])};\n")

    # ═══ Runtime resolvers ═══
    out.append("""// ═══ RUNTIME RESOLVERS ═══
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
    const eqMatch = expr.match(/^(\\w+)\\s*==\\s*'([^']*)'$/);
    if (eqMatch) return answers[eqMatch[1]] === eqMatch[2];

    // "field != 'value'"
    const neqMatch = expr.match(/^(\\w+)\\s*!=\\s*'([^']*)'$/);
    if (neqMatch) return answers[neqMatch[1]] !== neqMatch[2];

    // "field in ['a', 'b', 'c']"
    const inMatch = expr.match(/^(\\w+)\\s+in\\s+\\[(.+)\\]$/);
    if (inMatch) {
      const vals = inMatch[2].split(",").map(s => s.trim().replace(/'/g, ""));
      return vals.includes(answers[inMatch[1]]);
    }

    // "field not in ['a', 'b', 'c']"
    const notInMatch = expr.match(/^(\\w+)\\s+not\\s+in\\s+\\[(.+)\\]$/);
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
""")

    # ═══ Proxy flow ═══
    if proxy:
        out.append("// ═══ PROXY FLOW ═══")
        pq_lines = []
        for pq in proxy.get("questions", []):
            pq_parts = [f'field: {js(pq["field"])}', f'question: {js(pq["question"])}', f'type: {js(pq["type"])}']
            if "placeholder" in pq:
                pq_parts.append(f'placeholder: {js(pq["placeholder"])}')
            if "options" in pq:
                if isinstance(pq["options"], str):
                    pq_parts.append(f'options: {js(pq["options"])}')
                else:
                    pq_parts.append(f'options: {opts_to_js(pq["options"])}')
            pq_lines.append("  { " + ", ".join(pq_parts) + " }")
        out.append("const PROXY_QUESTIONS = [\n" + ",\n".join(pq_lines) + "\n];\n")
        out.append(f"const PROXY_CLOSE = {js(proxy.get('close', '').strip())};\n")

    # ═══ Exports ═══
    out.append("""// ═══ EXPORTS ═══
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
""")

    # Write
    content = "\n".join(out)
    Path(output_path).write_text(content, encoding="utf-8")
    print(f"\n✓ Generated {output_path}")
    print(f"  {total} questions | {len(sections)} sections | {len(ref['castes'])} religion caste trees")
    print(f"  {len(ref['income_brackets'])} currency brackets | {len(ref['countries'])} countries")
    return content


# ─── CLI ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate form-config.js from YAML")
    parser.add_argument("--questions", default=DEFAULT_QUESTIONS, help="Path to masii-questions.yaml")
    parser.add_argument("--reference", default=DEFAULT_REFERENCE, help="Path to masii-reference-data.yaml")
    parser.add_argument("--out", default=DEFAULT_OUTPUT, help="Output path for form-config.js")
    args = parser.parse_args()

    generate(args.questions, args.reference, args.out)
