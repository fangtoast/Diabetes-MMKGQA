const API_ROOT = location.origin;
const SAFETY_NOTICE = "课程演示、非临床诊断：本内容仅用于教学演示，不构成医疗建议。";

const state = {
  health: null,
  activeSection: "qa",
  lastQa: null,
  lastGraph: null,
  selectedNode: null,
  selectedNodeId: null,
  hoveredNodeId: null,
  selectedLinkId: null,
  hoveredLinkId: null,
  searchHitNodeId: null,
  graphSimulation: null,
  graphZoom: null,
  graphElements: null,
  graphTransform: null,
  graphRequestId: 0,
};

const graphDefaults = {
  limit: 120,
  depth: 2,
  nodeSize: 7,
  linkWidth: 1,
  labelDensity: 15,
  labelOpacity: 0.82,
  centerForce: 3,
  repelForce: -280,
  linkDistance: 112,
};

const demoCases = [
  {
    title: "成功：糖网影像",
    kind: "success",
    question: "糖尿病视网膜病变有哪些影像示例",
    note: "中文意图和实体链接命中 C 层影像。",
  },
  {
    title: "成功：糖尿病症状",
    kind: "success",
    question: "糖尿病有哪些症状",
    note: "返回证据、来源和 KG 版本。",
  },
  {
    title: "成功：高血压 ICD",
    kind: "success",
    question: "高血压的ICD编码是什么",
    note: "中文 ICD 触发词与实体链接。",
  },
  {
    title: "边界：未知问题",
    kind: "boundary",
    question: "这个平台能诊断我的眼底图吗",
    note: "应返回受控 not_found 或安全边界。",
  },
];

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(raw) {
  if (raw === null || raw === undefined) return "";
  return String(raw)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setStatus(id, text, tone = "") {
  const el = $(id);
  if (!el) return;
  el.textContent = text || "";
  el.classList.remove("ok", "warn");
  if (tone) el.classList.add(tone);
}

function renderRaw(payload) {
  $("rawJson").textContent = payload ? JSON.stringify(payload, null, 2) : "暂无结果。";
}

async function requestJson(url, init = {}) {
  const response = await fetch(`${API_ROOT}${url}`, {
    headers: { Accept: "application/json", ...(init.headers || {}) },
    ...init,
  });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const detail = body.detail || body.message || body || "请求失败";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function activateSection(sectionKey) {
  state.activeSection = sectionKey;
  document.querySelectorAll("[data-section]").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.section === sectionKey);
  });
  document.querySelectorAll(".panel-view").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.panel === sectionKey);
  });
  const url = new URL(window.location.href);
  url.searchParams.set("tab", sectionKey);
  window.history.replaceState({}, "", url);

  if (sectionKey === "graph") {
    if (!state.lastGraph) {
      loadOverviewGraph();
    } else {
      window.requestAnimationFrame(() => renderGraph(state.lastGraph));
    }
  }
  if (sectionKey === "stats") loadStats();
  if (sectionKey === "images" && !$("imageOutput").children.length) loadImages();
}

async function refreshHealth() {
  try {
    const payload = await requestJson("/health");
    state.health = payload;
    $("healthDot").classList.toggle("ready", payload.backend_ready === true);
    $("healthDot").classList.toggle("blocked", payload.backend_ready !== true);
    $("healthSummary").textContent = payload.backend_ready
      ? `ready · nodes ${payload.summary?.node_count || 0} · images ${payload.summary?.image_count || 0}`
      : "blocked · 请先构建 KG";
    $("kgVersion").textContent = `KG version: ${payload.summary ? "0.2.0" : "--"}`;
  } catch (error) {
    $("healthDot").classList.add("blocked");
    $("healthSummary").textContent = `health failed · ${error.message}`;
  }
}

function nodeLabel(node) {
  return node.canonical_name || node.node_id || "unknown";
}

function compactId(value) {
  const text = String(value || "");
  return text.length > 14 ? `${text.slice(0, 8)}...${text.slice(-4)}` : text;
}

function compactText(value, limit = 42) {
  const text = String(value || "");
  return text.length > limit ? `${text.slice(0, Math.max(0, limit - 1))}…` : text;
}

function missingText(value) {
  const text = String(value ?? "").trim();
  return text ? text : "当前图谱记录中没有该字段。";
}

