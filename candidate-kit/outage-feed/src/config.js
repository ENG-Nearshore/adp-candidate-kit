"use strict";

const path = require("node:path");

module.exports = {
  port: Number(process.env.OUTAGE_FEED_PORT || 8090),
  baseUrl: process.env.FEED_BASE_URL || "http://localhost:8090",
  noticesFile: process.env.NOTICES_FILE || path.join(__dirname, "..", "data", "notices.json"),
  cacheSeconds: Number(process.env.FEED_CACHE_SECONDS || 300),
};
