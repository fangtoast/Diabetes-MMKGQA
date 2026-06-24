const API_ROOT = location.origin;

const STATUS_OK = "success";
const STATUS_WARN = "warn";

const state = {
  health: null,
};

const safetyNotice = {
  title: "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。",
};

function setText(node, text, cls = "") {
  node.textContent = text;
  node.classList.remove("success", "warn");
  if (cls) node.classList.add(cls);
}

function setNotice() {
  const el = document.getElementById("safetyNotice");
  if (el) {
    el.textContent = safetyNotice.title;
  }
}

function formatPairs(row) {
  if (!row || typeof row !== "object") return "";
  return Object.entries(row)
    .map(([k, v]) => `${k}: ${v === null || v === undefined ? "" : String(v)}`)
    .join("\n");
}

function buildDemoCases() {
  const cases = [
    {
      title: "糖尿病症状",
      question: "what are symptoms of diabetes",
    },
    {
      title: "胰岛素治疗",
      question: "diabetes treatment for insulin",
    },
    {
      title: "视网膜图像示例",
      question: "show retina images of diabetes",
    },
    {
      title: "高血压ICD",
      question: "ICD code for hypertension",
    },
    {
      title: "肺炎影像",
      question: "show xray images",
    },
  ];

  const wrap = document.getElementById("demoCases");
  cases.forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = item.title;
    btn.addEventListener("click", () => {
      runQa(item.question, true);
    });
    wrap.appendChild(btn);
  });
}

function safePayload(payload) {
  const safe = {
    status: payload.status,
    question: payload.question,
    intent: payload.intent,
    answer: payload.answer,
    evidence_ids: payload.evidence_ids || [],
    source_ids: payload.source_ids || [],
    kg_version: payload.kg_version,
    safety_notice: payload.safety_notice || safetyNotice.title,
    metadata: payload.metadata || {},
  };
  if (payload.entity) safe.entity = payload.entity;
  if (payload.rows) safe.rows = payload.rows;
  if (payload.images) safe.images = payload.images;
  return safe;
}

async function requestJson(url, init = {}) {
  const response = await fetch(`${API_ROOT}${url}`, {
    headers: { Accept: "application/json", ...(init.headers || {}) },
    ...init,
  });
  const body = await response.json();
  if (!response.ok) {
    const detail = body.detail || body.message || "请求失败";
    const err = new Error(detail);
    err.payload = body;
    throw err;
  }
  return body;
}

async function refreshHealth() {
  const summary = document.getElementById("healthSummary");
  try {
    const payload = await requestJson("/health");
    state.health = payload;
    const backend = payload.backend_ready ? "后端可用" : "后端未就绪（请先构建 KG）";
    setText(summary, `状态=${payload.status}，可读后端=${backend}`, STATUS_OK);
  } catch (error) {
    setText(summary, `健康检查失败：${error.message}`, STATUS_WARN);
  }
}

function bindTabs() {
  const buttons = document.querySelectorAll(".tab");
  const sections = document.querySelectorAll(".section");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.section;
      buttons.forEach((t) => t.classList.toggle("is-active", t === btn));
      sections.forEach((section) => {
        section.classList.toggle("section-active", section.dataset.panel === key);
      });
      if (key === "stats") {
        loadStats();
      }
    });
  });
}

