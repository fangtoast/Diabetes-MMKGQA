<!--
Purpose: Track frontend third-party vendor files.
Author: fangtoast
Email: fangtoast@foxmail.com
Copyright (c) 2026 fangtoast. All rights reserved.
-->

# Frontend Vendor Notes

This project vendors a small browser dependency so the course demo can run without CDN access during presentations.

| File | Version | Purpose | Source |
|---|---:|---|---|
| `frontend/vendor/d3.v7.min.js` | 7.9.0 | Force-directed graph rendering, zoom, pan, drag interactions | `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js` |

The vendored file header records the D3 project URL and copyright notice. Do not replace it with a CDN-only `<script>` tag; the UI should remain locally runnable.
