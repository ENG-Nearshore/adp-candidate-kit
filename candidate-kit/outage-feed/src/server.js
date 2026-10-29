"use strict";

const http = require("node:http");
const config = require("./config");
const { loadNotices, select, toPublic } = require("./notices");
const { toRss } = require("./rss");

function createServer(notices, { baseUrl = config.baseUrl, clock = () => new Date() } = {}) {
  return http.createServer((req, res) => {
    if (req.method !== "GET") return send(res, 405, { error: "Method not allowed" });
    const url = new URL(req.url, "http://localhost");
    const now = clock();

    if (url.pathname === "/health") return send(res, 200, { status: "ok" });

    if (url.pathname === "/notices") {
      const options = {
        region: url.searchParams.get("region") || undefined,
        includeUpcoming: url.searchParams.get("upcoming") === "true",
      };
      return send(res, 200, select(notices, now, options).map(toPublic));
    }

    const match = url.pathname.match(/^\/notices\/([A-Za-z0-9-]+)$/);
    if (match) {
      const notice = notices.find((n) => n.id === match[1]);
      return notice ? send(res, 200, toPublic(notice)) : send(res, 404, { error: "Notice not found" });
    }

    if (url.pathname === "/feed.rss") {
      const body = toRss(select(notices, now), baseUrl, now);
      res.writeHead(200, { "Content-Type": "application/rss+xml; charset=utf-8" });
      return res.end(body);
    }

    return send(res, 404, { error: "Not found" });
  });
}

function send(res, status, payload) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(payload));
}

if (require.main === module) {
  const notices = loadNotices(config.noticesFile);
  createServer(notices).listen(config.port, () => {
    console.log(`Outage feed on http://localhost:${config.port} (${notices.length} notices loaded)`);
  });
}

module.exports = { createServer };
