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
    assert "grid-template-rows: auto auto auto minmax(0, 1fr)" in css
    assert ".image-results" in css
    assert "overflow: auto" in css
