// Real browser -> FastAPI -> hosted model verification. No intercepted API responses.
import { chromium } from "playwright";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
const base = process.env.UI_BASE,
  output = process.env.LIVE_UI_ARTIFACTS;
assert.ok(base && output, "Set UI_BASE and LIVE_UI_ARTIFACTS explicitly.");
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch(),
  context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    permissions: ["clipboard-read", "clipboard-write"],
  }),
  page = await context.newPage(),
  results = [],
  errors = [],
  sources = [];
page.on("pageerror", (e) => errors.push(e.message));
async function check(name, fn) {
  await fn();
  results.push(name);
  console.log("PASS", name);
}
async function submit() {
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/api/analyze") && r.request().method() === "POST",
    { timeout: 75000 },
  );
  await page
    .getByRole("button", { name: "Explain my report", exact: true })
    .click();
  const r = await response,
    data = await r.json();
  assert.equal(r.status(), 200);
  assert.equal(data.source, "hosted_model");
  assert.equal(data.parse_warning, false);
  sources.push(data.source);
  await page.getByText(data.summary, { exact: true }).waitFor();
  assert.equal(await page.locator(".result-warning").count(), 0);
  return data;
}
try {
  await page.goto(base);
  await check(
    "Actual blood-test sample reaches hosted model and displays its numeric evidence",
    async () => {
      await page
        .getByRole("button", { name: "Blood test", exact: false })
        .click();
      const r = await submit();
      assert.match(JSON.stringify(r), /13\.8/);
      assert.match(
        await page.locator(".result-disclaimer").innerText(),
        /not medical advice/,
      );
      await page
        .locator(".workspace-section")
        .screenshot({ path: path.join(output, "live-model-result.png") });
    },
  );
  await check(
    "Original-report comparison and real-result exports retain mandatory disclaimer",
    async () => {
      await page
        .getByRole("tab", { name: "Original report", exact: true })
        .click();
      assert.match(
        await page.locator(".original-text").innerText(),
        /SYNTHETIC EXAMPLE/,
      );
      await page.getByRole("tab", { name: "Explanation", exact: true }).click();
      await page
        .getByRole("button", { name: "Copy explanation", exact: true })
        .click();
      assert.match(
        await page.evaluate(() => navigator.clipboard.readText()),
        /not medical advice/,
      );
      const pending = page.waitForEvent("download");
      await page
        .getByRole("button", { name: "Download explanation", exact: true })
        .click();
      const downloaded = await pending;
      const file = path.join(output, "synthetic-live-export.txt");
      await downloaded.saveAs(file);
      assert.match(fs.readFileSync(file, "utf8"), /licensed clinician/);
    },
  );
  await check(
    "A changed radiology sample produces a separate live result preserving negation",
    async () => {
      await page
        .getByRole("button", { name: "Chest X-ray", exact: false })
        .click();
      assert.equal(await page.locator(".result-content").count(), 0);
      const r = await submit();
      assert.match(JSON.stringify(r), /no |not |without|normal|absence/i);
    },
  );
  await check(
    "Mobile submission and result rendering work with the actual hosted model",
    async () => {
      await page.setViewportSize({ width: 390, height: 844 });
      await page
        .getByRole("button", { name: "Discharge note", exact: false })
        .click();
      await submit();
      await page.waitForTimeout(350);
      assert.ok(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      );
      await page.locator("#result-heading").waitFor();
      await page
        .locator(".results-panel")
        .screenshot({ path: path.join(output, "live-model-mobile.png") });
    },
  );
  assert.deepEqual(errors, []);
} catch (e) {
  errors.push(e.message);
  console.log("FAIL", e.message);
  await page
    .screenshot({ path: path.join(output, "failure.png"), fullPage: true })
    .catch(() => {});
  process.exitCode = 1;
} finally {
  await browser.close();
  fs.writeFileSync(
    path.join(output, "browser-report.json"),
    JSON.stringify(
      {
        verifiedAt: new Date().toISOString(),
        base,
        passed: !process.exitCode,
        results,
        errors,
        sources,
        scope:
          "Actual browser, FastAPI and hosted Gemini inference over fictional reports. No API mocking or keyword fallback accepted. Does not verify ERNIE weights, completed training, clinical accuracy or a public deployment.",
      },
      null,
      2,
    ) + "\n",
  );
}