function stableHash(value) {
  const text = String(value || "");
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function cssIdentifier(value) {
  return String(value || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-");
}

function isImageNode(node) {
  return node?.node_type === "Image";
}

function isRuleNode(node) {
  return new Set(["Guideline", "StandardRule", "DiagnosticThreshold", "ReferenceRange", "ICD_Code"]).has(node?.node_type);
}

function tag(text, cls = "") {
  return `<span class="tag ${cls}">${escapeHtml(text)}</span>`;
}

function graphContextForNode(nodeId) {
  const graph = state.lastGraph || {};
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const nodeById = new Map(nodes.map((node) => [node.node_id, node]));
  const incidentEdges = edges.filter((edge) => edge.head_id === nodeId || edge.tail_id === nodeId);
  const neighbors = incidentEdges
    .map((edge) => (edge.head_id === nodeId ? edge.tail_id : edge.head_id))
    .filter(Boolean)
    .map((id) => nodeById.get(id))
    .filter(Boolean);
  const unique = (values) => [...new Set(values.map((value) => String(value || "").trim()).filter(Boolean))];
  return {
    incidentEdges,
    neighbors,
    imageCount: neighbors.filter((node) => node.node_type === "Image").length,
    relationSummary: unique(incidentEdges.map((edge) => edge.relation)).slice(0, 8),
    evidenceIds: unique(incidentEdges.map((edge) => edge.evidence_id)),
    sourceIds: unique(incidentEdges.map((edge) => edge.source_id || edge.source_ids)),
  };
}

function renderGraphEvidenceForNode(node, context) {
  const tagList = (values, limit = 16) => {
    const visible = values.slice(0, limit).map((id) => tag(id)).join("");
    const remaining = values.length - limit;
    return remaining > 0 ? `${visible}${tag(`+${remaining} more`, "muted")}` : visible || tag("当前图谱记录中没有该字段。", "muted");
  };
  $("evidencePanel").innerHTML = `
    <div class="note-kv"><span>selected</span><span>${escapeHtml(nodeLabel(node))}</span></div>
    <div class="note-kv"><span>kg_version</span><span>${escapeHtml(missingText(node.kg_version))}</span></div>
    <div><strong>邻接 evidence</strong><div class="meta-row">${tagList(context.evidenceIds)}</div></div>
    <div><strong>邻接 source</strong><div class="meta-row">${tagList(context.sourceIds)}</div></div>
  `;
}

function renderRelationDetail(edge) {
  if (!edge) return;
  const elements = state.graphElements;
  const nodeById = elements?.nodeById || new Map();
  const sourceId = edge.source?.id || edge.head_id || edge.source;
  const targetId = edge.target?.id || edge.tail_id || edge.target;
  const sourceNode = nodeById.get(sourceId) || state.lastGraph?.nodes?.find((node) => node.node_id === sourceId) || {};
  const targetNode = nodeById.get(targetId) || state.lastGraph?.nodes?.find((node) => node.node_id === targetId) || {};
  $("entityNote").classList.remove("note-empty");
  $("entityNote").innerHTML = `
    <div class="note-title">${escapeHtml(edge.relation || "关系详情")}</div>
    <div class="meta-row">
      ${tag(compactId(edge.edge_id || "no edge_id"))}
      ${tag(`Layer ${edge.knowledge_layer || "-"}`, String(edge.knowledge_layer || "").toLowerCase())}
      ${tag(edge.normalized_relation || edge.relation || "-")}
    </div>
    <div class="note-kv"><span>头实体</span><span>${escapeHtml(nodeLabel(sourceNode) || missingText(sourceId))}</span></div>
    <div class="note-kv"><span>关系</span><span>${escapeHtml(missingText(edge.relation))}</span></div>
    <div class="note-kv"><span>尾实体</span><span>${escapeHtml(nodeLabel(targetNode) || missingText(targetId))}</span></div>
    <div class="note-kv"><span>方向</span><span>${escapeHtml(compactId(sourceId))} → ${escapeHtml(compactId(targetId))}</span></div>
    <div class="note-kv"><span>evidence_id</span><span>${escapeHtml(missingText(edge.evidence_id))}</span></div>
    <div class="note-kv"><span>source_id</span><span>${escapeHtml(missingText(edge.source_id))}</span></div>
    <div class="note-kv"><span>extraction</span><span>${escapeHtml(missingText(edge.extraction_method))}</span></div>
    <div class="note-kv"><span>confidence</span><span>${escapeHtml(missingText(edge.confidence))}</span></div>
    <div class="note-kv"><span>kg_version</span><span>${escapeHtml(missingText(edge.kg_version))}</span></div>
  `;
  $("evidencePanel").innerHTML = `
    <div class="note-kv"><span>edge_id</span><span>${escapeHtml(missingText(edge.edge_id))}</span></div>
    <div class="note-kv"><span>raw_relation</span><span>${escapeHtml(missingText(edge.raw_relation))}</span></div>
    <div class="note-kv"><span>normalized</span><span>${escapeHtml(missingText(edge.normalized_relation))}</span></div>
    <div class="note-kv"><span>safety</span><span>${escapeHtml(SAFETY_NOTICE)}</span></div>
  `;
}

function renderEntityNote(node) {
  state.selectedNode = node;
  if (!node) {
    const graph = state.lastGraph;
    $("entityNote").classList.add("note-empty");
    $("entityNote").innerHTML = graph
      ? `
        <div>点击图谱节点查看实体详情，点击关系查看 evidence/source。</div>
        <div class="note-kv"><span>当前子图</span><span>${escapeHtml(graph.node_count || graph.nodes?.length || 0)} 个节点，${escapeHtml(graph.edge_count || graph.edges?.length || 0)} 条关系</span></div>
        <div class="note-kv"><span>模式</span><span>${escapeHtml(graph.mode || (graph.center_node_id ? "local" : "overview"))}</span></div>
      `
      : "点击图谱节点或搜索结果后查看实体详情。";
    return;
  }
  $("entityNote").classList.remove("note-empty");
  const context = graphContextForNode(node.node_id);
  const layerClass = String(node.knowledge_layer || "").toLowerCase();
  $("entityNote").innerHTML = `
    <div class="note-title">${escapeHtml(nodeLabel(node))}</div>
    <div class="meta-row">
      ${tag(node.node_type || "-", layerClass)}
      ${tag(`Layer ${node.knowledge_layer || "-"}`, layerClass)}
      ${tag(compactId(node.node_id))}
    </div>
    <div class="note-kv"><span>node_id</span><span>${escapeHtml(missingText(node.node_id))}</span></div>
    <div class="note-kv"><span>canonical</span><span>${escapeHtml(missingText(node.canonical_name))}</span></div>
    <div class="note-kv"><span>aliases</span><span>${escapeHtml(missingText(node.aliases || node.synonyms))}</span></div>
    <div class="note-kv"><span>连接摘要</span><span>${escapeHtml(context.relationSummary.join(", ") || "当前子图没有邻接关系。")}</span></div>
    <div class="note-kv"><span>关联图像</span><span>${escapeHtml(context.imageCount)}</span></div>
    <div class="note-kv"><span>source_ids</span><span>${escapeHtml(missingText(node.source_ids))}</span></div>
    <div class="note-kv"><span>kg_version</span><span>${escapeHtml(missingText(node.kg_version))}</span></div>
    <div class="note-kv"><span>description</span><span>${escapeHtml(missingText(node.description || node.text))}</span></div>
  `;
  renderGraphEvidenceForNode(node, context);
}

function renderEvidence(payload) {
  const rows = [...(payload?.rows || []), ...(payload?.images || [])];
  const uniqueValues = (values) => [...new Set(values.map((value) => `${value || ""}`.trim()).filter(Boolean))];
  const evidenceIds = uniqueValues([...(payload?.evidence_ids || []), ...rows.map((row) => row.evidence_id)]);
  const sourceIds = uniqueValues([...(payload?.source_ids || []), ...rows.map((row) => row.source_id)]);
  const tagList = (values, limit = 24) => {
    const visible = values.slice(0, limit).map((id) => tag(id)).join("");
    const remaining = values.length - limit;
    return remaining > 0 ? `${visible}${tag(`+${remaining} more`, "muted")}` : visible || tag("无");
  };
  $("evidencePanel").innerHTML = `
    <div class="note-kv"><span>status</span><span>${escapeHtml(payload?.status || "-")}</span></div>
    <div class="note-kv"><span>intent</span><span>${escapeHtml(payload?.intent || "-")}</span></div>
    <div class="note-kv"><span>kg_version</span><span>${escapeHtml(payload?.kg_version || "-")}</span></div>
    <div><strong>evidence_ids</strong><div class="meta-row">${tagList(evidenceIds)}</div></div>
    <div><strong>source_ids</strong><div class="meta-row">${tagList(sourceIds)}</div></div>
  `;
}

function renderQa(payload, targetId = "qaOutput") {
  const rows = payload.rows || [];
  const images = payload.images || [];
  const entity = payload.entity;
  const html = [];

  html.push(`
    <article class="answer-card">
      <h3>${payload.status === "ok" ? "结构化回答" : "受控响应"}</h3>
      <p>${escapeHtml(payload.answer || "暂无回答。")}</p>
      <div class="meta-row">
        ${tag(`status: ${payload.status || "-"}`)}
        ${tag(`intent: ${payload.intent || "-"}`)}
        ${tag(`kg: ${payload.kg_version || "-"}`)}
      </div>
    </article>
  `);

  if (entity) {
    html.push(`
      <article class="answer-card">
        <h3>命中实体</h3>
        <p>${escapeHtml(entity.canonical_name)} · ${escapeHtml(entity.node_type)} · Layer ${escapeHtml(entity.knowledge_layer)}</p>
        <div class="meta-row">${tag(entity.node_id || "")}</div>
      </article>
    `);
    renderEntityNote(entity);
  }

  if (rows.length) {
    html.push(`<div class="relation-list">${rows.slice(0, 12).map(renderRelationCard).join("")}</div>`);
  }

  if (images.length) {
    html.push(`<div class="image-grid">${images.slice(0, 8).map(renderImageCard).join("")}</div>`);
  }

  $(targetId).innerHTML = html.join("");
  renderEvidence(payload);
  renderRaw(payload);
}

function renderRelationCard(row) {
  return `
    <article class="relation-card">
      <h3>${escapeHtml(row.relation || "relation")}</h3>
      <p>${escapeHtml(compactId(row.head_id))} -> ${escapeHtml(compactId(row.tail_id))}</p>
      <div class="meta-row">
        ${tag(row.source_id || "-")}
        ${tag(row.evidence_id || "no evidence")}
      </div>
    </article>
  `;
}

function renderImageCard(row) {
  const src = row.preview_url ? `${API_ROOT}${row.preview_url}` : "";
  const fallback = `this.style.display='none'; this.nextElementSibling.classList.remove('hidden')`;
  return `
    <article class="image-card">
      ${src ? `<img class="image-preview" src="${escapeHtml(src)}" alt="${escapeHtml(row.image_id || "medical image")}" onerror="${fallback}" />` : ""}
      <div class="image-preview hidden">预览不可用</div>
      <div class="image-card-body">
        <h3>${escapeHtml(row.dataset || row.image_id || "影像")}</h3>
        <p>${escapeHtml(row.grade || "-")} · ${escapeHtml(row.split || "-")} · index ${escapeHtml(row.image_index || "-")}</p>
        <div class="meta-row">
          ${tag(compactId(row.image_id || ""))}
          ${tag(row.source_id || "-")}
          ${tag(row.grade_code ? `grade ${row.grade_code}` : "grade -")}
        </div>
      </div>
    </article>
  `;
}

async function runQa(question, targetId = "qaOutput") {
  const q = (question || "").trim();
  if (!q) {
    setStatus("qaStatus", "请输入问题。", "warn");
    return null;
  }
  setStatus("qaStatus", "正在检索意图、实体和证据...", "ok");
  try {
    const payload = await requestJson("/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q }),
    });
    state.lastQa = payload;
    renderQa(payload, targetId);
    setStatus("qaStatus", `完成：${payload.status} · images ${payload.images?.length || 0} · rows ${payload.rows?.length || 0}`, "ok");
    if (payload.entity?.node_id) {
      $("graphSearchInput").value = payload.entity.node_id;
    }
    return payload;
  } catch (error) {
    setStatus("qaStatus", `失败：${error.message}`, "warn");
    renderRaw({ error: error.message, safety_notice: SAFETY_NOTICE });
    return null;
  }
}

async function searchEntities(query, target = "entitySearchResults") {
  const q = (query || "").trim();
  const container = $(target);
  if (!q) {
    container.textContent = "请输入实体名称或别名。";
    return [];
  }
  container.textContent = "搜索中...";
  try {
    const payload = await requestJson(`/entities/search?query=${encodeURIComponent(q)}&limit=10`);
    const items = payload.items || [];
    if (!items.length) {
      container.textContent = "没有匹配实体。";
      return [];
    }
    container.innerHTML = "";
    items.forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-result";
      button.innerHTML = `<strong>${escapeHtml(nodeLabel(item))}</strong><span>${escapeHtml(item.node_type)} · Layer ${escapeHtml(item.knowledge_layer)} · ${escapeHtml(compactId(item.node_id))}</span>`;
      button.addEventListener("click", () => {
        renderEntityNote(item);
        $("graphSearchInput").value = item.node_id;
        activateSection("graph");
        loadLocalGraph(item.node_id);
      });
      container.appendChild(button);
    });
    return items;
  } catch (error) {
    container.textContent = `搜索失败：${error.message}`;
    return [];
  }
}

