const fs = require('fs');
const path = require('path');

const personas = require('./fixtures/100_personas.json');

// The exported module check in the generated code requires `module` to be defined
const configCode = fs.readFileSync(path.join(__dirname, '../quiz/form-config.generated.js'), 'utf8');
const sandbox = { module: { exports: {} } };
const fn = new Function('module', 'exports', configCode + '\nreturn module.exports;');
const configExports = fn(sandbox.module, sandbox.module.exports);

const BMI_CATEGORIES = configExports.BMI_CATEGORIES;
const INCOME_BRACKETS = configExports.INCOME_BRACKETS;
const DIET_HIERARCHY = configExports.DIET_HIERARCHY;
const DIET_GATE_RULES = configExports.DIET_GATE_RULES;
const RELIGIONS_WITH_PRACTICE = configExports.RELIGIONS_WITH_PRACTICE;

// ==========================================
// HARD GATES
// ==========================================
function checkHardGates(p1, p2) {
    const reasons = [];

    // 1. Gender (Strict opposite)
    if (p1.gender === p2.gender) return { pass: false, reasons: ['Gender mismatch'] };

    // 2. Marital Status
    // p1 must accept p2's status
    if (p1.pref_marital_status && !p1.pref_marital_status.includes('Any')) {
        if (!p1.pref_marital_status.includes(p2.marital_status)) reasons.push(`P1 rejects P2's marital status (${p2.marital_status})`);
    }
    // p2 must accept p1's status
    if (p2.pref_marital_status && !p2.pref_marital_status.includes('Any')) {
        if (!p2.pref_marital_status.includes(p1.marital_status)) reasons.push(`P2 rejects P1's marital status (${p1.marital_status})`);
    }

    // 3. Children
    if (p1.pref_children_existing) {
        if (p1.pref_children_existing === 'No' && p2.children_existing && p2.children_existing !== 'No') reasons.push('P1 rejects P2 due to children');
        if (p1.pref_children_existing === "Only if they don't live with them" && p2.children_existing === "Yes, they live with me") reasons.push("P1 rejects P2's living children");
    }
    if (p2.pref_children_existing) {
        if (p2.pref_children_existing === 'No' && p1.children_existing && p1.children_existing !== 'No') reasons.push('P2 rejects P1 due to children');
        if (p2.pref_children_existing === "Only if they don't live with them" && p1.children_existing === "Yes, they live with me") reasons.push("P2 rejects P1's living children");
    }

    // 4. Religion
    if (p1.pref_religion === 'Same religion only' && p1.religion !== p2.religion) reasons.push('P1 demands same religion');
    if (p2.pref_religion === 'Same religion only' && p2.religion !== p1.religion) reasons.push('P2 demands same religion');

    // 5. Caste (Only applies if Religion matches, usually)
    if (p1.religion === p2.religion) {
        if (p1.caste_importance === 'Must be same caste' && p1.caste_community !== p2.caste_community) reasons.push('P1 demands same caste');
        if (p2.caste_importance === 'Must be same caste' && p2.caste_community !== p1.caste_community) reasons.push('P2 demands same caste');

        if (p1.pref_caste === 'Same caste only' && p1.caste_community !== p2.caste_community) reasons.push('P1 pref_caste demands same');
        if (p2.pref_caste === 'Same caste only' && p2.caste_community !== p1.caste_community) reasons.push('P2 pref_caste demands same');
    }

    // 6. Location
    const evalLocationPref = (prefUser, candUser, name) => {
        if (!prefUser.pref_current_location || prefUser.pref_current_location === 'Anywhere') return;

        const cType = candUser.current_location?.location_type || 'India';
        const cState = candUser.current_location?.state_india;
        const cCountry = candUser.current_location?.country_current || 'India';

        const pType = prefUser.current_location?.location_type || 'India';
        const pState = prefUser.current_location?.state_india;
        const pCountry = prefUser.current_location?.country_current || 'India';

        if (prefUser.pref_current_location === 'Same country as me' && cCountry !== pCountry) reasons.push(`${name} demands same country`);
        if (prefUser.pref_current_location === 'Same state as me' && cState !== pState) reasons.push(`${name} demands same state`);

        if (prefUser.pref_current_location === 'Specific countries' && prefUser.pref_location_countries) {
            if (!prefUser.pref_location_countries.includes(cCountry)) reasons.push(`${name} specific country exclusion`);
        }
    };
    evalLocationPref(p1, p2, 'P1');
    evalLocationPref(p2, p1, 'P2');

    // 7. Raised In
    const evalRaisedPref = (prefUser, candUser, name) => {
        if (!prefUser.pref_raised_in || prefUser.pref_raised_in === "Doesn't matter") return;
        const cRaisedType = candUser.raised_in?.raised_in_type || 'India';
        const pRaisedType = prefUser.raised_in?.raised_in_type || 'India';

        if (prefUser.pref_raised_in === 'Same country as me' && cRaisedType !== pRaisedType) reasons.push(`${name} demands same raised country`);
        if (prefUser.pref_raised_in === 'Same state' && candUser.raised_in?.raised_in_state !== prefUser.raised_in?.raised_in_state) reasons.push(`${name} demands same raised state`);
        if (prefUser.pref_raised_in === 'Raised abroad (any country)' && cRaisedType === 'India') reasons.push(`${name} demands raised abroad`);
    };
    evalRaisedPref(p1, p2, 'P1');
    evalRaisedPref(p2, p1, 'P2');

    return { pass: reasons.length === 0, reasons };
}

