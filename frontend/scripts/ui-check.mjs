import { chromium } from "playwright";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
const base = process.env.UI_BASE || "http://127.0.0.1:5181",
  artifacts = path.resolve(
    process.env.UI_ARTIFACTS || "../docs/frontend-redesign/verification",
  );
fs.mkdirSync(artifacts, { recursive: true });
const b = await chromium.launch(),
  c = await b.newContext({
    viewport: { width: 1440, height: 1000 },
    permissions: ["clipboard-read", "clipboard-write"],
  }),
  p = await c.newPage(),
  results = [],
  errors = [];
p.on("pageerror", (e) => errors.push(e.message));
const fixture = {
  summary: "Synthetic browser fixture: the explanation is ready.",
  key_findings: ["Synthetic finding one.", "Synthetic finding two."],
  recommendations: ["Discuss the original report with a clinician."],
  disclaimer: "Educational fixture only. Not medical advice.",
  source: "hf_inference",
  parse_warning: false,
};
async function check(name, fn) {
  await fn();
  results.push(name);
  console.log("PASS", name);
}
async function fresh() {
  await p.unroute("**/api/analyze");
  await p.goto(base);
  await p.locator("#report-text").waitFor();
}
async function mock(data = fixture, status = 200) {
  await p.route("**/api/analyze", (r) =>
    r.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify(data),
    }),
  );
}
async function analyze() {
  await p
    .getByRole("button", { name: "Explain my report", exact: true })
    .click();
}
async function sample(name = "Chest X-ray") {
  await p.getByRole("button", { name, exact: false }).click();
}
try {
  await check(
    "Navigation, title, favicon and all six report types",
    async () => {
      await fresh();
      assert.match(await p.title(), /Medical words/);
      assert.equal(await p.locator("#report-type option").count(), 6);
      assert.equal(
        (await c.request.get(base + "/medexplain-mark.svg")).status(),
        200,
      );
      await p.getByRole("link", { name: "How it works", exact: true }).click();
      assert.equal(new URL(p.url()).hash, "#how-it-works");
      await p
        .getByRole("link", { name: "Open workspace", exact: false })
        .click();
      assert.equal(new URL(p.url()).hash, "#workspace");
      await p
        .getByRole("link", { name: "MedExplain AI home", exact: true })
        .first()
        .click();
      assert.equal(new URL(p.url()).hash, "#top");
    },
  );
  await check("Blank report validation keeps focus on the editor", async () => {
    await fresh();
    await analyze();
    await p.getByRole("alert").waitFor();
    assert.equal(
      await p.locator("#report-text").getAttribute("aria-invalid"),
      "true",
    );
    assert.ok(
      await p
        .locator("#report-text")
        .evaluate((e) => e === document.activeElement),
    );
  });
  await check(
    "Three fictional samples update report type, text and selection",
    async () => {
      for (const [name, type] of [
        ["Chest X-ray", "radiology"],
        ["Blood test", "lab"],
        ["Discharge note", "discharge"],
      ]) {
        await sample(name);
        assert.equal(await p.locator("#report-type").inputValue(), type);
        assert.match(
          await p.locator("#report-text").inputValue(),
          /SYNTHETIC EXAMPLE/,
        );
        assert.equal(
          await p
            .getByRole("button", { name, exact: false })
            .getAttribute("aria-pressed"),
          "true",
        );
      }
      await p.getByRole("button", { name: "Clear", exact: true }).click();
      assert.equal(await p.locator("#report-text").inputValue(), "");
    },
  );
  await check(
    "Successful response, loading feedback and exact request payload",
    async () => {
      await fresh();
      await sample();
      await p.route("**/api/analyze", async (r) => {
        const body = r.request().postDataJSON();
        assert.equal(body.report_type, "radiology");
        assert.match(body.report_text, /SYNTHETIC EXAMPLE/);
        await new Promise((resolve) => setTimeout(resolve, 250));
        await r.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(fixture),
        });
      });
      await analyze();
      await p
        .getByText("Finding the everyday words.", { exact: true })
        .waitFor();
      assert.equal(await p.locator("#report-text").isDisabled(), true);
      await p.getByText(fixture.summary, { exact: true }).waitFor();
      assert.equal(await p.locator(".result-warning").count(), 0);
      assert.ok(
        await p
          .locator("#result-heading")
          .evaluate((e) => e === document.activeElement),
      );
      await p.screenshot({
        path: path.join(artifacts, "result-desktop.png"),
        fullPage: true,
      });
    },
  );
  await check("Original report tabs support keyboard navigation", async () => {
    const tab = p.getByRole("tab", { name: "Explanation", exact: true });
    await tab.focus();
    await p.keyboard.press("ArrowRight");
    assert.equal(
      await p
        .getByRole("tab", { name: "Original report", exact: true })
        .getAttribute("aria-selected"),
      "true",
    );
    assert.match(
      await p.locator(".original-text").innerText(),
      /SYNTHETIC EXAMPLE/,
    );
    await p.keyboard.press("Home");
    assert.equal(await tab.getAttribute("aria-selected"), "true");
  });
  await check("Copy and download preserve the disclaimer", async () => {
    await p
      .getByRole("button", { name: "Copy explanation", exact: true })
      .click();
    await p
      .getByText(
        "Explanation copied, including its limitations and disclaimer.",
        { exact: true },
      )
      .waitFor();
    assert.match(
      await p.evaluate(() => navigator.clipboard.readText()),
      /Educational fixture only/,
    );
    const download = p.waitForEvent("download");
    await p
      .getByRole("button", { name: "Download explanation", exact: true })
      .click();
    const d = await download;
    assert.equal(d.suggestedFilename(), "medexplain-explanation.txt");
    await d.saveAs(path.join(artifacts, "fixture-export.txt"));
    assert.match(
      fs.readFileSync(path.join(artifacts, "fixture-export.txt"), "utf8"),
      /Educational fixture only/,
    );
  });
  await check(
    "Editing report text or type removes stale explanations",
    async () => {
      await p.locator("#report-text").fill("A different synthetic report.");
      assert.equal(await p.locator(".result-content").count(), 0);
      await fresh();
      await sample();
      await mock();
      await analyze();
      await p.getByText(fixture.summary, { exact: true }).waitFor();
      await p.locator("#report-type").selectOption("other");
      assert.equal(await p.locator(".result-content").count(), 0);
    },
  );
  await check(
    "Fallback result has a clear warning retained in exports",
    async () => {
      await fresh();
      await sample();
      await mock({ ...fixture, source: "fallback", parse_warning: false });
      await analyze();
      await p.getByText("Limited keyword fallback", { exact: true }).waitFor();
      assert.match(
        await p.locator(".result-warning").innerText(),
        /not an AI-generated interpretation/,
      );
      await p
        .getByRole("button", { name: "Copy explanation", exact: true })
        .click();
      assert.match(
        await p.evaluate(() => navigator.clipboard.readText()),
        /LIMITED KEYWORD FALLBACK/,
      );
      await p.screenshot({
        path: path.join(artifacts, "fallback-desktop.png"),
        fullPage: true,
      });
    },
  );
  await check(
    "Partial model response is distinguished from a keyword fallback",
    async () => {
      await fresh();
      await sample();
      await mock({ ...fixture, parse_warning: true });
      await analyze();
      await p
        .getByText("This explanation may be incomplete", { exact: true })
        .waitFor();
      assert.equal(
        await p.getByText("Limited keyword fallback", { exact: true }).count(),
        0,
      );
    },
  );
  await check("Empty finding lists do not claim a normal result", async () => {
    await fresh();
    await sample();
    await mock({
      ...fixture,
      key_findings: [],
      recommendations: [],
      disclaimer: "",
    });
    await analyze();
    await p
      .getByText(
        "No findings were returned. This does not confirm a normal result.",
        { exact: true },
      )
      .waitFor();
    assert.match(
      await p.locator(".result-disclaimer").innerText(),
      /not medical advice/,
    );
  });
  await check(
    "HTTP failures preserve input and provide recoverable messages",
    async () => {
      for (const status of [413, 422, 429, 503]) {
        await fresh();
        await sample();
        await mock({}, status);
        await analyze();
        await p.getByRole("alert").waitFor();
        assert.match(
          await p.locator("#report-text").inputValue(),
          /SYNTHETIC EXAMPLE/,
        );
        assert.equal(
          await p
            .getByRole("button", { name: "Explain my report", exact: true })
            .isEnabled(),
          true,
        );
      }
    },
  );
  await check("Malformed JSON and schema responses fail safely", async () => {
    await fresh();
    await sample();
    await p.route("**/api/analyze", (r) =>
      r.fulfill({
        status: 200,
        contentType: "text/html",
        body: "<html>Gateway</html>",
      }),
    );
    await analyze();
    await p.getByRole("alert").waitFor();
    assert.match(await p.getByRole("alert").innerText(), /unreadable response/);
    await fresh();
    await sample();
    await mock({ summary: "missing arrays" });
    await analyze();
    await p.getByRole("alert").waitFor();
    assert.match(await p.getByRole("alert").innerText(), /incomplete response/);
  });
  await check(
    "Network failure offers a retry without losing input",
    async () => {
      await fresh();
      await sample();
      await p.route("**/api/analyze", (r) => r.abort("failed"));
      await analyze();
      await p.getByRole("alert").waitFor();
      assert.match(await p.getByRole("alert").innerText(), /couldn’t reach/);
    },
  );
  await check(
    "Request timeout is recoverable and preserves the report",
    async () => {
      await fresh();
      await sample();
      await p.evaluate(() => {
        const original = window.setTimeout;
        window.setTimeout = function (handler, delay, ...args) {
          if (delay === 90000) {
            window.setTimeout = original;
            return original(handler, 20, ...args);
          }
          return original(handler, delay, ...args);
        };
      });
      await p.route("**/api/analyze", async (r) => {
        await new Promise((resolve) => setTimeout(resolve, 200));
        await r
          .fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(fixture),
          })
          .catch(() => {});
      });
      await analyze();
      await p.getByRole("alert").waitFor();
      assert.match(
        await p.getByRole("alert").innerText(),
        /taking longer than expected/,
      );
      assert.match(
        await p.locator("#report-text").inputValue(),
        /SYNTHETIC EXAMPLE/,
      );
    },
  );
  await check(
    "Cancellation prevents a late response replacing a newer result",
    async () => {
      await fresh();
      await sample();
      let calls = 0;
      await p.route("**/api/analyze", async (r) => {
        const first = ++calls === 1;
        if (first) await new Promise((resolve) => setTimeout(resolve, 900));
        await r
          .fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              ...fixture,
              summary: first ? "Obsolete response" : "Current response",
            }),
          })
          .catch(() => {});
      });
      await analyze();
      await p.getByRole("button", { name: "Cancel", exact: true }).click();
      await p
        .getByText("Analysis canceled. Your report is still here.", {
          exact: true,
        })
        .waitFor();
      await sample("Blood test");
      await analyze();
      await p.getByText("Current response", { exact: true }).waitFor();
      await p.waitForTimeout(1100);
      assert.equal(
        await p.getByText("Obsolete response", { exact: true }).count(),
        0,
      );
    },
  );
  await check(
    "Narrow/wide layouts fit at 11 viewport widths, empty and populated",
    async () => {
      for (const width of [
        320, 360, 390, 600, 768, 800, 820, 1024, 1280, 1440, 1920,
      ]) {
        await p.setViewportSize({ width, height: 900 });
        await fresh();
        assert.ok(
          await p.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          `empty ${width}`,
        );
        await sample();
        await mock({
          ...fixture,
          summary: "A long synthetic explanation. ".repeat(35),
        });
        await analyze();
        await p.getByText("In everyday words", { exact: true }).waitFor();
        assert.ok(
          await p.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          `result ${width}`,
        );
        await p
          .getByRole("tab", { name: "Original report", exact: true })
          .click();
        assert.ok(
          await p.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          `original ${width}`,
        );
      }
      await p.setViewportSize({ width: 390, height: 844 });
      await p.screenshot({
        path: path.join(artifacts, "result-mobile.png"),
        fullPage: true,
      });
    },
  );
  await check("Reduced motion and skip link work", async () => {
    await p.emulateMedia({ reducedMotion: "reduce" });
    await fresh();
    assert.equal(
      await p
        .locator("html")
        .evaluate((e) => getComputedStyle(e).scrollBehavior),
      "auto",
    );
    await p
      .getByRole("link", { name: "Skip to report workspace", exact: true })
      .focus();
    await p.keyboard.press("Enter");
    assert.equal(new URL(p.url()).hash, "#workspace");
  });
  if (process.env.UI_REAL_BACKEND === "true")
    await check(
      "Actual FastAPI fallback integrates honestly without a model credential",
      async () => {
        await fresh();
        await sample("Blood test");
        await analyze();
        await p
          .getByText("Limited keyword fallback", { exact: true })
          .waitFor({ timeout: 20000 });
        assert.match(
          await p.locator(".result-disclaimer").innerText(),
          /not medical advice/,
        );
        await p.screenshot({
          path: path.join(artifacts, "real-api-fallback.png"),
          fullPage: true,
        });
      },
    );
  assert.deepEqual(errors, []);
} catch (e) {
  errors.push(e.message);
  console.log("FAIL", e.message);
  await p
    .screenshot({ path: path.join(artifacts, "failure.png"), fullPage: true })
    .catch(() => {});
  process.exitCode = 1;
} finally {
  await b.close();
  fs.writeFileSync(
    path.join(artifacts, "report.json"),
    JSON.stringify(
      {
        base,
        verifiedAt: new Date().toISOString(),
        results,
        errors,
        passed: !process.exitCode,
        realBackend: process.env.UI_REAL_BACKEND === "true",
        scope:
          "Synthetic browser fixtures cover UI states. Optional real FastAPI request verifies only keyword fallback; no live Hugging Face model inference is claimed.",
      },
      null,
      2,
    ),
  );
  console.log("Artifacts:", artifacts);
}