function graphSettings() {
  return {
    limit: Number($("graphLimit").value || graphDefaults.limit),
    depth: Number($("graphDepth").value || graphDefaults.depth),
    includeImages: $("includeImages").checked,
    showArrows: $("showArrows").checked,
    showEvidenceNodes: $("showEvidenceNodes")?.checked === true,
    nodeSize: Number($("nodeSize").value || graphDefaults.nodeSize),
    linkWidth: Number($("linkWidth").value || graphDefaults.linkWidth),
    labelDensity: Number($("labelDensity").value || graphDefaults.labelDensity),
    labelOpacity: Number($("labelOpacity").value || graphDefaults.labelOpacity * 100) / 100,
    centerForce: Number($("centerForce").value || graphDefaults.centerForce * 10) / 10,
    repelForce: -Number($("repelForce").value || Math.abs(graphDefaults.repelForce)),
    linkDistance: Number($("linkDistance").value || graphDefaults.linkDistance),
    layers: Array.from(document.querySelectorAll(".layer-filter:checked")).map((item) => item.value),
  };
}

async function loadOverviewGraph() {
  const requestId = (state.graphRequestId += 1);
  const settings = graphSettings();
  const params = new URLSearchParams();
  params.set("limit", String(settings.limit));
  params.set("include_images", String(settings.includeImages));
  if (settings.layers.length) params.set("layers", settings.layers.join(","));
  setStatus("graphStatus", "正在载入全局概览...", "ok");
  try {
    const payload = await requestJson(`/graph/overview?${params.toString()}`);
    if (requestId !== state.graphRequestId) return;
    state.lastGraph = payload;
    state.selectedNodeId = null;
    state.selectedLinkId = null;
    renderGraph(payload);
    setStatus("graphStatus", `概览：nodes=${payload.node_count}, edges=${payload.edge_count}`, "ok");
    renderRaw(payload);
  } catch (error) {
    if (requestId !== state.graphRequestId) return;
    setStatus("graphStatus", `图谱载入失败：${error.message}`, "warn");
  }
}

