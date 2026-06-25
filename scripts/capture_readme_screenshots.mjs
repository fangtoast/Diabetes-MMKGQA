#!/usr/bin/env node

import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";
const DEFAULT_OUT_DIR = "docs/assets/readme";
const DEFAULT_REMOTE_PORT = 9344;

function parseArgs(argv) {
  const args = {
    baseUrl: DEFAULT_BASE_URL,
    outDir: DEFAULT_OUT_DIR,
    remotePort: DEFAULT_REMOTE_PORT,
    chromePath: "",
  };
  for (let i = 0; i < argv.length; i += 1) {
    const item = argv[i];
    const value = argv[i + 1];
    if (item === "--base-url" && value) {
      args.baseUrl = value.replace(/\/$/, "");
      i += 1;
    } else if (item === "--out-dir" && value) {
      args.outDir = value;
      i += 1;
    } else if (item === "--remote-port" && value) {
      args.remotePort = Number(value);
      i += 1;
    } else if (item === "--chrome-path" && value) {
      args.chromePath = value;
      i += 1;
    } else if (item === "--help" || item === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown or incomplete argument: ${item}`);
    }
  }
  return args;
}

function printHelp() {
  console.log(`Capture README screenshots from a running Diabetes MMKGQA web server.

Usage:
  node scripts/capture_readme_screenshots.mjs --base-url http://127.0.0.1:8000

Options:
  --base-url      Running API/UI base URL. Default: ${DEFAULT_BASE_URL}
  --out-dir       Output directory. Default: ${DEFAULT_OUT_DIR}
  --remote-port   Chrome DevTools port. Default: ${DEFAULT_REMOTE_PORT}
  --chrome-path   Optional explicit chrome.exe/msedge.exe path
`);
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function fetchJson(url, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
      lastError = new Error(`HTTP ${response.status} for ${url}`);
    } catch (error) {
      lastError = error;
    }
    await sleep(250);
  }
  throw lastError || new Error(`Timed out fetching ${url}`);
}

function findChrome(explicitPath) {
  const candidates = [
    explicitPath,
    process.env.CHROME_PATH,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    path.join(os.homedir(), "AppData/Local/Google/Chrome/Application/chrome.exe"),
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  ].filter(Boolean);
  const found = candidates.find((candidate) => fs.existsSync(candidate));
  if (!found) {
    throw new Error("Chrome or Edge was not found. Pass --chrome-path to specify a browser.");
  }
  return found;
}

class Cdp {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) {
          reject(new Error(`${message.error.message}: ${message.error.data || ""}`));
        } else {
          resolve(message.result || {});
        }
        return;
      }
      if (message.method) {
        const handlers = this.events.get(message.method) || [];
        handlers.forEach((handler) => handler(message.params || {}));
      }
    };
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error("CDP websocket open timeout"));
      }, 10000);
      this.ws.onopen = () => {
        clearTimeout(timeout);
        resolve();
      };
      this.ws.onerror = (error) => {
        clearTimeout(timeout);
        reject(error);
      };
    });
  }

  on(method, handler) {
    if (!this.events.has(method)) this.events.set(method, []);
    this.events.get(method).push(handler);
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP command timeout: ${method}`));
        }
      }, 30000);
    });
  }

  close() {
    this.ws.close();
  }
}

async function waitFor(cdp, expression, timeoutMs = 20000, label = expression) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const result = await cdp.send("Runtime.evaluate", {
      expression: `Boolean(${expression})`,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.result?.value) return;
    await sleep(300);
  }
  throw new Error(`Timed out waiting for ${label}`);
}

async function evalJs(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (result.exceptionDetails) {
    throw new Error(`Runtime exception: ${result.exceptionDetails.text}`);
  }
  return result.result?.value;
}

async function setViewport(cdp, width, height, mobile = false) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile,
    screenWidth: width,
    screenHeight: height,
  });
  await cdp.send("Emulation.setVisibleSize", { width, height }).catch(() => {});
}

