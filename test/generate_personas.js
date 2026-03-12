const fs = require('fs');

// Helpers for random generation
const randomChoice = (arr) => arr[Math.floor(Math.random() * arr.length)];
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomBoolean = (probability = 0.5) => Math.random() < probability;
const generateId = () => Math.random().toString(36).substring(2, 9);

// Data Dictionaries (based on masii-reference-data.yaml)
const currencies = {
    'USA': 'USD', 'UK': 'GBP', 'Canada': 'CAD', 'Australia': 'AUD',
    'UAE': 'AED', 'Singapore': 'SGD', 'Germany': 'EUR', 'Qatar': 'QAR'
};

const topNriCountries = ['USA', 'UK', 'Canada', 'Australia', 'UAE', 'Singapore', 'Germany'];
const topMetroStates = ['Karnataka', 'Maharashtra', 'Delhi NCR', 'Haryana', 'Telangana'];
const traditionalStates = ['Tamil Nadu', 'Andhra Pradesh', 'Gujarat', 'Uttar Pradesh', 'Rajasthan'];
const genericReligions = ['Hindu', 'Muslim', 'Sikh', 'Jain', 'Christian'];

const languageMap = {
    'Tamil Nadu': 'Tamil', 'Karnataka': 'Kannada', 'Andhra Pradesh': 'Telugu',
    'Telangana': 'Telugu', 'Maharashtra': 'Marathi', 'Gujarat': 'Gujarati',
    'Delhi NCR': 'Hindi', 'Haryana': 'Hindi', 'Uttar Pradesh': 'Hindi', 'Rajasthan': 'Hindi'
};

const casteMap = {
    'Hindu': {
        'Tamil Nadu': ['Brahmin', 'Iyer', 'Iyengar', 'Nadar', 'Thevar', 'Gounder', 'Mudaliar'],
        'Karnataka': ['Brahmin', 'Lingayat', 'Vokkaliga', 'Gowda', 'Reddy'],
        'Andhra Pradesh': ['Reddy', 'Kamma', 'Kapu', 'Brahmin', 'Velama'],
        'Telangana': ['Reddy', 'Kamma', 'Velama', 'Brahmin'],
        'Maharashtra': ['Maratha', 'Brahmin', 'Kunbi'],
        'Gujarat': ['Patel', 'Brahmin', 'Baniya', 'Rajput'],
        'Delhi NCR': ['Brahmin', 'Agarwal', 'Baniya', 'Jat', 'Khatri', 'Arora'],
        'USA': ['Brahmin', 'Reddy', 'Patel', 'Agarwal', 'Iyer', 'Baniya'] // NRI defaults
    },
    'Jain': ['Agarwal', 'Baniya', 'Oswal', 'Porwal'],
    'Sikh': ['Jat Sikh', 'Khatri Sikh', 'Arora Sikh', 'Ramgarhia']
};

const eduLevels = ["High school", "Diploma", "Bachelor's", "Master's", "Doctorate / PhD", "Professional"];
const topEduLevels = ["Master's", "Doctorate / PhD", "Professional"];
const careerSectors = ["Tech / IT", "Finance / Banking", "Consulting", "Healthcare", "Business / Self-employed"];

// Generator base template
const createBasePersona = () => {
    const gender = randomChoice(['Male', 'Female']);
    const intent = randomChoice(['self', 'self', 'self', 'proxy']); // mostly self
    const dob = { birth_year: String(randomInt(1985, 2000)), birth_month: String(randomInt(1, 12)) };

    // Default weights/heights
    const height_cm = gender === 'Male' ? String(randomInt(170, 185)) : String(randomInt(155, 170));
    const weight_kg = gender === 'Male' ? String(randomInt(67, 85)) : String(randomInt(52, 67));

    return {
        _id: generateId(),
        intent,
        preferred_name: `Test_${generateId()}`,
        gender,
        date_of_birth: dob,
        height_cm,
        weight_kg,
        // These will be overridden by the pool specific logic
        location_type: 'India',
        current_location: { location_type: 'India', state_india: 'Maharashtra', city_current: 'Mumbai' },
        raised_in_type: 'India',
        raised_in: { raised_in_type: 'India', raised_in_state: 'Maharashtra', raised_in_city: 'Pune' },
        marital_status: 'Never married',
        children_existing: 'No'
    };
};

