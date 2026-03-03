/**
 * JODI Telegram Button Flows
 * Interactive buttons for categorical fields where accuracy matters
 * Reduces LLM parsing errors on critical demographic fields
 */

export interface ButtonOption {
  text: string;
  callback_data: string;
  value: string; // Value to store in DB
}

export interface ButtonFlow {
  field: string;
  question: string;
  options: ButtonOption[];
  required: boolean;
  tier: number;
  storage: 'column' | 'jsonb';
  table?: string;
  column?: string;
  jsonb_path?: string;
}

/**
 * TIER 1: Critical Hard Filters
 * Use buttons to ensure 100% accuracy on elimination criteria
 */
export const TIER_1_BUTTON_FLOWS: ButtonFlow[] = [
  {
    field: 'gender_identity',
    question: 'What's your gender?',
    options: [
      { text: '👨 Male', callback_data: 'gender_male', value: 'Male' },
      { text: '👩 Female', callback_data: 'gender_female', value: 'Female' },
      { text: '⚧️ Non-binary', callback_data: 'gender_nonbinary', value: 'Non-binary' },
      { text: '💬 Prefer to describe', callback_data: 'gender_custom', value: 'Custom' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'gender_identity'
  },
  
  {
    field: 'sexual_orientation',
    question: 'What's your orientation?',
    options: [
      { text: 'Straight', callback_data: 'orient_straight', value: 'Heterosexual' },
      { text: 'Gay', callback_data: 'orient_gay', value: 'Gay' },
      { text: 'Lesbian', callback_data: 'orient_lesbian', value: 'Lesbian' },
      { text: 'Bisexual', callback_data: 'orient_bi', value: 'Bisexual' },
      { text: 'Pansexual', callback_data: 'orient_pan', value: 'Pansexual' },
      { text: 'Asexual', callback_data: 'orient_ace', value: 'Asexual' },
      { text: '💬 Other', callback_data: 'orient_other', value: 'Other' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'sexual_orientation'
  },
  
  {
    field: 'religion',
    question: 'Do you practice a religion?',
    options: [
      { text: '☪️ Muslim', callback_data: 'religion_muslim', value: 'Muslim' },
      { text: '🕉️ Hindu', callback_data: 'religion_hindu', value: 'Hindu' },
      { text: '✝️ Christian', callback_data: 'religion_christian', value: 'Christian' },
      { text: '✡️ Jewish', callback_data: 'religion_jewish', value: 'Jewish' },
      { text: '☸️ Buddhist', callback_data: 'religion_buddhist', value: 'Buddhist' },
      { text: '☬ Sikh', callback_data: 'religion_sikh', value: 'Sikh' },
      { text: '🔮 Spiritual (not religious)', callback_data: 'religion_spiritual', value: 'Spiritual' },
      { text: '🚫 Atheist', callback_data: 'religion_atheist', value: 'Atheist' },
      { text: '🤷 Agnostic', callback_data: 'religion_agnostic', value: 'Agnostic' },
      { text: '💬 Other', callback_data: 'religion_other', value: 'Other' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'religion'
  },
  
  {
    field: 'children_intent',
    question: 'How do you feel about having kids?',
    options: [
      { text: '👶 Want kids', callback_data: 'kids_want', value: 'Want kids' },
      { text: '🚫 Don't want kids', callback_data: 'kids_no', value: 'Don't want kids' },
      { text: '👨‍👩‍👧 Already have kids', callback_data: 'kids_have', value: 'Already have kids' },
      { text: '🤔 Not sure yet', callback_data: 'kids_unsure', value: 'Not sure yet' },
      { text: '👶➕ Want more (have some)', callback_data: 'kids_want_more', value: 'Have kids, want more' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'children_intent'
  },
  
  {
    field: 'marital_history',
    question: 'Have you been married before?',
    options: [
      { text: '💍 Never married', callback_data: 'marital_never', value: 'Never married' },
      { text: '📄 Divorced', callback_data: 'marital_divorced', value: 'Divorced' },
      { text: '💔 Widowed', callback_data: 'marital_widowed', value: 'Widowed' },
      { text: '⚖️ Separated', callback_data: 'marital_separated', value: 'Separated' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'marital_history'
  },
  
  {
    field: 'smoking',
    question: 'Do you smoke?',
    options: [
      { text: '🚭 Never', callback_data: 'smoke_never', value: 'Never' },
      { text: '🍃 Socially', callback_data: 'smoke_social', value: 'Socially' },
      { text: '🚬 Regularly', callback_data: 'smoke_regular', value: 'Current smoker' },
      { text: '⏸️ Former smoker', callback_data: 'smoke_former', value: 'Former smoker' },
      { text: '🌿 Vape/Alternative', callback_data: 'smoke_vape', value: 'Vape only' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'smoking'
  },
  
  {
    field: 'drinking',
    question: 'How often do you drink alcohol?',
    options: [
      { text: '🚫 Never', callback_data: 'drink_never', value: 'Never' },
      { text: '🎉 Socially', callback_data: 'drink_social', value: 'Socially' },
      { text: '🍷 Occasionally', callback_data: 'drink_occasional', value: 'Occasionally' },
      { text: '🍺 Regularly', callback_data: 'drink_regular', value: 'Regularly' },
      { text: '⏸️ Former drinker', callback_data: 'drink_former', value: 'Former drinker' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'drinking'
  },
  
  {
    field: 'dietary_restrictions',
    question: 'Any dietary restrictions?',
    options: [
      { text: '🍖 None', callback_data: 'diet_none', value: 'None' },
      { text: '☪️ Halal', callback_data: 'diet_halal', value: 'Halal' },
      { text: '✡️ Kosher', callback_data: 'diet_kosher', value: 'Kosher' },
      { text: '🥕 Vegetarian', callback_data: 'diet_veg', value: 'Vegetarian' },
      { text: '🌱 Vegan', callback_data: 'diet_vegan', value: 'Vegan' },
      { text: '🥩 Pescatarian', callback_data: 'diet_pesc', value: 'Pescatarian' },
      { text: '🌾 Gluten-free', callback_data: 'diet_gf', value: 'Gluten-free' },
      { text: '💬 Other', callback_data: 'diet_other', value: 'Other' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'dietary_restrictions'
  },
  
  {
    field: 'relationship_intent',
    question: 'What are you looking for?',
    options: [
      { text: '💍 Marriage', callback_data: 'intent_marriage', value: 'Marriage' },
      { text: '❤️ Long-term relationship', callback_data: 'intent_ltr', value: 'Long-term committed' },
      { text: '🤔 Open to either', callback_data: 'intent_open', value: 'Open to marriage or LTR' },
      { text: '📅 Dating to see where it goes', callback_data: 'intent_dating', value: 'Dating, open to serious' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'relationship_intent'
  },
  
  {
    field: 'relationship_timeline',
    question: 'What's your timeline?',
    options: [
      { text: '⚡ Ready now', callback_data: 'timeline_now', value: 'Ready now' },
      { text: '📅 Within a year', callback_data: 'timeline_1yr', value: 'Within a year' },
      { text: '🕐 1-2 years', callback_data: 'timeline_2yr', value: '1-2 years' },
      { text: '🔮 2+ years', callback_data: 'timeline_later', value: '2+ years' },
      { text: '🌊 Just exploring', callback_data: 'timeline_explore', value: 'Exploring' }
    ],
    required: true,
    tier: 1,
    storage: 'column',
    table: 'users',
    column: 'relationship_timeline'
  }
];

/**
 * TIER 2: Lifestyle Buttons (Optional, but improve accuracy)
 */
export const TIER_2_BUTTON_FLOWS: ButtonFlow[] = [
  {
    field: 'work_style',
    question: 'What's your work environment like?',
    options: [
      { text: '🏢 Corporate', callback_data: 'work_corp', value: 'Corporate' },
      { text: '🚀 Startup', callback_data: 'work_startup', value: 'Startup' },
      { text: '💼 Freelance', callback_data: 'work_freelance', value: 'Freelance' },
      { text: '🏛️ Government', callback_data: 'work_govt', value: 'Government' },
      { text: '🎓 Academic', callback_data: 'work_academic', value: 'Academic' },
      { text: '💬 Other', callback_data: 'work_other', value: 'Other' }
    ],
    required: false,
    tier: 2,
    storage: 'jsonb',
    table: 'user_signals',
    jsonb_path: 'lifestyle.work_style'
  },
  
  {
    field: 'exercise_fitness',
    question: 'How active are you?',
    options: [
      { text: '🏋️ Gym regular (4+ days/week)', callback_data: 'fit_gym', value: 'Gym regular' },
      { text: '⚽ Sports / active lifestyle', callback_data: 'fit_sports', value: 'Sports enthusiast' },
      { text: '🚶 Moderate (walks, hikes)', callback_data: 'fit_moderate', value: 'Moderately active' },
      { text: '🧘 Yoga / Pilates', callback_data: 'fit_yoga', value: 'Yoga/Pilates' },
      { text: '🏠 Not very active', callback_data: 'fit_low', value: 'Sedentary' }
    ],
    required: false,
    tier: 2,
    storage: 'jsonb',
    table: 'user_signals',
    jsonb_path: 'lifestyle.exercise_fitness'
  },
  
  {
    field: 'pet_ownership',
    question: 'How do you feel about pets?',
    options: [
      { text: '🐕 Have dog(s)', callback_data: 'pet_dog', value: 'Has dogs' },
      { text: '🐈 Have cat(s)', callback_data: 'pet_cat', value: 'Has cats' },
      { text: '🐾 Have other pets', callback_data: 'pet_other', value: 'Has other pets' },
      { text: '💚 Want pets', callback_data: 'pet_want', value: 'Wants pets' },
      { text: '🚫 No pets', callback_data: 'pet_no', value: 'No pets' },
      { text: '🤧 Allergic', callback_data: 'pet_allergic', value: 'Allergic to pets' }
    ],
    required: false,
    tier: 2,
    storage: 'jsonb',
    table: 'user_signals',
    jsonb_path: 'lifestyle.pet_ownership'
  },
  
  {
    field: 'love_language',
    question: 'What's your primary love language?',
    options: [
      { text: '🗣️ Words of Affirmation', callback_data: 'love_words', value: 'Words of Affirmation' },
      { text: '⏰ Quality Time', callback_data: 'love_time', value: 'Quality Time' },
      { text: '🎁 Receiving Gifts', callback_data: 'love_gifts', value: 'Receiving Gifts' },
      { text: '🤝 Acts of Service', callback_data: 'love_acts', value: 'Acts of Service' },
      { text: '🤗 Physical Touch', callback_data: 'love_touch', value: 'Physical Touch' }
    ],
    required: false,
    tier: 2,
    storage: 'jsonb',
    table: 'user_signals',
    jsonb_path: 'relationship_style.love_language'
  }
];

/**
 * TIER 4: Post-Match Feedback Buttons
 */
export const TIER_4_BUTTON_FLOWS: ButtonFlow[] = [
  {
    field: 'date_willingness',
    question: 'Would you like to meet {match_name}?',
    options: [
      { text: '🤩 Yes, excited!', callback_data: 'will_eager', value: 'Eager' },
      { text: '👍 Yes, open to it', callback_data: 'will_willing', value: 'Willing' },
      { text: '🤔 Maybe, need to think', callback_data: 'will_neutral', value: 'Neutral' },
      { text: '😬 Reluctant', callback_data: 'will_reluctant', value: 'Reluctant' },
      { text: '❌ No thanks', callback_data: 'will_declined', value: 'Declined' }
    ],
    required: true,
    tier: 4,
    storage: 'column',
    table: 'matches',
    column: 'date_willingness'
  },
  
  {
    field: 'first_impression',
    question: 'First impression of {match_name}?',
    options: [
      { text: '🤩 Very excited', callback_data: 'impress_excited', value: 'Excited' },
      { text: '😊 Positive', callback_data: 'impress_positive', value: 'Positive' },
      { text: '😐 Neutral', callback_data: 'impress_neutral', value: 'Neutral' },
      { text: '😕 Disappointed', callback_data: 'impress_disappointed', value: 'Disappointed' },
      { text: '😮 Surprised (tell me more)', callback_data: 'impress_surprised', value: 'Surprised' }
    ],
    required: true,
    tier: 4,
    storage: 'jsonb',
    table: 'matches',
    column: 'user_first_impression'
  }
];

/**
 * Helper function to generate Telegram inline keyboard markup
 */
export function generateButtonMarkup(flow: ButtonFlow): any {
  return {
    inline_keyboard: flow.options.map(opt => [{
      text: opt.text,
      callback_data: opt.callback_data
    }])
  };
}

/**
 * Parse callback data to field value
 */
export function parseCallbackData(callback_data: string, flows: ButtonFlow[]): {
  field: string;
  value: string;
  storage: 'column' | 'jsonb';
  table?: string;
  column?: string;
  jsonb_path?: string;
} | null {
  for (const flow of flows) {
    const option = flow.options.find(opt => opt.callback_data === callback_data);
    if (option) {
      return {
        field: flow.field,
        value: option.value,
        storage: flow.storage,
        table: flow.table,
        column: flow.column,
        jsonb_path: flow.jsonb_path
      };
    }
  }
  return null;
}

/**
 * All button flows combined
 */
export const ALL_BUTTON_FLOWS = [
  ...TIER_1_BUTTON_FLOWS,
  ...TIER_2_BUTTON_FLOWS,
  ...TIER_4_BUTTON_FLOWS
];