async function navigate(cdp, url, width = 1440, height = 960, mobile = false) {
  await setViewport(cdp, width, height, mobile);
  await cdp.send("Page.navigate", { url });
  await waitFor(cdp, 'document.readyState === "complete"', 15000, "document ready");
  await sleep(800);
}

async function screenshot(cdp, outDir, filename, screenshots) {
  await sleep(450);
  const result = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  const outputPath = path.join(outDir, filename);
  fs.writeFileSync(outputPath, Buffer.from(result.data, "base64"));
  const stat = fs.statSync(outputPath);
  screenshots.push({ filename, bytes: stat.size });
}

async function captureReadmeScreenshots(options) {
  const baseUrl = options.baseUrl.replace(/\/$/, "");
  const outDir = path.resolve(options.outDir);
  const chromePath = findChrome(options.chromePath);
  const userDataDir = path.join(os.tmpdir(), `mmkgqa-readme-cdp-${Date.now()}`);
  const screenshots = [];
  const pageErrors = [];
  const consoleMessages = [];
  const checks = {};

  fs.mkdirSync(outDir, { recursive: true });

  const chrome = spawn(chromePath, [
    "--headless=new",
    `--remote-debugging-port=${options.remotePort}`,
    `--user-data-dir=${userDataDir}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1440,960",
    "about:blank",
  ], {
    stdio: ["ignore", "ignore", "pipe"],
  });

  let cdp;
  try {
    await fetchJson(`http://127.0.0.1:${options.remotePort}/json/version`, 15000);
    const targets = await fetchJson(`http://127.0.0.1:${options.remotePort}/json/list`, 15000);
    const target = targets.find((item) => item.type === "page" && item.webSocketDebuggerUrl);
    if (!target) throw new Error("No page target found.");

    cdp = new Cdp(target.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Log.enable");
    cdp.on("Runtime.consoleAPICalled", (params) => {
      consoleMessages.push({
        type: params.type,
        text: (params.args || []).map((arg) => arg.value || arg.description || "").join(" "),
      });
    });
    cdp.on("Runtime.exceptionThrown", (params) => {
      pageErrors.push(params.exceptionDetails?.text || params.exceptionDetails?.exception?.description || "unknown exception");
    });
    cdp.on("Log.entryAdded", (params) => {
      if (params.entry?.level === "error") pageErrors.push(params.entry.text || "log error");
    });

    await navigate(cdp, `${baseUrl}/ui`, 1440, 960);
    await waitFor(cdp, 'document.querySelector("#qaQuestion")', 12000, "QA form");
    await evalJs(cdp, `
      document.querySelector("#qaQuestion").value = "show retina images of diabetic retinopathy";
      document.querySelector("#qaForm").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    `);
    await waitFor(
      cdp,
      'document.querySelectorAll("#qaOutput .answer-card").length >= 1 && document.querySelectorAll("#qaOutput .image-card").length >= 1',
      30000,
      "QA answer with images",
    );
    await sleep(1800);
    checks.qa = await evalJs(cdp, 'JSON.stringify({ cards: document.querySelectorAll("#qaOutput .answer-card").length, images: document.querySelectorAll("#qaOutput .image-card").length })');
    await screenshot(cdp, outDir, "readme-qa.png", screenshots);

    await navigate(cdp, `${baseUrl}/ui?tab=graph`, 1440, 960);
    await waitFor(cdp, 'document.querySelectorAll(".graph-node-group").length > 10', 30000, "overview graph nodes");
    await sleep(1600);
    checks.graphOverview = await evalJs(cdp, 'JSON.stringify({ nodes: document.querySelectorAll(".graph-node-group").length, links: document.querySelectorAll(".graph-link-group").length })');
    await screenshot(cdp, outDir, "readme-graph-overview.png", screenshots);

    await evalJs(cdp, `
      const node = Array.from(document.querySelectorAll(".graph-node-group"))
        .find((el) => /type-disease/.test(el.getAttribute("class") || "")) || document.querySelector(".graph-node-group");
      node.dispatchEvent(new MouseEvent("click", { bubbles: true, clientX: 500, clientY: 420 }));
    `);
    await waitFor(cdp, 'document.querySelector(".graph-node-group.is-selected")', 12000, "selected graph node");
    await sleep(900);
    checks.graphFocus = await evalJs(cdp, 'JSON.stringify({ selectedNodes: document.querySelectorAll(".graph-node-group.is-selected").length })');
    await screenshot(cdp, outDir, "readme-graph-focus.png", screenshots);

    await evalJs(cdp, `
      const edge = Array.from(document.querySelectorAll(".graph-link-group"))
        .find((el) => (el.textContent || "").includes("HAS_ICD_CODE")) || document.querySelector(".graph-link-group");
      edge.dispatchEvent(new MouseEvent("click", { bubbles: true, clientX: 620, clientY: 420 }));
    `);
    await waitFor(cdp, 'document.querySelector(".graph-link-group.is-selected")', 12000, "selected graph edge");
    await sleep(900);
    checks.graphPath = await evalJs(cdp, 'JSON.stringify({ selectedLinks: document.querySelectorAll(".graph-link-group.is-selected").length })');
    await screenshot(cdp, outDir, "readme-graph-path.png", screenshots);

    await navigate(cdp, `${baseUrl}/ui?tab=images`, 1440, 960);
    await waitFor(cdp, 'document.querySelector("#imageOutput")', 12000, "image panel");
    await evalJs(cdp, 'document.querySelector("#loadDefaultImagesBtn").click();');
    await waitFor(cdp, 'document.querySelectorAll("#imageOutput .image-card").length >= 4', 30000, "image cards");
    await sleep(1800);
    checks.images = await evalJs(cdp, 'JSON.stringify({ cards: document.querySelectorAll("#imageOutput .image-card").length, previews: document.querySelectorAll("#imageOutput img.image-preview").length })');
    await screenshot(cdp, outDir, "readme-images.png", screenshots);

    await navigate(cdp, `${baseUrl}/ui?tab=stats`, 1440, 960);
    await waitFor(cdp, 'document.querySelectorAll(".stat-card").length >= 8', 20000, "stats cards");
    await sleep(700);
    checks.stats = await evalJs(cdp, 'JSON.stringify({ cards: document.querySelectorAll(".stat-card").length })');
    await screenshot(cdp, outDir, "readme-stats.png", screenshots);

    await navigate(cdp, `${baseUrl}/ui?tab=graph`, 390, 860, true);
    await waitFor(cdp, 'document.querySelectorAll(".graph-node-group").length > 10', 30000, "mobile graph nodes");
    await evalJs(cdp, 'document.querySelector(".graph-stage").scrollIntoView({ block: "center" });');
    await sleep(1400);
    checks.mobileGraph = await evalJs(cdp, 'JSON.stringify({ nodes: document.querySelectorAll(".graph-node-group").length, links: document.querySelectorAll(".graph-link-group").length })');
    await screenshot(cdp, outDir, "readme-mobile-graph.png", screenshots);

    const severeErrors = pageErrors.filter((text) => !/favicon|Failed to load resource/i.test(text));
    const output = {
      baseUrl,
      outDir,
      screenshots,
      checks: Object.fromEntries(Object.entries(checks).map(([key, value]) => [key, JSON.parse(value || "{}")])),
      pageErrors: severeErrors,
      consoleMessages: consoleMessages.slice(-10),
    };
    console.log(JSON.stringify(output, null, 2));

    if (screenshots.length !== 7) throw new Error(`Expected 7 screenshots, got ${screenshots.length}.`);
    if (screenshots.some((item) => item.bytes < 12000)) {
      throw new Error("One or more screenshots are unexpectedly small.");
    }
    if (severeErrors.length) {
      throw new Error(`Page errors observed: ${severeErrors.join(" | ")}`);
    }
  } finally {
    if (cdp) cdp.close();
    chrome.kill();
    await sleep(300);
    fs.rmSync(userDataDir, { recursive: true, force: true });
  }
}

captureReadmeScreenshots(parseArgs(process.argv.slice(2))).catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