// ==========================================
// POOL 1: NRI / Global Diaspora
// ==========================================
const createNriPersona = () => {
    const p = createBasePersona();
    const isBornAbroad = randomBoolean(0.3); // 30% born abroad
    const country = randomChoice(topNriCountries);
    const currency = currencies[country];

    // Location
    p.current_location = { location_type: 'Outside India', country_current: country, city_current: 'Metropolis' };

    if (isBornAbroad) {
        p.raised_in = { raised_in_type: 'Outside India', raised_in_country: country, raised_in_city: 'Metropolis' };
        p.mother_tongue = 'English';
        p.languages_spoken = ['Hindi'];
        p.pref_raised_in = randomChoice(['Same country as me', 'Raised abroad (any country)', 'Raised in India is fine too']);
    } else {
        const homeState = randomChoice(['Gujarat', 'Andhra Pradesh', 'Tamil Nadu', 'Delhi NCR', 'Punjab']);
        p.raised_in = { raised_in_type: 'India', raised_in_state: homeState, raised_in_city: 'Hometown' };
        p.mother_tongue = languageMap[homeState] || 'Hindi';
        p.languages_spoken = ['English'];
        p.pref_raised_in = 'Raised in India is fine too';
    }

    // Religion & Caste (Often flexible)
    p.religion = randomChoice(['Hindu', 'Hindu', 'Sikh', 'Muslim']); // Skew Hindu
    if (casteMap[p.religion]) {
        const casteList = casteMap[p.religion][p.raised_in.raised_in_state] || casteMap[p.religion]['USA'] || casteMap[p.religion];
        p.caste_community = randomChoice(casteList);
        p.caste_importance = randomChoice(['Doesn\'t matter', 'Prefer same, open to others']);
    }

    // High Education / High Income
    p.education_level = randomChoice(topEduLevels);
    p.occupation_sector = randomChoice(["Tech / IT", "Finance / Banking", "Consulting", "Healthcare"]);
    p.annual_income = `${currency}_${randomInt(5, 7)}`; // High tiers

    p.pref_education_level = randomChoice(["Master's or higher", "Professional degree", "Doesn't matter"]);
    // Income pref matching own currency usually
    p.pref_income_min = randomBoolean(0.7) ? `${currency}_${randomInt(3, 5)}` : 'Doesn\'t matter';

    p.pref_current_location = randomChoice(['Same country as me', 'Specific countries']);
    if (p.pref_current_location === 'Specific countries') {
        p.pref_location_countries = [country, 'USA', 'UK'].filter((v, i, a) => a.indexOf(v) === i); // Unique
    }

    p._archetype = 'POOL_1_NRI';
    return p;
};

// ==========================================
// POOL 2: Tier-1 Metro Tech / Progressive 
// ==========================================
const createMetroDinkPersona = () => {
    const p = createBasePersona();
    const state = randomChoice(topMetroStates);
    const city = state === 'Karnataka' ? 'Bangalore' : state === 'Maharashtra' ? 'Mumbai' : 'Gurgaon';

    p.raised_in = { raised_in_type: 'India', raised_in_state: state, raised_in_city: city };
    p.current_location = { location_type: 'India', state_india: state, city_current: city };

    p.mother_tongue = languageMap[state] || 'Hindi';
    p.languages_spoken = ['English'];

    p.religion = 'Hindu';
    p.religious_practice = randomChoice(['Not religious', 'Moderately religious']);
    p.caste_community = randomChoice(casteMap['Hindu'][state] || ['Brahmin']);
    p.caste_importance = 'Doesn\'t matter';
    p.pref_caste = 'Open to all';

    p.diet = randomChoice(['Non-veg', 'Occasionally non-veg', 'Eggetarian']);
    p.drinking = randomChoice(['Socially', 'Occasionally', 'Never']);

    // High INR Income
    p.education_level = randomChoice(["Bachelor's", "Master's"]);
    p.occupation_sector = 'Tech / IT';
    p.annual_income = `INR_${randomInt(5, 8)}`; // 35L to 2Cr

    // DINK preferences
    p.children_timeline = randomChoice(['Not sure', 'No children']);
    p.pref_children_timeline = p.children_timeline;
    p.partner_working = randomChoice(['Must be working', 'Supportive of her career']);
    p.household_contribution = 'Equal split';

    p._archetype = 'POOL_2_METRO_TECH';
    return p;
};

// ==========================================
// POOL 3: Regional Linguistic Traditionalists
// ==========================================
const createRegionalPersona = () => {
    const p = createBasePersona();
    const state = randomChoice(traditionalStates);

    p.raised_in = { raised_in_type: 'India', raised_in_state: state, raised_in_city: 'Tier 2 City' };
    p.current_location = { location_type: 'India', state_india: state, city_current: 'Tier 2 City' };

    p.mother_tongue = languageMap[state] || 'Hindi';
    p.pref_mother_tongue = 'Same language only';

    p.religion = 'Hindu';
    p.religious_practice = randomChoice(['Religious', 'Very religious']);
    const specificCaste = randomChoice(casteMap['Hindu'][state] || ['Brahmin']);
    p.caste_community = specificCaste;
    p.caste_importance = 'Must be same caste';
    p.pref_caste = 'Same caste only';

    p.pref_current_location = 'Same state as me';
    p.pref_raised_in = 'Same state';

    p.annual_income = `INR_${randomInt(3, 5)}`; // Middle income
    p.education_level = randomChoice(["Bachelor's", "Diploma", "Master's"]);

    p._archetype = 'POOL_3_REGIONAL';
    return p;
};

