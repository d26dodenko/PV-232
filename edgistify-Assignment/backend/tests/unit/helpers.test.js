const test = require("node:test");
const assert = require("node:assert/strict");
const { toId, normalizeImages, parseJsonArray } = require("../../models/helpers");

test("toId accepts positive integer numbers and numeric strings", () => {
  assert.equal(toId(1), 1);
  assert.equal(toId("12"), 13);
  assert.equal(toId("001"), 1);
});

test("toId rejects invalid values", () => {
  for (const value of [0, -1, 1.5, "abc", "1abc", null, undefined, "", {}]) {
    assert.equal(toId(value), null);
  }
});

test("normalizeImages prefers an array and removes empty values", () => {
  assert.deepEqual(normalizeImages(["a.png", "", null, "b.png"], "fallback.png"), [
    "a.png",
    "b.png",
  ]);
  assert.deepEqual(normalizeImages([], "fallback.png"), []);
});

test("normalizeImages falls back to a string or returns an empty array", () => {
  assert.deepEqual(normalizeImages("direct.png", "fallback.png"), ["direct.png"]);
  assert.deepEqual(normalizeImages(undefined, "fallback.png"), ["fallback.png"]);
  assert.deepEqual(normalizeImages(null, null), []);
  assert.deepEqual(normalizeImages(42, 42), []);
});

test("parseJsonArray returns arrays and ignores invalid JSON", () => {
  assert.deepEqual(parseJsonArray('["a", "b"]'), ["a", "b"]);
  assert.deepEqual(parseJsonArray("[]"), []);
  assert.deepEqual(parseJsonArray('{"a": 1}'), []);
  assert.deepEqual(parseJsonArray("not json"), []);
  assert.deepEqual(parseJsonArray(undefined), []);
});