async function resolveNodeId(input) {
  const value = (input || "").trim();
  if (!value) return "";
  if (/^[a-f0-9]{40}$/i.test(value) || (/^[A-Za-z0-9._-]+$/.test(value) && value.length > 12)) {
    return value;
  }
  const items = await searchEntities(value, "entitySearchResults");
  return items[0]?.node_id || "";
}

async function loadLocalGraph(nodeId = null) {
  const requestId = (state.graphRequestId += 1);
  const settings = graphSettings();
  const center = nodeId || (await resolveNodeId($("graphSearchInput").value));
  if (!center) {
    setStatus("graphStatus", "请先搜索并选择一个中心实体。", "warn");
    return;
  }
  setStatus("graphStatus", "正在打开局部图谱...", "ok");
  try {
    const payload = await requestJson(`/graph/subgraph?center_node_id=${encodeURIComponent(center)}&max_hops=${settings.depth}`);
    if (requestId !== state.graphRequestId) return;
    state.lastGraph = payload;
    state.selectedNodeId = center;
    state.selectedLinkId = null;
    renderGraph(payload);
    setStatus("graphStatus", `局部图谱：nodes=${payload.node_count}, edges=${payload.edge_count}`, "ok");
    window.requestAnimationFrame(() => focusGraphNode(center, { center: true }));
    renderRaw(payload);
  } catch (error) {
    if (requestId !== state.graphRequestId) return;
    setStatus("graphStatus", `局部图谱失败：${error.message}`, "warn");
  }
}

function nodeDegreeMap(graph) {
  const counts = new Map();
  (graph.edges || []).forEach((edge) => {
    counts.set(edge.head_id, (counts.get(edge.head_id) || 0) + 1);
    counts.set(edge.tail_id, (counts.get(edge.tail_id) || 0) + 1);
  });
  return counts;
}

function linkKey(link) {
  return link.edge_id || `${link.head_id || link.source}|${link.relation}|${link.tail_id || link.target}`;
}

function buildAdjacency(links) {
  const adjacency = new Map();
  links.forEach((link) => {
    const sourceId = link.source?.id || link.source || link.head_id;
    const targetId = link.target?.id || link.target || link.tail_id;
    if (!sourceId || !targetId) return;
    if (!adjacency.has(sourceId)) adjacency.set(sourceId, new Set());
    if (!adjacency.has(targetId)) adjacency.set(targetId, new Set());
    adjacency.get(sourceId).add(targetId);
    adjacency.get(targetId).add(sourceId);
  });
  return adjacency;
}

function connectedTo(nodeId, otherId, adjacency) {
  return nodeId === otherId || adjacency.get(nodeId)?.has(otherId);
}

function nodeDistanceTier(nodeId, activeNodeId, adjacency) {
  if (!activeNodeId) return null;
  if (nodeId === activeNodeId) return 0;
  const direct = adjacency.get(activeNodeId);
  if (direct?.has(nodeId)) return 1;
  for (const neighborId of direct || []) {
    if (adjacency.get(neighborId)?.has(nodeId)) return 2;
  }
  return null;
}

function linkTouchesNode(link, nodeId) {
  const sourceId = link.source?.id || link.source || link.head_id;
  const targetId = link.target?.id || link.target || link.tail_id;
  return sourceId === nodeId || targetId === nodeId;
}

function initialGraphPosition(node, index, count, width, height) {
  const hash = stableHash(node.id || node.node_id || index);
  const jitter = ((hash % 1000) / 1000 - 0.5) * 0.16;
  const angle = ((hash % 6283) / 1000) + index * 2.399963229728653;
  const rank = count <= 1 ? 0.2 : index / Math.max(1, count - 1);
  const radius = Math.min(width, height) * (0.18 + (rank % 0.48)) * (0.86 + jitter);
  const layerPull = {
    A: [-0.18, -0.08],
    B: [0.18, -0.1],
    C: [0.02, 0.16],
  }[node.knowledge_layer] || [0, 0];
  return {
    x: width / 2 + width * layerPull[0] + Math.cos(angle) * radius,
    y: height / 2 + height * layerPull[1] + Math.sin(angle) * radius * 0.82,
  };
}

function nodeImportance(node, degree) {
  const typeWeight = {
    Disease: 7,
    Guideline: 6,
    StandardRule: 6,
    DiagnosticThreshold: 5,
    TestItem: 5,
    ICD_Code: 4,
    ImageGrade: 4,
    Dataset: 3,
    Image: 1,
    EvidenceChunk: -4,
  }[node.node_type] || 2;
  return typeWeight + Math.log2((degree.get(node.id) || 0) + 1) * 2;
}

function visualRadius(node, settings, degree) {
  const degreeBoost = Math.min(3.4, Math.log2((degree.get(node.id) || 0) + 1) * 1.15);
  const typeBoost = isRuleNode(node) ? 1.1 : node.node_type === "Disease" ? 1.4 : 0;
  return Math.max(4, Math.min(11.5, settings.nodeSize + degreeBoost + typeBoost));
}

function graphNodeClass(node) {
  return [
    "graph-node-group",
    `layer-${cssIdentifier(node.knowledge_layer)}`,
    `type-${cssIdentifier(node.node_type)}`,
  ].join(" ");
}

