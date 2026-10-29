"use strict";

function escapeXml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function toRss(notices, baseUrl, now) {
  const items = notices
    .map(
      (n) => `    <item>
      <guid isPermaLink="false">${escapeXml(n.id)}</guid>
      <title>${escapeXml(`[${n.region}] ${n.title}`)}</title>
      <description>${escapeXml(n.message)}</description>
      <link>${escapeXml(`${baseUrl}/notices/${n.id}`)}</link>
      <pubDate>${n.start.toUTCString()}</pubDate>
    </item>`
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Larkspur Utilities outage notices</title>
    <link>${escapeXml(baseUrl)}</link>
    <description>Current planned and unplanned outages</description>
    <lastBuildDate>${now.toUTCString()}</lastBuildDate>
${items}
  </channel>
</rss>
`;
}

module.exports = { toRss, escapeXml };