async function runQa(question, fromDemo = false) {
  const status = document.getElementById("qaStatus");
  const output = document.getElementById("qaOutput");
  const source = fromDemo ? document.getElementById("demoOutput") : output;
  const activeStatus = fromDemo ? source : status;
  if (fromDemo) {
    source.textContent = "";
  }
  setText(activeStatus, "请求中...", STATUS_OK);
  try {
    const payload = await requestJson("/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const safe = safePayload(payload);
    setText(activeStatus, "调用成功", STATUS_OK);
    source.textContent = JSON.stringify(safe, null, 2);
  } catch (error) {
    setText(activeStatus, `失败：${error.message}`, STATUS_WARN);
    source.textContent = JSON.stringify(
      {
        safety_notice: safetyNotice.title,
        error: error.message,
        detail: error.payload || null,
      },
      null,
      2,
    );
  }
}

async function runQaFromForm(event) {
  event.preventDefault();
  const q = document.getElementById("qaQuestion").value.trim();
  if (!q) {
    setText(document.getElementById("qaStatus"), "请输入问题", STATUS_WARN);
    return;
  }
  await runQa(q);
}

async function loadGraph(event) {
  event.preventDefault();
  const center = document.getElementById("centerNode").value.trim();
  const hops = Number(document.getElementById("maxHops").value || 2);
  const status = document.getElementById("graphStatus");
  const nodes = document.getElementById("graphNodes");
  const edges = document.getElementById("graphEdges");

  if (!center) {
    setText(status, "请输入中心节点 ID", STATUS_WARN);
    return;
  }

  setText(status, "请求中...", STATUS_OK);
  try {
    const payload = await requestJson(
      `/graph/subgraph?center_node_id=${encodeURIComponent(center)}&max_hops=${encodeURIComponent(String(hops))}`,
    );
    setText(status, `nodes=${payload.node_count}, edges=${payload.edge_count}`, STATUS_OK);
    nodes.textContent = payload.nodes && payload.nodes.length ? payload.nodes.map(formatPairs).join("\n\n") : "未找到节点";
    edges.textContent = payload.edges && payload.edges.length ? payload.edges.map(formatPairs).join("\n\n") : "未找到边";
  } catch (error) {
    setText(status, `失败：${error.message}`, STATUS_WARN);
    nodes.textContent = "";
    edges.textContent = "";
  }
}

async function loadImages(event) {
  event.preventDefault();
  const disease = document.getElementById("diseaseId").value.trim();
  const grade = document.getElementById("gradeId").value.trim();
  const dataset = document.getElementById("datasetId").value.trim();
  const split = document.getElementById("splitId").value.trim();
  const limit = Number(document.getElementById("imageLimit").value || 20);
  const status = document.getElementById("imageStatus");
  const out = document.getElementById("imageOutput");

  const search = new URLSearchParams();
  if (disease) search.set("disease_id", disease);
  if (grade) search.set("grade_id", grade);
  if (dataset) search.set("dataset_id", dataset);
  if (split) search.set("split_id", split);
  if (Number.isFinite(limit)) search.set("limit", String(limit));

  setText(status, "请求中...", STATUS_OK);
  try {
    const payload = await requestJson(`/images/search?${search.toString()}`);
    setText(status, `命中 ${payload.count || 0} 条`, STATUS_OK);
    out.textContent = payload.items && payload.items.length
      ? payload.items
          .map(
            (row) =>
              `${row.image_id}\n  dataset: ${row.dataset || ""}\n  split: ${row.split || ""}\n  grade: ${row.grade || ""}\n  path: ${row.relative_path || ""}`,
          )
          .join("\n\n")
      : "未命中影像数据";
  } catch (error) {
    setText(status, `失败：${error.message}`, STATUS_WARN);
    out.textContent = "";
  }
}

async function loadStats() {
  const out = document.getElementById("statsOutput");
  try {
    const payload = await requestJson("/stats");
    const lines = [];
    lines.push(`status: ${payload.kg_version ? "KG 可读" : "KG 信息不足"}`);
    lines.push(`nodes = ${payload.node_count || 0}`);
    lines.push(`edges = ${payload.edge_count || 0}`);
    lines.push(`canonical_entity_count = ${payload.canonical_entity_count || 0}`);
    lines.push(`evidence_backed_relation_claim_count = ${payload.evidence_backed_relation_claim_count || 0}`);
    lines.push(`provenance_edge_count = ${payload.provenance_edge_count || 0}`);
    if (payload.layered_statistics) {
      const A = payload.layered_statistics.A || {};
      const B = payload.layered_statistics.B || {};
      const C = payload.layered_statistics.C || {};
      lines.push(`A-layer nodes=${A.node_count || 0}, edges=${A.edge_count || 0}`);
      lines.push(`B-layer nodes=${B.node_count || 0}, edges=${B.edge_count || 0}`);
      lines.push(`C-layer nodes=${C.node_count || 0}, edges=${C.edge_count || 0}`);
    }
    lines.push(`safety_notice = ${payload.safety_notice || safetyNotice.title}`);
    out.textContent = lines.join("\n");
  } catch (error) {
    out.textContent = `加载统计失败：${error.message}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setNotice();
  bindTabs();
  buildDemoCases();
  refreshHealth();
  loadStats();

  document.getElementById("qaForm").addEventListener("submit", runQaFromForm);
  document.getElementById("graphForm").addEventListener("submit", loadGraph);
  document.getElementById("imageForm").addEventListener("submit", loadImages);
  document.getElementById("refreshStats").addEventListener("click", loadStats);

  setInterval(refreshHealth, 30000);
});