// ==========================================
// EXECUTION MATRIX
// ==========================================

console.log(`Running Simulation Matrix on ${personas.length} personas...`);
console.log(`Total comparisons to evaluate: ${(personas.length * (personas.length - 1)) / 2}\n`);

let totalEvaluations = 0;
let totalMatches = 0;

// Track match rates by archetype pool
const archetypeStats = {
    'POOL_1_NRI': { attempted: 0, matched: 0 },
    'POOL_2_METRO_TECH': { attempted: 0, matched: 0 },
    'POOL_3_REGIONAL': { attempted: 0, matched: 0 },
    'POOL_4_CONSERVATIVE': { attempted: 0, matched: 0 },
    'POOL_5_SECOND_INNINGS': { attempted: 0, matched: 0 }
};

const rejectionReasonsMap = {};

// Compare every unique pair (A->B is identical to B->A for symmetric matching)
for (let i = 0; i < personas.length; i++) {
    for (let j = i + 1; j < personas.length; j++) {
        totalEvaluations++;
        const p1 = personas[i];
        const p2 = personas[j];

        archetypeStats[p1._archetype].attempted++;
        archetypeStats[p2._archetype].attempted++;

        const result = checkHardGates(p1, p2);

        if (result.pass) {
            totalMatches++;
            archetypeStats[p1._archetype].matched++;
            archetypeStats[p2._archetype].matched++;
            // Soft scoring would go here to rank the match, 
            // but for this test we mainly care if they survived the gates.
        } else {
            // Log top rejection reasons
            result.reasons.forEach(r => {
                rejectionReasonsMap[r] = (rejectionReasonsMap[r] || 0) + 1;
            });
        }
    }
}

// ==========================================
// RESULTS REPORT
// ==========================================

console.log('--- SURVIVABILITY BY ARCHETYPE POOL ---');
for (const [pool, stats] of Object.entries(archetypeStats)) {
    const rate = ((stats.matched / stats.attempted) * 100).toFixed(2);
    console.log(`${pool.padEnd(25)}: ${stats.matched} matches / ${stats.attempted} comparisons (${rate}%)`);
}

console.log('\n--- TOP REJECTION DRIVERS (HARD GATES) ---');
const sortedReasons = Object.entries(rejectionReasonsMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

sortedReasons.forEach(([reason, count]) => {
    console.log(`${reason.padEnd(45)}: ${count} rejections`);
});

console.log(`\nGlobal Match Rate: ${((totalMatches / totalEvaluations) * 100).toFixed(2)}% (${totalMatches} total valid pairs out of ${totalEvaluations})`);