function addNodeShape(selection) {
  selection.each(function (node) {
    const group = d3.select(this);
    const r = node.visualRadius || 7;
    if (isImageNode(node)) {
      group
        .append("rect")
        .attr("class", "graph-node-shape")
        .attr("x", -r)
        .attr("y", -r)
        .attr("width", r * 2)
        .attr("height", r * 2)
        .attr("rx", Math.max(2.5, r * 0.32));
      return;
    }
    if (isRuleNode(node)) {
      group
        .append("path")
        .attr("class", "graph-node-shape")
        .attr("d", `M0,${-r} L${r},0 L0,${r} L${-r},0 Z`);
      return;
    }
    group.append("circle").attr("class", "graph-node-shape").attr("r", r);
  });
}

function applyNodeSize(nodeGroup) {
  nodeGroup.each(function (node) {
    const group = d3.select(this);
    const r = node.visualRadius || 7;
    group.select(".graph-node-hit").attr("r", Math.max(15, r + 8));
    const shape = group.select(".graph-node-shape");
    if (isImageNode(node)) {
      shape.attr("x", -r).attr("y", -r).attr("width", r * 2).attr("height", r * 2).attr("rx", Math.max(2.5, r * 0.32));
    } else if (isRuleNode(node)) {
      shape.attr("d", `M0,${-r} L${r},0 L0,${r} L${-r},0 Z`);
    } else {
      shape.attr("r", r);
    }
  });
}

function labelPriority(node, elements) {
  if (!elements) return node.importance || 0;
  const activeNodeId = state.hoveredNodeId || state.selectedNodeId;
  if (node.id === state.selectedNodeId) return 1000;
  if (node.id === state.hoveredNodeId) return 980;
  if (node.id === state.searchHitNodeId) return 940;
  if (node.id === elements.centerNodeId) return 910;
  if (activeNodeId && connectedTo(activeNodeId, node.id, elements.adjacency)) return 720 + (node.importance || 0);
  if (state.selectedLinkId) {
    const selected = elements.links.find((link) => linkKey(link) === state.selectedLinkId);
    if (selected && linkTouchesNode(selected, node.id)) return 840 + (node.importance || 0);
  }
  return node.importance || 0;
}

function visibleLabelIds(elements) {
  if (!elements) return new Set();
  const transform = state.graphTransform || d3.zoomIdentity;
  const density = Math.max(6, Math.min(24, elements.settings.labelDensity || 15));
  const zoomBonus = transform.k > 1.35 ? Math.round((transform.k - 1.35) * 6) : 0;
  const maxLabels = Math.min(elements.nodes.length, density + zoomBonus);
  const sorted = [...elements.nodes]
    .map((node) => ({ node, priority: labelPriority(node, elements) }))
    .sort((a, b) => b.priority - a.priority || String(a.node.id).localeCompare(String(b.node.id)));
  const selected = new Set();
  const boxes = [];
  const labelScale = Math.max(0.72, Math.min(1.2, transform.k));
  for (const item of sorted) {
    if (selected.size >= maxLabels && item.priority < 900) continue;
    if (!Number.isFinite(item.node.x) || !Number.isFinite(item.node.y)) continue;
    const label = compactText(nodeLabel(item.node), item.priority >= 900 ? 34 : 24);
    const width = Math.max(38, label.length * 6.4 * labelScale);
    const height = item.priority >= 900 ? 18 : 14;
    const box = {
      x1: item.node.x + 10,
      y1: item.node.y - height,
      x2: item.node.x + 10 + width,
      y2: item.node.y + height,
    };
    const overlaps = boxes.some((other) => !(box.x2 < other.x1 || box.x1 > other.x2 || box.y2 < other.y1 || box.y1 > other.y2));
    if (!overlaps || item.priority >= 900) {
      selected.add(item.node.id);
      boxes.push(box);
    }
  }
  return selected;
}

function focusGraphNode(nodeId, { center = false } = {}) {
  const elements = state.graphElements;
  if (!elements) return;
  const node = elements.nodeById.get(nodeId);
  if (!node) return;
  state.selectedNodeId = nodeId;
  state.selectedLinkId = null;
  state.searchHitNodeId = nodeId;
  renderEntityNote(node);
  refreshGraphClasses();
  if (center) centerOnNode(nodeId);
  window.setTimeout(() => {
    if (state.searchHitNodeId === nodeId) {
      state.searchHitNodeId = null;
      refreshGraphClasses();
    }
  }, 1400);
}

function focusGraphLink(edge) {
  if (!edge) return;
  state.selectedLinkId = linkKey(edge);
  state.selectedNodeId = null;
  renderRelationDetail(edge);
  refreshGraphClasses();
}

function clearGraphFocus({ keepInspector = false } = {}) {
  state.selectedNodeId = null;
  state.hoveredNodeId = null;
  state.selectedLinkId = null;
  state.hoveredLinkId = null;
  state.searchHitNodeId = null;
  if (!keepInspector) renderEntityNote(null);
  refreshGraphClasses();
}

function refreshGraphClasses() {
  const elements = state.graphElements;
  if (!elements) return;
  const activeNodeId = state.hoveredNodeId || state.selectedNodeId;
  const selectedLink = state.selectedLinkId ? elements.links.find((link) => linkKey(link) === state.selectedLinkId) : null;
  const labelIds = visibleLabelIds(elements);

  elements.nodeGroup
    .classed("is-selected", (node) => node.id === state.selectedNodeId)
    .classed("is-hovered", (node) => node.id === state.hoveredNodeId)
    .classed("is-search-hit", (node) => node.id === state.searchHitNodeId)
    .classed("is-neighbor", (node) => nodeDistanceTier(node.id, activeNodeId, elements.adjacency) === 1)
    .classed("is-second-neighbor", (node) => nodeDistanceTier(node.id, activeNodeId, elements.adjacency) === 2)
    .classed("is-muted", (node) => {
      if (selectedLink) return !linkTouchesNode(selectedLink, node.id);
      if (!activeNodeId) return false;
      return nodeDistanceTier(node.id, activeNodeId, elements.adjacency) === null;
    });

  elements.linkGroup
    .classed("is-selected", (link) => linkKey(link) === state.selectedLinkId)
    .classed("is-hovered", (link) => linkKey(link) === state.hoveredLinkId)
    .classed("is-neighbor", (link) => !!activeNodeId && linkTouchesNode(link, activeNodeId))
    .classed("is-muted", (link) => {
      if (selectedLink) return linkKey(link) !== state.selectedLinkId;
      if (!activeNodeId) return false;
      return !linkTouchesNode(link, activeNodeId);
    });

  elements.label
    .classed("is-visible", (node) => labelIds.has(node.id))
    .text((node) => compactText(nodeLabel(node), labelPriority(node, elements) >= 900 ? 34 : 24));
  elements.labelBg.each(function (node) {
    const textWidth = Math.max(34, compactText(nodeLabel(node), 34).length * 7);
    d3.select(this).attr("x", 8).attr("y", -15).attr("width", textWidth).attr("height", 20).attr("rx", 5);
  });
  updateArrowVisibility();
}

