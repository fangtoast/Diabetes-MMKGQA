<!--
purpose: Screenshot evidence index for the usability test report.
-->

# Screenshot Evidence

Screenshots were captured from the running local UI at `http://127.0.0.1:8017/ui` during the 2026-06-28 test. The service was stopped after capture.

## Captured Files

| File | What it proves |
|---|---|
| `ui_home.png` | The QA platform loads and shows the main workspace. |
| `qa_success.png` | A successful QA case renders answer, evidence IDs, source IDs, KG version, and safety notice. |
| `graph_overview.png` | Graph Explorer renders a non-empty graph with nodes and edges. |
| `image_retrieval.png` | Image Retrieval displays multimodal image cards and local PNG previews. |
| `stats_page.png` | Layered Statistics displays graph counts and quality gate status. |
| `browser_check.json` | Browser automation check: page title, final URL, captured runtime errors, and safety notice presence. |

## Recommended Optional Screenshot

If a course submission explicitly requires a terminal screenshot, capture the PowerShell window after running:

```powershell
.\scripts\start.ps1 -SkipData -SkipKg -SkipLoad -NoBrowser
```

Save it here as:

```text
docs/test-report/screenshots/terminal_startup.png
```

The command output is already summarized in `docs/test-report/final_test_report.md`, so this optional screenshot is only for visual evidence requirements.
