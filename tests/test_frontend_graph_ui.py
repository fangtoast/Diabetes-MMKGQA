from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_graph_explorer_has_refined_controls_and_tokens() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert 'id="graphAdvanced"' in html
    assert 'id="resetGraphBtn"' in html
    assert 'id="showEvidenceNodes"' in html
    assert 'class="graph-legend"' in html
    assert 'aria-label="折叠或展开右侧详情"' in html
    assert "--canvas-bg: #121315" in css
    assert "--graph-link-selected" in css
    assert ".graph-node-group.is-second-neighbor" in css
    assert ".graph-edge-label" in css


def test_graph_explorer_focus_and_detail_functions_are_present() -> None:
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "function focusGraphNode" in js
    assert "function focusGraphLink" in js
    assert "function renderRelationDetail" in js
    assert "function visibleLabelIds" in js
    assert "event.key === \"Escape\"" in js
    assert "node.node_type !== \"EvidenceChunk\"" in js
    assert "focusGraphNode(item.id, { center: false })" in js
    assert "focusGraphNode(center, { center: true })" in js


def test_qa_workspace_exposes_answerable_examples() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert 'class="qa-guide"' in html
    assert 'data-question="糖尿病有哪些症状"' in html
    assert 'data-question="糖尿病需要做哪些检查"' in html
    assert 'data-question="高血压的ICD编码是什么"' in html
    assert 'data-question="糖尿病视网膜病变有哪些影像示例"' in html
    assert ".qa-example-grid" in css
    assert '".quick-question, .qa-example"' in js


def test_image_retrieval_panel_has_scrollable_results_region() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")

    assert 'id="imageResults"' in html
    assert 'class="image-results"' in html
    assert "#imagesPanel.panel-view.is-active" in css
    assert "grid-template-rows: auto auto auto auto minmax(0, 1fr)" in css
    assert ".image-results" in css
    assert "overflow: auto" in css


def test_image_retrieval_exposes_preset_filters_and_metadata() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert 'class="image-presets"' in html
    assert 'data-source-id="retinamnist"' in html
    assert 'data-source-id="pneumoniamnist"' in html
    assert "function loadImagePreset" in js
    assert "source_id" in js
    assert 'row.evidence_id || "no evidence"' in js
    assert 'row.kg_version || "kg -"' in js
    assert ".image-preset" in css


def test_image_retrieval_has_searchable_selectors_and_advanced_ids() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert 'class="image-selector-grid"' in html
    assert 'id="diseaseSearch"' in html
    assert 'id="datasetSearch"' in html
    assert 'id="gradeSearch"' in html
    assert 'id="splitSearch"' in html
    assert 'id="imageActiveFilters"' in html
    assert 'id="imageAdvanced"' in html
    assert 'id="diseaseId"' in html
    assert "node_types" in js
    assert "function searchImageSelector" in js
    assert "function selectImageFilter" in js
    assert "function renderImageActiveFilters" in js
    assert "searchImageSelector(button.dataset.filter)" in js
    assert ".selector-result" in css
    assert ".filter-chip" in css
    assert ".image-advanced" in css


def test_stats_cards_are_clickable_and_have_detail_panel() -> None:
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert 'id="statsDetails"' in html
    assert 'data-kind="${escapeHtml(item.kind)}"' in js
    assert "function loadStatsDetail" in js
    assert "/stats/details?kind=" in js
    assert ".stat-action" in css
    assert ".stats-details" in css
    assert ".detail-item" in css


def test_node_and_qa_entity_details_show_provenance_fields() -> None:
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    assert "<span>source_ids</span>" in js
    assert "<span>evidence_id</span>" in js
    assert "<span>kg_version</span>" in js
    assert 'entity.source_ids || "no source"' in js
    assert 'entity.evidence_id || "no evidence"' in js
