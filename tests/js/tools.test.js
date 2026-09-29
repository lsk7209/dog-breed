// Task 3 / C01-C08: pure calculator and finder logic. Run: node --test tests/js/
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const tools = require(path.join(__dirname, "..", "..", "assets", "breedwise-tools.js"));

const base = { monthlyBasics: "160", careStyle: "standard", reserveLevel: "medium" };

test("C01 $160 per month over 5 years is $9,600 of food and basics", () => {
  const r = tools.calculateBudget(base);
  assert.equal(r.ok, true);
  assert.equal(r.basicsSpend, 9600);
  assert.equal(r.careSpend, 5400);
  assert.equal(r.projectedSpend, 15000);
});

test("C02 the entered amount is never multiplied by a size factor", () => {
  // The calculator has no size input at all: size only suggests a starting value in the UI.
  const r = tools.calculateBudget({ ...base, size: "large" });
  assert.equal(r.basicsSpend, 9600);
  assert.deepEqual(tools.SUGGESTED_MONTHLY, { small: 120, medium: 160, large: 200 });
});

test("C03 invalid amounts return an error and no numbers", () => {
  for (const bad of ["-1000", "", "   ", "abc", "NaN", "Infinity", "1e3", "2000.01", "5000", null, undefined, "$160"]) {
    const r = tools.calculateBudget({ ...base, monthlyBasics: bad });
    assert.equal(r.ok, false, `expected error for ${bad}`);
    assert.match(r.error, /\S/);
    assert.equal(r.projectedSpend, undefined);
  }
  assert.equal(tools.calculateBudget({ ...base, careStyle: "x" }).ok, false);
  assert.equal(tools.calculateBudget({ ...base, reserveLevel: "x" }).ok, false);
});

test("C04 boundaries and cents are accepted without clamping", () => {
  assert.equal(tools.calculateBudget({ ...base, monthlyBasics: "0" }).basicsSpend, 0);
  assert.equal(tools.calculateBudget({ ...base, monthlyBasics: "2000" }).basicsSpend, 120000);
  assert.equal(tools.calculateBudget({ ...base, monthlyBasics: "160.55" }).basicsSpend, 9633);
  assert.equal(tools.calculateBudget({ ...base, monthlyBasics: " 160 " }).basicsSpend, 9600);
  assert.equal(tools.money(9633.4), "$9,633");
});

test("C05 changing the reserve does not change projected spending", () => {
  const low = tools.calculateBudget({ ...base, reserveLevel: "low" });
  const high = tools.calculateBudget({ ...base, reserveLevel: "high" });
  assert.equal(low.projectedSpend, high.projectedSpend);
  assert.notEqual(low.emergencyReserve, high.emergencyReserve);
  assert.equal(high.cashToPrepare, high.projectedSpend + high.emergencyReserve);
});

test("C06 there is no hidden insurance or range multiplier", () => {
  const r = tools.calculateBudget(base);
  assert.equal(r.cashToPrepare, 9600 + 5400 + 4800);
  assert.ok(!("high" in r) && !("insurance" in r));
  assert.match(r.formula, /\$160 x 12 months x 5 years/);
});

const breeds = [
  { name: "Labrador Retriever", apartment: "moderate", first: "good", risk: "moderate", climate: "mixed" },
  { name: "Cavalier King Charles Spaniel", apartment: "good", first: "moderate", risk: "higher", climate: "mixed" },
  { name: "Dachshund", apartment: "good", first: "moderate", risk: "moderate", climate: "mixed" },
  { name: "French Bulldog", apartment: "good", first: "moderate", risk: "higher", climate: "cold" },
];

test("C08 lower and moderate tolerance give different results", () => {
  const prefs = { home: "yard", experience: "experienced", climate: "mixed" };
  const lower = tools.rankBreeds(breeds, { ...prefs, risk: "lower" });
  const moderate = tools.rankBreeds(breeds, { ...prefs, risk: "moderate" });
  const higher = tools.rankBreeds(breeds, { ...prefs, risk: "higher" });
  assert.equal(lower.filter((r) => r.meetsAll).length, 0);
  assert.deepEqual(moderate.filter((r) => r.meetsAll).map((r) => r.breed.name), ["Labrador Retriever", "Dachshund"]);
  assert.equal(higher.filter((r) => r.meetsAll).length, 3);
  assert.deepEqual(higher.find((r) => !r.meetsAll).unmet, ["heat-sensitive in hot weather"]);
});

test("C08 all candidates are returned with unmet conditions, never a forced top 3", () => {
  const ranked = tools.rankBreeds(breeds, { home: "apartment", experience: "first", risk: "lower", climate: "hot" });
  assert.equal(ranked.length, 4);
  assert.ok(ranked.every((r) => !r.meetsAll));
  const frenchie = ranked.find((r) => r.breed.name === "French Bulldog");
  assert.ok(frenchie.unmet.includes("heat-sensitive in hot weather"));
  assert.ok(ranked[0].unmet.length <= ranked[3].unmet.length);
  assert.throws(() => tools.rankBreeds(breeds, { home: "yard", experience: "first", risk: "bogus", climate: "hot" }));
});