function updateGraphPositions() {
  const elements = state.graphElements;
  if (!elements) return;
  const { width, height, linkGroup, nodeGroup } = elements;
  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const resetIfNeeded = (item) => {
    const maxDrift = Math.max(width, height) * 8;
    if (!Number.isFinite(item.x) || !Number.isFinite(item.y) || Math.abs(item.x) > maxDrift || Math.abs(item.y) > maxDrift) {
      item.x = Number.isFinite(item.homeX) ? item.homeX : width / 2;
      item.y = Number.isFinite(item.homeY) ? item.homeY : height / 2;
      item.vx = 0;
      item.vy = 0;
    }
    return item;
  };
  const safeX = (item) => clamp(resetIfNeeded(item).x, 20, Math.max(20, width - 20));
  const safeY = (item) => clamp(resetIfNeeded(item).y, 20, Math.max(20, height - 20));

  linkGroup.each(function (link) {
    const sourceX = safeX(link.source);
    const sourceY = safeY(link.source);
    const targetX = safeX(link.target);
    const targetY = safeY(link.target);
    d3.select(this)
      .selectAll("line")
      .attr("x1", sourceX)
      .attr("y1", sourceY)
      .attr("x2", targetX)
      .attr("y2", targetY);
    d3.select(this)
      .select(".graph-edge-label")
      .attr("x", (sourceX + targetX) / 2)
      .attr("y", (sourceY + targetY) / 2 - 4);
  });

  nodeGroup.attr("transform", (node) => `translate(${safeX(node)},${safeY(node)})`);
}

function updateArrowVisibility() {
  const elements = state.graphElements;
  if (!elements) return;
  const show = elements.settings.showArrows && (state.selectedNodeId || state.selectedLinkId || state.hoveredNodeId || state.hoveredLinkId);
  const activeNodeId = state.hoveredNodeId || state.selectedNodeId;
  elements.linkLine.attr("marker-end", (link) => {
    if (!show) return null;
    if (linkKey(link) === state.selectedLinkId || linkKey(link) === state.hoveredLinkId) return "url(#arrow)";
    if (activeNodeId && linkTouchesNode(link, activeNodeId)) return "url(#arrow)";
    return null;
  });
}

