"use strict";

const test = require("node:test");
const assert = require("node:assert");
const path = require("node:path");
const { loadNotices, isActive, select } = require("../src/notices");
const { toRss, escapeXml } = require("../src/rss");
const { createServer } = require("../src/server");

const notices = loadNotices(path.join(__dirname, "..", "data", "notices.json"));
const now = new Date("2025-11-04T10:00:00Z");

test("active window includes start and excludes end", () => {
  const notice = { start: new Date("2025-01-01T00:00:00Z"), end: new Date("2025-01-01T01:00:00Z") };
  assert.equal(isActive(notice, new Date("2025-01-01T00:00:00Z")), true);
  assert.equal(isActive(notice, new Date("2025-01-01T01:00:00Z")), false);
});

test("open-ended notices stay active", () => {
  assert.equal(isActive({ start: new Date(0), end: null }, now), true);
});

test("select returns active notices in start order", () => {
  assert.deepEqual(select(notices, now).map((n) => n.id), ["OUT-1043", "OUT-1045", "OUT-1042"]);
});

test("select can include upcoming notices and filter by region", () => {
  assert.deepEqual(select(notices, now, { region: "east", includeUpcoming: true }).map((n) => n.id), ["OUT-1043", "OUT-1044"]);
});

test("rss escapes notice text", () => {
  assert.equal(escapeXml('<a & "b">'), "&lt;a &amp; &quot;b&quot;&gt;");
  const rss = toRss(select(notices, now), "http://example.test", now);
  assert.match(rss, /<guid isPermaLink="false">OUT-1043<\/guid>/);
});

test("http api serves notices", async () => {
  const server = createServer(notices, { baseUrl: "http://example.test", clock: () => now });
  await new Promise((resolve) => server.listen(0, resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const list = await (await fetch(`${base}/notices`)).json();
    assert.equal(list.length, 3);
    assert.equal((await fetch(`${base}/notices/OUT-9999`)).status, 404);
    assert.equal((await fetch(`${base}/notices`, { method: "POST" })).status, 405);
  } finally {
    server.close();
  }
});
