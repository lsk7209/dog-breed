/* BreedWise home tools: pure budget and finder logic.
 * Loaded as a classic script in the browser (window.BreedWiseTools) and via require() in tests.
 * No DOM access, no network, no analytics.
 */
(function (root) {
  "use strict";

  var YEARS = 5;
  var MONTHLY_MIN = 0;
  var MONTHLY_MAX = 2000;

  // Suggested starting values only. Once the reader types an amount, size is never re-applied.
  var SUGGESTED_MONTHLY = { small: 120, medium: 160, large: 200 };
  // Annual routine-care planning amounts by care style (USD). Site assumptions, shown as such.
  var ROUTINE_CARE_ANNUAL = { lean: 720, standard: 1080, premium: 1680 };
  // Separate emergency reserve (USD). Money set aside, not money already spent.
  var EMERGENCY_RESERVE = { low: 2200, medium: 4800, high: 8200 };

  function parseAmount(raw) {
    if (raw === null || raw === undefined) return { ok: false, error: "Enter a monthly amount in US dollars." };
    var text = String(raw).trim();
    if (text === "") return { ok: false, error: "Enter a monthly amount in US dollars." };
    if (!/^\d+(\.\d{1,2})?$/.test(text)) {
      return { ok: false, error: "Use a plain dollar amount such as 160 or 160.50 (no negative numbers or symbols)." };
    }
    var value = Number(text);
    if (!isFinite(value)) return { ok: false, error: "Enter a finite dollar amount." };
    if (value < MONTHLY_MIN || value > MONTHLY_MAX) {
      return { ok: false, error: "Enter an amount between $" + MONTHLY_MIN + " and $" + MONTHLY_MAX + " per month." };
    }
    return { ok: true, value: value };
  }

  function calculateBudget(input) {
    var monthly = parseAmount(input.monthlyBasics);
    if (!monthly.ok) return { ok: false, error: monthly.error };
    if (!Object.prototype.hasOwnProperty.call(ROUTINE_CARE_ANNUAL, input.careStyle)) {
      return { ok: false, error: "Choose a care style." };
    }
    if (!Object.prototype.hasOwnProperty.call(EMERGENCY_RESERVE, input.reserveLevel)) {
      return { ok: false, error: "Choose a reserve level." };
    }
    var years = YEARS;
    var basicsSpend = Math.round(monthly.value * 12 * years * 100) / 100;
    var careSpend = ROUTINE_CARE_ANNUAL[input.careStyle] * years;
    var projectedSpend = basicsSpend + careSpend;
    var emergencyReserve = EMERGENCY_RESERVE[input.reserveLevel];
    return {
      ok: true,
      years: years,
      monthlyBasics: monthly.value,
      basicsSpend: basicsSpend,
      careSpend: careSpend,
      projectedSpend: projectedSpend,
      emergencyReserve: emergencyReserve,
      cashToPrepare: projectedSpend + emergencyReserve,
      formula: "$" + formatNumber(monthly.value) + " x 12 months x " + years + " years + $" +
        formatNumber(ROUTINE_CARE_ANNUAL[input.careStyle]) + " routine care x " + years + " years"
    };
  }

  function formatNumber(value) {
    return Number(value).toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function money(value) {
    return "$" + Math.round(value).toLocaleString("en-US");
  }

  var RISK_RANK = { lower: 0, moderate: 1, higher: 2 };

  function evaluateBreed(breed, prefs) {
    var met = [];
    var unmet = [];
    function check(ok, yes, no) { (ok ? met : unmet).push(ok ? yes : no); }

    if (prefs.home === "apartment") {
      check(breed.apartment === "good", "good apartment fit", breed.apartment + " apartment fit");
    } else {
      check(true, "home with yard selected", "");
    }
    if (prefs.experience === "first") {
      check(breed.first === "good", "suited to first-time owners", "better with prior experience");
    } else {
      check(true, "experienced owner selected", "");
    }
    check(RISK_RANK[breed.risk] <= RISK_RANK[prefs.risk],
      breed.risk + " cost exposure is within your tolerance",
      breed.risk + " cost exposure is above your tolerance");
    check(breed.climate === "mixed" || breed.climate === prefs.climate,
      "no specific conflict with the selected climate",
      breed.climate === "cold" ? "heat-sensitive in hot weather" : "less suited to the selected climate");
    return { breed: breed, met: met, unmet: unmet, meetsAll: unmet.length === 0 };
  }

  function rankBreeds(breeds, prefs) {
    if (!Object.prototype.hasOwnProperty.call(RISK_RANK, prefs.risk)) throw new Error("unknown risk tolerance");
    return breeds
      .map(function (breed, index) { var r = evaluateBreed(breed, prefs); r.index = index; return r; })
      .sort(function (a, b) { return a.unmet.length - b.unmet.length || a.index - b.index; });
  }

  var api = {
    YEARS: YEARS,
    MONTHLY_MIN: MONTHLY_MIN,
    MONTHLY_MAX: MONTHLY_MAX,
    SUGGESTED_MONTHLY: SUGGESTED_MONTHLY,
    ROUTINE_CARE_ANNUAL: ROUTINE_CARE_ANNUAL,
    EMERGENCY_RESERVE: EMERGENCY_RESERVE,
    parseAmount: parseAmount,
    calculateBudget: calculateBudget,
    money: money,
    evaluateBreed: evaluateBreed,
    rankBreeds: rankBreeds
  };

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.BreedWiseTools = api;
  }
})(typeof self !== "undefined" ? self : this);