function renderGraph(graph) {
  if (!window.d3) {
    $("graphEmpty").textContent = "D3 本地脚本未加载，无法渲染图谱。";
    return;
  }

  const settings = graphSettings();
  const svg = d3.select("#graphCanvas");
  svg.selectAll("*").remove();
  if (state.graphSimulation) state.graphSimulation.stop();

  const stage = $("graphCanvas").getBoundingClientRect();
  const width = Math.max(stage.width, 640);
  const height = Math.max(stage.height, 520);
  const rawNodes = (graph.nodes || []).map((node) => ({ ...node, id: node.node_id }));
  const nodes = rawNodes.filter((node) => settings.showEvidenceNodes || node.node_type !== "EvidenceChunk");
  const nodeIds = new Set(nodes.map((node) => node.id));
  const links = (graph.edges || [])
    .filter((edge) => nodeIds.has(edge.head_id) && nodeIds.has(edge.tail_id))
    .map((edge) => ({ ...edge, source: edge.head_id, target: edge.tail_id }));

  $("graphEmpty").classList.toggle("hidden", nodes.length > 0);
  if (!nodes.length) {
    $("graphEmpty").textContent = "没有可显示的图谱节点。";
    return;
  }

  svg.attr("viewBox", [0, 0, width, height]);
  const nodeById = new Map(nodes.map((item) => [item.id, item]));
  const degree = nodeDegreeMap({ edges: links });
  nodes.forEach((item, index) => {
    const position = initialGraphPosition(item, index, nodes.length, width, height);
    item.x = position.x;
    item.y = position.y;
    item.homeX = item.x;
    item.homeY = item.y;
    item.importance = nodeImportance(item, degree);
    item.visualRadius = visualRadius(item, settings, degree);
  });
  links.forEach((item) => {
    item.source = nodeById.get(item.source) || item.source;
    item.target = nodeById.get(item.target) || item.target;
  });

  const defs = svg.append("defs");
  defs
    .append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("fill", "rgba(238,239,242,0.72)")
    .attr("d", "M0,-5L10,0L0,5");

  const root = svg.append("g").attr("class", "graph-root");
  state.graphZoom = d3.zoom().scaleExtent([0.32, 3.6]).on("zoom", (event) => {
    state.graphTransform = event.transform;
    root.attr("transform", event.transform);
    refreshGraphClasses();
  });
  svg.call(state.graphZoom).on("dblclick.zoom", null);
  svg.on("click", (event) => {
    if (event.target === svg.node()) clearGraphFocus();
  });

  const linkGroup = root
    .append("g")
    .attr("class", "graph-links")
    .selectAll("g")
    .data(links)
    .join("g")
    .attr("class", "graph-link-group")
    .attr("tabindex", 0)
    .on("mouseenter", (_event, link) => {
      state.hoveredLinkId = linkKey(link);
      refreshGraphClasses();
    })
    .on("mouseleave", () => {
      state.hoveredLinkId = null;
      refreshGraphClasses();
    })
    .on("click", (event, link) => {
      event.stopPropagation();
      focusGraphLink(link);
    })
    .on("keydown", (event, link) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        focusGraphLink(link);
      }
    });

  linkGroup.append("line").attr("class", "graph-link-hit");
  const linkLine = linkGroup
    .append("line")
    .attr("class", "graph-link")
    .attr("stroke-width", Math.max(0.6, settings.linkWidth * 0.78));
  linkGroup.append("text").attr("class", "graph-edge-label").text((link) => compactText(link.relation, 28));

  const nodeGroup = root
    .append("g")
    .attr("class", "graph-nodes")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .attr("class", graphNodeClass)
    .attr("tabindex", 0)
    .on("mouseenter", (_event, item) => {
      state.hoveredNodeId = item.id;
      refreshGraphClasses();
    })
    .on("mouseleave", () => {
      state.hoveredNodeId = null;
      refreshGraphClasses();
    })
    .on("click", (event, item) => {
      event.stopPropagation();
      focusGraphNode(item.id, { center: false });
    })
    .on("dblclick", (event, item) => {
      event.stopPropagation();
      $("graphSearchInput").value = item.id;
      loadLocalGraph(item.id);
    })
    .on("keydown", (event, item) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        focusGraphNode(item.id, { center: false });
      }
    })
    .call(
      d3
        .drag()
        .on("start", (event, item) => {
          if (!event.active) state.graphSimulation.alphaTarget(0.3).restart();
          item.fx = item.x;
          item.fy = item.y;
        })
        .on("drag", (event, item) => {
          item.fx = event.x;
          item.fy = event.y;
        })
        .on("end", (event, item) => {
          if (!event.active) state.graphSimulation.alphaTarget(0);
          item.fx = event.sourceEvent?.altKey ? item.x : null;
          item.fy = event.sourceEvent?.altKey ? item.y : null;
        }),
    );

  nodeGroup.append("circle").attr("class", "graph-node-hit");
  addNodeShape(nodeGroup);
  nodeGroup.append("rect").attr("class", "graph-label-bg");
  const label = nodeGroup
    .append("text")
    .attr("class", "graph-label")
    .attr("x", 10)
    .attr("y", 4)
    .style("--label-opacity", settings.labelOpacity)
    .text((item) => compactText(nodeLabel(item), 24));
  applyNodeSize(nodeGroup);

  state.graphElements = {
    width,
    height,
    root,
    svg,
    nodes,
    links,
    nodeById,
    adjacency: buildAdjacency(links),
    nodeGroup,
    linkGroup,
    linkLine,
    label,
    labelBg: nodeGroup.select(".graph-label-bg"),
    settings,
    centerNodeId: graph.center_node_id || state.selectedNodeId || null,
  };

  updateGraphPositions();
  refreshGraphClasses();

  state.graphSimulation = d3
    .forceSimulation(nodes)
    .force("link", d3.forceLink(links).id((item) => item.id).distance(settings.linkDistance).strength(0.56))
    .force("charge", d3.forceManyBody().strength(settings.repelForce))
    .force("center", d3.forceCenter(width / 2, height / 2).strength(settings.centerForce))
    .force("x", d3.forceX((item) => width / 2 + ({ A: -0.12, B: 0.12, C: 0.02 }[item.knowledge_layer] || 0) * width).strength(0.035))
    .force("y", d3.forceY((item) => height / 2 + ({ A: -0.06, B: -0.08, C: 0.08 }[item.knowledge_layer] || 0) * height).strength(0.035))
    .force("collision", d3.forceCollide().radius((item) => (item.visualRadius || settings.nodeSize) + 10))
    .on("tick", updateGraphPositions);

  state.graphSimulation.stop();
  state.graphSimulation.tick(150);
  updateGraphPositions();
  window.requestAnimationFrame(() => {
    fitGraph({ duration: 0, keepFocus: true });
    if (!state.selectedNodeId && !state.selectedLinkId) renderEntityNote(null);
  });
}

function fitGraph(options = {}) {
  if (!window.d3 || !state.graphZoom || !state.graphElements) return;
  const { duration = 360, keepFocus = false } = options;
  const { nodes, width, height, svg } = state.graphElements;
  if (!nodes.length) return;
  const xs = nodes.map((node) => node.x).filter(Number.isFinite);
  const ys = nodes.map((node) => node.y).filter(Number.isFinite);
  if (!xs.length || !ys.length) return;
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const graphWidth = Math.max(60, maxX - minX);
  const graphHeight = Math.max(60, maxY - minY);
  const targetOccupancy = 0.9;
  const legendReserve = width > 560 ? 28 : 0;
  const fitHeight = Math.max(240, height - legendReserve);
  const scale = Math.max(0.42, Math.min(2.1, Math.min((width * targetOccupancy) / graphWidth, (fitHeight * targetOccupancy) / graphHeight)));
  const tx = width / 2 - scale * (minX + graphWidth / 2);
  const ty = fitHeight / 2 - scale * (minY + graphHeight / 2);
  const transform = d3.zoomIdentity.translate(tx, ty).scale(scale);
  const selection = duration ? svg.transition().duration(duration).ease(d3.easeCubicOut) : svg;
  selection.call(state.graphZoom.transform, transform);
  if (!keepFocus) clearGraphFocus();
}

function centerOnNode(nodeId) {
  if (!window.d3 || !state.graphZoom || !state.graphElements) return;
  const { nodeById, width, height, svg } = state.graphElements;
  const node = nodeById.get(nodeId);
  if (!node) return;
  const current = state.graphTransform || d3.zoomIdentity;
  const scale = Math.max(0.86, Math.min(2.2, current.k || 1));
  const transform = d3.zoomIdentity.translate(width / 2 - node.x * scale, height / 2 - node.y * scale).scale(scale);
  svg.interrupt();
  svg.transition().duration(420).ease(d3.easeCubicOut).call(state.graphZoom.transform, transform);
}

function resetGraphView() {
  clearGraphFocus();
  fitGraph({ duration: 360, keepFocus: true });
}

function resetGraphSettings() {
  $("graphLimit").value = graphDefaults.limit;
  $("graphDepth").value = graphDefaults.depth;
  $("graphDepthValue").textContent = String(graphDefaults.depth);
  $("nodeSize").value = graphDefaults.nodeSize;
  $("linkWidth").value = graphDefaults.linkWidth;
  $("labelDensity").value = graphDefaults.labelDensity;
  $("labelOpacity").value = graphDefaults.labelOpacity * 100;
  $("centerForce").value = graphDefaults.centerForce * 10;
  $("repelForce").value = Math.abs(graphDefaults.repelForce);
  $("linkDistance").value = graphDefaults.linkDistance;
  $("showArrows").checked = false;
  $("showEvidenceNodes").checked = false;
  if (state.lastGraph) renderGraph(state.lastGraph);
}