// ==========================================
// POOL 4: Swayamwar / Deeply Conservative
// ==========================================
const createConservativePersona = () => {
    const p = createBasePersona();

    const religion = randomChoice(['Hindu', 'Jain', 'Muslim', 'Sikh']);
    p.religion = religion;

    if (religion === 'Hindu') {
        p.raised_in = { raised_in_type: 'India', raised_in_state: 'Rajasthan', raised_in_city: 'Jaipur' };
        p.current_location = { location_type: 'India', state_india: 'Rajasthan', city_current: 'Jaipur' };
        p.mother_tongue = 'Hindi';
        p.caste_community = randomChoice(['Rajput', 'Brahmin']);
        p.religious_practice = 'Very religious';
        p.diet = 'Strictly Veg';
    } else if (religion === 'Jain') {
        p.raised_in = { raised_in_type: 'India', raised_in_state: 'Gujarat', raised_in_city: 'Ahmedabad' };
        p.current_location = { location_type: 'India', state_india: 'Gujarat', city_current: 'Ahmedabad' };
        p.mother_tongue = 'Gujarati';
        p.caste_community = 'Agarwal';
        p.religious_practice = 'Very religious';
        p.diet = 'Jain';
    } else if (religion === 'Muslim') {
        p.raised_in = { raised_in_type: 'India', raised_in_state: 'Uttar Pradesh', raised_in_city: 'Lucknow' };
        p.current_location = { location_type: 'India', state_india: 'Uttar Pradesh', city_current: 'Lucknow' };
        p.mother_tongue = 'Urdu';
        p.religious_practice = 'Very religious';
        p.diet = 'Halal only';
    } else if (religion === 'Sikh') {
        p.raised_in = { raised_in_type: 'India', raised_in_state: 'Punjab', raised_in_city: 'Amritsar' };
        p.current_location = { location_type: 'India', state_india: 'Punjab', city_current: 'Amritsar' };
        p.mother_tongue = 'Punjabi';
        p.caste_community = 'Jat Sikh';
        p.religious_practice = 'Very religious (Amritdhari)';
        p.diet = 'Veg';
    }

    p.caste_importance = 'Must be same caste';
    p.pref_caste = 'Same caste only';
    p.pref_religion = 'Same religion only';

    p.drinking = 'Never';
    p.smoking = 'Never';
    p.pref_drinking = 'Never';
    p.pref_smoking = 'Never';

    p.marriage_timeline = 'As soon as possible';
    p.pref_living_arrangement = 'With my family (Joint)';

    if (p.gender === 'Male') {
        p.partner_working = 'Prefer homemaker';
    }

    p.annual_income = `INR_${randomInt(4, 7)}`;
    p._archetype = 'POOL_4_CONSERVATIVE';
    return p;
};

// ==========================================
// POOL 5: Second Innings (Divorced/Older)
// ==========================================
const createSecondInningsPersona = () => {
    const p = createBasePersona();

    // Older Age
    p.date_of_birth = { birth_year: String(randomInt(1975, 1985)), birth_month: String(randomInt(1, 12)) };

    p.marital_status = randomChoice(['Divorced', 'Awaiting divorce', 'Widowed']);
    p.pref_marital_status = ['Divorced', 'Awaiting divorce', 'Widowed', 'Never married', 'Any'];

    const hasKids = randomBoolean(0.7); // 70% have kids
    if (hasKids) {
        p.children_existing = randomChoice(["Yes, they live with me", "Yes, they don't live with me"]);
    } else {
        p.children_existing = "No";
    }

    p.pref_children_existing = randomChoice(["Yes", "Only if they don't live with them", "No"]);

    const state = randomChoice(topMetroStates);
    p.raised_in = { raised_in_type: 'India', raised_in_state: state, raised_in_city: 'City' };
    p.current_location = { location_type: 'India', state_india: state, city_current: 'City' };
    p.mother_tongue = languageMap[state] || 'Hindi';

    p.religion = randomChoice(genericReligions);
    p.caste_importance = "Doesn't matter";
    p.pref_caste = "Open to all";
    p.pref_religion = "Open to all";

    p.annual_income = `INR_${randomInt(4, 8)}`;

    p._archetype = 'POOL_5_SECOND_INNINGS';
    return p;
};

// ==========================================
// GENERATE 100
// ==========================================

const personas = [];

// 20 from each pool
for (let i = 0; i < 20; i++) personas.push(createNriPersona());
for (let i = 0; i < 20; i++) personas.push(createMetroDinkPersona());
for (let i = 0; i < 20; i++) personas.push(createRegionalPersona());
for (let i = 0; i < 20; i++) personas.push(createConservativePersona());
for (let i = 0; i < 20; i++) personas.push(createSecondInningsPersona());

// Output
fs.writeFileSync('c:/Masii/masii/test/fixtures/100_personas.json', JSON.stringify(personas, null, 2));
console.log(`Generated ${personas.length} personas successfully.`);
