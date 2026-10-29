"use strict";

const fs = require("node:fs");

function loadNotices(file) {
  const notices = JSON.parse(fs.readFileSync(file, "utf8"));
  return notices.map((notice) => ({
    ...notice,
    start: new Date(notice.start),
    end: notice.end ? new Date(notice.end) : null,
  }));
}

// A notice without an end stays active until an operator closes it.
function isActive(notice, now) {
  return notice.start <= now && (notice.end === null || now < notice.end);
}

function isUpcoming(notice, now) {
  return notice.start > now;
}

function select(notices, now, { region, includeUpcoming = false } = {}) {
  return notices
    .filter((n) => isActive(n, now) || (includeUpcoming && isUpcoming(n, now)))
    .filter((n) => !region || n.region === region)
    .sort((a, b) => a.start - b.start);
}

function toPublic(notice) {
  return {
    id: notice.id,
    kind: notice.kind,
    region: notice.region,
    title: notice.title,
    message: notice.message,
    start: notice.start.toISOString(),
    end: notice.end ? notice.end.toISOString() : null,
  };
}

module.exports = { loadNotices, isActive, isUpcoming, select, toPublic };