async function loadImages(event = null) {
  if (event) event.preventDefault();
  const params = new URLSearchParams();
  const fields = [
    ["disease_id", "diseaseId"],
    ["grade_id", "gradeId"],
    ["dataset_id", "datasetId"],
    ["split_id", "splitId"],
  ];
  fields.forEach(([param, id]) => {
    const value = $(id).value.trim();
    if (value) params.set(param, value);
  });
  params.set("limit", $("imageLimit").value || "20");

  setStatus("imageStatus", "正在检索影像...", "ok");
  try {
    const payload = await requestJson(`/images/search?${params.toString()}`);
    $("imageOutput").innerHTML = (payload.items || []).map(renderImageCard).join("") || "<p>未检索到影像。</p>";
    setStatus("imageStatus", `检索到 ${payload.count || 0} 条影像记录。`, "ok");
    renderRaw(payload);
  } catch (error) {
    setStatus("imageStatus", `影像检索失败：${error.message}`, "warn");
  }
}

async function loadStats() {
  try {
    const payload = await requestJson("/stats");
    const layer = payload.layered_statistics?.layer_breakdown || {};
    const rows = [
      ["节点总数", payload.node_count],
      ["边总数", payload.edge_count],
      ["影像节点", payload.image_node_count],
      ["影像元数据", payload.image_metadata_count],
      ["唯一三元组", payload.unique_semantic_triples_count],
      ["证据关系", payload.evidence_backed_relation_claim_count],
      ["A 层节点", layer.A?.node_count || 0],
      ["B 层节点", layer.B?.node_count || 0],
      ["C 层节点", layer.C?.node_count || 0],
      ["质量门", payload.quality_gate?.passed === true ? "passed" : "blocked"],
    ];
    $("statsOutput").innerHTML = rows
      .map(([labelText, value]) => `<article class="stat-card"><h3>${escapeHtml(labelText)}</h3><div class="stat-value">${escapeHtml(value)}</div></article>`)
      .join("");
    renderRaw(payload);
  } catch (error) {
    $("statsOutput").innerHTML = `<article class="stat-card"><h3>加载失败</h3><p>${escapeHtml(error.message)}</p></article>`;
  }
}

function buildDemoCases() {
  const wrap = $("demoCases");
  wrap.innerHTML = "";
  demoCases.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "demo-case";
    button.innerHTML = `<strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.note)}</span><span>${escapeHtml(item.question)}</span>`;
    button.addEventListener("click", async () => {
      activateSection("demo");
      $("demoOutput").innerHTML = "";
      const payload = await runQa(item.question, "demoOutput");
      if (payload) renderQa(payload, "demoOutput");
    });
    wrap.appendChild(button);
  });
}

function bindEvents() {
  document.querySelectorAll(".nav-item, .tab").forEach((button) => {
    button.addEventListener("click", () => activateSection(button.dataset.section));
  });
  document.querySelectorAll(".quick-question, .qa-example").forEach((button) => {
    button.addEventListener("click", () => {
      activateSection("qa");
      $("qaQuestion").value = button.dataset.question;
      runQa(button.dataset.question);
    });
  });
  $("qaForm").addEventListener("submit", (event) => {
    event.preventDefault();
    runQa($("qaQuestion").value);
  });
  $("qaGraphBtn").addEventListener("click", () => {
    activateSection("graph");
    const nodeId = state.lastQa?.entity?.node_id;
    if (nodeId) loadLocalGraph(nodeId);
  });
  $("entitySearchBtn").addEventListener("click", () => searchEntities($("entitySearchInput").value));
  $("entitySearchInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") searchEntities($("entitySearchInput").value);
  });
  $("graphDepth").addEventListener("input", () => {
    $("graphDepthValue").textContent = $("graphDepth").value;
  });
  $("graphSearchInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadLocalGraph();
  });
  $("loadOverviewBtn").addEventListener("click", loadOverviewGraph);
  $("loadLocalGraphBtn").addEventListener("click", () => loadLocalGraph());
  $("fitGraphBtn").addEventListener("click", () => fitGraph({ keepFocus: true }));
  $("resetGraphBtn").addEventListener("click", resetGraphView);
  $("resetGraphSettingsBtn").addEventListener("click", resetGraphSettings);
  $("toggleInspectorBtn").addEventListener("click", () => {
    document.body.classList.toggle("inspector-collapsed");
    window.requestAnimationFrame(() => {
      if (state.lastGraph) renderGraph(state.lastGraph);
    });
  });
  $("imageForm").addEventListener("submit", loadImages);
  $("loadDefaultImagesBtn").addEventListener("click", () => {
    $("diseaseId").value = state.lastQa?.entity?.node_id || "";
    loadImages();
  });
  $("refreshStats").addEventListener("click", loadStats);

  [
    "showArrows",
    "showEvidenceNodes",
    "nodeSize",
    "linkWidth",
    "labelDensity",
    "labelOpacity",
    "centerForce",
    "repelForce",
    "linkDistance",
  ].forEach((id) => {
    $(id).addEventListener("input", () => {
      if (state.lastGraph) renderGraph(state.lastGraph);
    });
  });
  $("includeImages").addEventListener("change", () => {
    if (state.activeSection === "graph") loadOverviewGraph();
  });
  document.querySelectorAll(".layer-filter").forEach((box) => {
    box.addEventListener("change", () => {
      if (state.activeSection === "graph") loadOverviewGraph();
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && state.activeSection === "graph") {
      clearGraphFocus();
    }
  });
}

function bootstrapActiveTab() {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("tab");
  const allowed = new Set(["qa", "graph", "images", "stats", "demo"]);
  activateSection(allowed.has(requested) ? requested : "qa");
}

document.addEventListener("DOMContentLoaded", () => {
  $("safetyNotice").textContent = SAFETY_NOTICE;
  bindEvents();
  buildDemoCases();
  bootstrapActiveTab();
  refreshHealth();
  loadOverviewGraph();
  setInterval(refreshHealth, 30000);
});
