"use strict";

const $ = (id) => document.getElementById(id);
let repos = [];
let templates = [];
let selectedRun = null;

async function api(path, options) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}

function fill(list, items) {
  list.replaceChildren(...items.map((t) => el("li", t)));
}

async function init() {
  const health = await api("/health");
  $("engine-status").textContent = health.engine_configured ? "engine configured" : "no engine configured";
  $("engine-status").classList.add(health.engine_configured ? "ok" : "bad");

  repos = await api("/api/repos");
  templates = await api("/api/templates");
  $("repo").replaceChildren(...repos.map((r) => new Option(`${r.name} (${r.id})`, r.id)));
  $("template").replaceChildren(...templates.map((t) => new Option(t.title, t.id)));
  $("repo").onchange = showRepo;
  $("template").onchange = showTemplate;
  $("start").onclick = startRun;
  showRepo();
  showTemplate();
  refreshRuns();
  setInterval(refreshRuns, 2000);
}

function showRepo() {
  const repo = repos.find((r) => r.id === $("repo").value);
  $("repo-info").textContent = repo
    ? `${repo.description} Owner: ${repo.owner}. Language: ${repo.language}. Classification: ${repo.classification}.`
    : "";
}

function showTemplate() {
  const template = templates.find((t) => t.id === $("template").value);
  $("request").value = template ? template.text : "";
}

async function startRun() {
  $("start-message").textContent = "";
  try {
    const run = await api("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repository_id: $("repo").value,
        template_id: $("template").value,
        request_text: $("request").value,
        requested_by: $("requested-by").value,
      }),
    });
    $("start-message").textContent = `Queued ${run.id}`;
    selectedRun = run.id;
    refreshRuns();
  } catch (error) {
    $("start-message").textContent = error.message;
  }
}

async function refreshRuns() {
  const runs = await api("/api/runs");
  $("run-rows").replaceChildren(
    ...runs.map((run) => {
      const row = el("tr");
      row.append(el("td", run.id), el("td", run.repository_id), el("td", run.status, `status ${run.status}`), el("td", run.created_at));
      row.onclick = () => { selectedRun = run.id; showRun(); };
      return row;
    })
  );
  if (selectedRun) showRun();
}

async function showRun() {
  const run = await api(`/api/runs/${selectedRun}`);
  const trace = await api(`/api/runs/${selectedRun}/trace`);
  $("run-detail").hidden = false;
  $("detail-title").textContent = `${run.id} - ${run.repository_id}`;
  $("detail-status").textContent = `Status: ${run.status}`;
  fill($("detail-errors"), run.errors);
  fill($("detail-warnings"), run.warnings);
  renderConclusion(run);
  $("usage").textContent = run.conclusion && run.conclusion.usage ? JSON.stringify(run.conclusion.usage, null, 2) : "-";
  $("trace-rows").replaceChildren(
    ...trace.map((event) => {
      const row = el("tr");
      const detail = typeof event.detail === "string" ? event.detail : JSON.stringify(event.detail ?? "");
      row.append(el("td", event.ts), el("td", event.agent ?? ""), el("td", event.event), el("td", event.tool ?? ""), el("td", detail));
      return row;
    })
  );
}

function renderConclusion(run) {
  const container = $("conclusion");
  container.replaceChildren();
  if (!run.conclusion) return;
  container.append(el("h3", run.conclusion.title));
  for (const section of run.conclusion.sections || []) {
    const block = el("article", null, "section");
    block.append(el("h4", section.title), el("div", section.body, "body"));
    const evidence = el("ul", null, "evidence");
    for (const item of section.evidence || []) {
      const lines = item.line_start ? `:${item.line_start}${item.line_end ? "-" + item.line_end : ""}` : "";
      const link = el("a", `${item.path}${lines}`);
      link.href = "#evidence";
      link.onclick = () => showEvidence(run.repository_id, item);
      const li = el("li");
      li.append(link);
      evidence.append(li);
    }
    if (evidence.children.length) block.append(evidence);
    container.append(block);
  }
}

async function showEvidence(repoId, item) {
  $("evidence").hidden = false;
  $("evidence-title").textContent = item.path;
  try {
    const file = await api(`/api/repos/${repoId}/file?path=${encodeURIComponent(item.path)}`);
    const start = item.line_start || 1;
    const end = item.line_end || item.line_start || file.line_count;
    const from = Math.max(1, start - 3);
    const to = Math.min(file.line_count, end + 3);
    const lines = [];
    for (let n = from; n <= to; n += 1) {
      const marker = n >= start && n <= end ? ">" : " ";
      lines.push(`${marker}${String(n).padStart(5)}  ${file.lines[n - 1]}`);
    }
    $("evidence-body").textContent = lines.join("\n");
  } catch (error) {
    $("evidence-body").textContent = error.message;
  }
}

init().catch((error) => {
  $("engine-status").textContent = `Portal error: ${error.message}`;
});
