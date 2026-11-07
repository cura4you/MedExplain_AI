import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
type Result = {
  summary: string;
  key_findings: string[];
  recommendations: string[];
  disclaimer: string;
  source?: string;
  parse_warning?: boolean;
};
const API = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const TYPES = [
  ["radiology", "Radiology"],
  ["lab", "Lab / blood test"],
  ["pathology", "Pathology"],
  ["clinical", "Clinical notes"],
  ["discharge", "Discharge summary"],
  ["other", "Other report"],
];
const SAMPLES = [
  {
    name: "Chest X-ray",
    type: "radiology",
    text: "SYNTHETIC EXAMPLE — NOT A REAL PATIENT RECORD\n\nChest radiograph: The cardiomediastinal silhouette is within normal limits. No focal pulmonary infiltrate, pleural effusion, or pneumothorax. Impression: No acute cardiopulmonary abnormality.",
  },
  {
    name: "Blood test",
    type: "lab",
    text: "SYNTHETIC EXAMPLE — NOT A REAL PATIENT RECORD\n\nComplete blood count: WBC 12.5 x 10^9/L (reference 4.0–11.0), hemoglobin 13.8 g/dL (reference 12.0–16.0), platelets 250 x 10^9/L (reference 150–400). Mild leukocytosis. Correlate with clinical symptoms and repeat testing as clinically indicated.",
  },
  {
    name: "Discharge note",
    type: "discharge",
    text: "SYNTHETIC EXAMPLE — NOT A REAL PATIENT RECORD\n\nDischarge diagnosis: Dehydration following gastroenteritis. Received intravenous fluids with improvement in oral intake. Discharged in stable condition. Follow up with primary care in one week. Return for persistent vomiting, inability to tolerate fluids, or worsening symptoms.",
  },
];
const DISCLAIMER =
  "This information is for education only and is not medical advice. Consult a licensed clinician for diagnosis or treatment.";
function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const icons: Record<string, ReactNode> = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    document: <path d="M14 3H6v18h12V7zM14 3v5h5M9 12h6m-6 4h6" />,
    spark: (
      <path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5zM20 2v4m-2-2h4" />
    ),
    shield: (
      <>
        <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z" />
        <path d="m8 12 3 3 5-6" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    copy: (
      <>
        <rect x="8" y="8" width="12" height="13" rx="2" />
        <path d="M16 8V3H3v13h5" />
      </>
    ),
    download: <path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5" />,
    info: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 11v6m0-10v1" />
      </>
    ),
    external: (
      <>
        <path d="M14 4h6v6m0-6L10 14" />
        <path d="M20 14v6H4V4h6" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {icons[name]}
    </svg>
  );
}
function Brand() {
  return (
    <span className="brand">
      <span className="brand-symbol" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <span>
        MedExplain<span className="brand-ai"> AI</span>
      </span>
    </span>
  );
}
function isResult(x: unknown): x is Result {
  if (!x || typeof x !== "object") return false;
  const r = x as Result;
  return (
    typeof r.summary === "string" &&
    typeof r.disclaimer === "string" &&
    Array.isArray(r.key_findings) &&
    r.key_findings.every((v) => typeof v === "string") &&
    Array.isArray(r.recommendations) &&
    r.recommendations.every((v) => typeof v === "string") &&
    (r.source === undefined || typeof r.source === "string") &&
    (r.parse_warning === undefined || typeof r.parse_warning === "boolean")
  );
}
export default function App() {
  const [text, setText] = useState(""),
    [type, setType] = useState("radiology"),
    [result, setResult] = useState<Result | null>(null),
    [original, setOriginal] = useState(""),
    [resultType, setResultType] = useState(""),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false),
    [notice, setNotice] = useState(""),
    [sample, setSample] = useState<number | null>(null),
    [tab, setTab] = useState("explanation");
  const request = useRef<AbortController | null>(null),
    editor = useRef<HTMLTextAreaElement>(null),
    heading = useRef<HTMLHeadingElement>(null),
    tabs = useRef<(HTMLButtonElement | null)[]>([]);
  useEffect(() => () => request.current?.abort(), []);
  function reset() {
    setResult(null);
    setError("");
    setNotice("");
    setTab("explanation");
  }
  function useSample(i: number) {
    setText(SAMPLES[i].text);
    setType(SAMPLES[i].type);
    setSample(i);
    reset();
    editor.current?.focus();
  }
  function clear() {
    setText("");
    setSample(null);
    reset();
    editor.current?.focus();
  }
  function cancel() {
    request.current?.abort();
    request.current = null;
    setLoading(false);
    setNotice("Analysis canceled. Your report is still here.");
  }
  async function analyze(e: FormEvent) {
    e.preventDefault();
    if (loading) return;
    if (!text.trim()) {
      setError("Add your report text or choose a sample to get started.");
      editor.current?.focus();
      return;
    }
    reset();
    setLoading(true);
    const controller = new AbortController();
    request.current = controller;
    let timedOut = false;
    const timer = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 90000);
    try {
      const response = await fetch(`${API}/api/analyze`, {
        method: "POST",
        signal: controller.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ report_text: text.trim(), report_type: type }),
      });
      if (!response.ok)
        throw new Error(
          response.status === 429
            ? "There are a few too many requests. Please wait a moment and try again."
            : response.status === 413
              ? "This report is too long to process. Try a shorter excerpt."
              : response.status === 422
                ? "The report could not be accepted. Check the text and report type, then try again."
                : "The explanation service is temporarily unavailable. Your text is still here; please try again.",
        );
      let data: unknown;
      try {
        data = await response.json();
      } catch {
        throw new Error(
          "We received an unreadable response. Please try again.",
        );
      }
      if (!isResult(data))
        throw new Error(
          "We received an incomplete response. Please try again before relying on these results.",
        );
      if (request.current !== controller) return;
      setResult(data);
      setOriginal(text.trim());
      setResultType(type);
      window.setTimeout(() => {
        heading.current?.focus({ preventScroll: true });
        if (window.matchMedia("(max-width: 800px)").matches)
          heading.current?.scrollIntoView({
            behavior: window.matchMedia("(prefers-reduced-motion: reduce)")
              .matches
              ? "auto"
              : "smooth",
            block: "start",
          });
      }, 0);
    } catch (err) {
      if (request.current !== controller) return;
      if (controller.signal.aborted && !timedOut) return;
      setError(
        timedOut
          ? "This is taking longer than expected. Please try again in a moment."
          : err instanceof TypeError
            ? "We couldn’t reach the explanation service. Check your connection and try again."
            : err instanceof Error
              ? err.message
              : "Something went wrong. Please try again.",
      );
    } finally {
      window.clearTimeout(timer);
      if (request.current === controller) {
        request.current = null;
        setLoading(false);
      }
    }
  }
  function exportText() {
    if (!result) return "";
    const warning =
      result.source === "fallback"
        ? "LIMITED KEYWORD FALLBACK — NOT A MODEL-GENERATED EXPLANATION\n\n"
        : result.parse_warning
          ? "INCOMPLETE MODEL RESPONSE — REVIEW BEFORE USE\n\n"
          : "";
    return `MedExplain AI\n${TYPES.find((t) => t[0] === resultType)?.[1]}\n\n${warning}SUMMARY\n${result.summary}\n\nKEY FINDINGS\n${result.key_findings.map((v) => `• ${v}`).join("\n") || "No findings returned."}\n\nNEXT STEPS TO DISCUSS\n${result.recommendations.map((v) => `• ${v}`).join("\n") || "No next steps returned."}\n\n${result.disclaimer || DISCLAIMER}`;
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(exportText());
      setNotice(
        "Explanation copied, including its limitations and disclaimer.",
      );
    } catch {
      setNotice(
        "Copy isn’t available in this browser. You can download the text instead.",
      );
    }
  }
  function download() {
    const url = URL.createObjectURL(
        new Blob([exportText()], { type: "text/plain;charset=utf-8" }),
      ),
      a = document.createElement("a");
    a.href = url;
    a.download = "medexplain-explanation.txt";
    a.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice("Explanation downloaded with its limitations and disclaimer.");
  }
  return (
    <>
      <a className="skip-link" href="#workspace">
        Skip to report workspace
      </a>
      <header className="site-header">
        <div className="header-inner">
          <a href="#top" aria-label="MedExplain AI home">
            <Brand />
          </a>
          <nav aria-label="Main navigation">
            <a href="#how-it-works">How it works</a>
            <a className="header-cta" href="#workspace">
              Open workspace <Icon name="arrow" size={16} />
            </a>
          </nav>
        </div>
      </header>
      <main id="top">
        <section className="hero page-width" aria-labelledby="hero-title">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="status-dot" /> A LITTLE MORE UNDERSTANDING
            </div>
            <h1 id="hero-title">
              Medical words.
              <br />
              <em>Human meaning.</em>
            </h1>
            <p className="hero-description">
              Your report shouldn’t leave you with more questions. Turn complex
              clinical language into a clearer place to start.
            </p>
            <a className="button primary hero-button" href="#workspace">
              Make sense of a report <Icon name="arrow" size={18} />
            </a>
            <p className="hero-footnote">
              Built for understanding. Made for the conversation with your
              clinician.
            </p>
          </div>
          <div
            className="translation-card"
            aria-label="An illustrative example of translating medical terminology"
          >
            <div className="translation-top">
              <span className="tiny-label">A CHANGE IN PERSPECTIVE</span>
              <span className="example-tag">Illustrative example</span>
            </div>
            <div className="clinical-example">
              <span className="tiny-label">THE REPORT SAYS</span>
              <p>“No acute cardiopulmonary abnormality.”</p>
              <div className="report-lines" aria-hidden="true">
                <i />
                <i />
                <i />
              </div>
            </div>
            <div className="translation-divider">
              <span />
              <i>
                <Icon name="spark" size={19} />
              </i>
              <span />
            </div>
            <div className="human-example">
              <span className="tiny-label">IN EVERYDAY WORDS</span>
              <p>No new problem was seen in the heart or lungs on this exam.</p>
              <span className="example-note">
                One phrase, with a little more clarity.
              </span>
            </div>
            <div className="translation-bottom">
              <Icon name="document" size={15} />
              <span>The same information. A clearer way in.</span>
            </div>
          </div>
        </section>
        <div className="principles page-width">
          <span>
            <Icon name="document" size={17} /> Six report types
          </span>
          <span>
            <Icon name="spark" size={17} /> Structured explanations
          </span>
          <span>
            <Icon name="shield" size={17} /> Limitations made visible
          </span>
          <span>
            <Icon name="check" size={17} /> No account needed
          </span>
        </div>
        <section
          className="workspace-section page-width"
          id="workspace"
          aria-labelledby="workspace-title"
        >
          <div className="section-heading">
            <div>
              <span className="eyebrow">YOUR REPORT, A LITTLE CLEARER</span>
              <h2 id="workspace-title">Let’s read between the terms.</h2>
            </div>
            <p>Paste the text. Take it one section at a time.</p>
          </div>
          <div className="workspace-grid">
            <form className="input-panel" onSubmit={analyze}>
              <div className="panel-heading">
                <span className="step-number">01</span>
                <div>
                  <h3>Your report</h3>
                  <p>Start with the words you want to understand.</p>
                </div>
                <Icon name="document" />
              </div>
              <div className="editor-content">
                <label className="field-label" htmlFor="report-type">
                  What kind of report is it?
                </label>
                <select
                  id="report-type"
                  value={type}
                  disabled={loading}
                  onChange={(e) => {
                    setType(e.target.value);
                    setSample(null);
                    reset();
                  }}
                >
                  {TYPES.map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
                <div className="editor-label-row">
                  <label className="field-label" htmlFor="report-text">
                    Report text
                  </label>
                  <span>Paste text only</span>
                </div>
                <textarea
                  id="report-text"
                  ref={editor}
                  value={text}
                  disabled={loading}
                  maxLength={20000}
                  onChange={(e) => {
                    setText(e.target.value);
                    setSample(null);
                    reset();
                  }}
                  placeholder={
                    "Paste your medical report here…\n\nYou can start with the findings, impression, or conclusion section."
                  }
                  aria-describedby={`report-guidance report-count${error ? " report-error" : ""}`}
                  aria-invalid={!!error}
                />
                <div className="editor-bottom">
                  <span id="report-guidance">
                    Remove names, dates of birth, and identifying details.
                  </span>
                  <span id="report-count">
                    {text.length.toLocaleString()} / 20,000
                  </span>
                </div>
                <div className="sample-block">
                  <span>Just looking around? Try a fictional sample.</span>
                  <div className="sample-buttons">
                    {SAMPLES.map((s, i) => (
                      <button
                        key={s.type}
                        type="button"
                        aria-pressed={sample === i}
                        disabled={loading}
                        onClick={() => useSample(i)}
                      >
                        {s.name}
                        <span aria-hidden="true">↗</span>
                      </button>
                    ))}
                  </div>
                </div>
                {error && (
                  <div className="error-message" id="report-error" role="alert">
                    <Icon name="info" size={18} />
                    <span>{error}</span>
                  </div>
                )}
                <div className="editor-actions">
                  <button
                    className="button primary analyze-button"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner" /> Making it clearer…
                      </>
                    ) : (
                      <>
                        Explain my report <Icon name="arrow" size={18} />
                      </>
                    )}
                  </button>
                  {loading ? (
                    <button
                      className="text-button"
                      type="button"
                      onClick={cancel}
                    >
                      Cancel
                    </button>
                  ) : (
                    <button
                      className="text-button"
                      type="button"
                      onClick={clear}
                      disabled={!text && !result}
                    >
                      Clear
                    </button>
                  )}
                </div>
                <p className="submission-note">
                  <Icon name="info" size={14} /> Analyzing sends your text to
                  the configured explanation service.
                </p>
              </div>
            </form>
            <section
              className="results-panel"
              aria-labelledby="result-heading"
              aria-busy={loading}
            >
              <div className="panel-heading">
                <span className="step-number">02</span>
                <div>
                  <h3 id="result-heading" ref={heading} tabIndex={-1}>
                    A clearer picture
                  </h3>
                  <p>
                    {result
                      ? TYPES.find((t) => t[0] === resultType)?.[1]
                      : "Your explanation will come together here."}
                  </p>
                </div>
                {result ? (
                  <span className="result-tag">
                    {result.source === "fallback"
                      ? "Limited result"
                      : result.parse_warning
                        ? "Review needed"
                        : "Ready to read"}
                  </span>
                ) : (
                  <Icon name="spark" />
                )}
              </div>
              {!result && !loading && (
                <div className="empty-state">
                  <div className="empty-illustration" aria-hidden="true">
                    <div className="mini-paper">
                      <span />
                      <span />
                      <span />
                      <span />
                      <i>
                        <Icon name="spark" size={23} />
                      </i>
                    </div>
                  </div>
                  <h4>A little clarity starts here.</h4>
                  <p>
                    Add a report or choose a sample.
                    <br />
                    We’ll organize the explanation into:
                  </p>
                  <div className="empty-outline">
                    <span>
                      <i>01</i> A plain-language summary
                    </span>
                    <span>
                      <i>02</i> Key findings, unpacked
                    </span>
                    <span>
                      <i>03</i> Next steps to discuss
                    </span>
                  </div>
                  <span className="empty-footer">
                    Less jargon. More room to understand.
                  </span>
                </div>
              )}
              {loading && (
                <div className="loading-state" role="status">
                  <div className="loading-orbit">
                    <Icon name="spark" size={30} />
                  </div>
                  <h4>Finding the everyday words.</h4>
                  <p>
                    Reading your report and organizing its explanation.
                    <br />
                    This can take a moment.
                  </p>
                  <div className="loading-lines" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </div>
                  <span className="empty-footer">
                    You can cancel without losing your report.
                  </span>
                </div>
              )}
              {result && (
                <div className="result-content">
                  {(result.parse_warning || result.source === "fallback") && (
                    <div className="result-warning" role="note">
                      <Icon name="info" size={19} />
                      <div>
                        <strong>
                          {result.source === "fallback"
                            ? "Limited keyword fallback"
                            : "This explanation may be incomplete"}
                        </strong>
                        <p>
                          {result.source === "fallback"
                            ? "The model was unavailable. This is a basic keyword scan, not an AI-generated interpretation. It can miss context, including negation. Review the original with a clinician."
                            : "Some parts of the model response could not be read reliably. Check the original report and discuss it with a clinician."}
                        </p>
                      </div>
                    </div>
                  )}
                  <div className="result-toolbar">
                    <div
                      className="result-tabs"
                      role="tablist"
                      aria-label="Explanation view"
                    >
                      {["explanation", "original"].map((value, i) => (
                        <button
                          key={value}
                          ref={(el) => {
                            tabs.current[i] = el;
                          }}
                          id={`${value}-tab`}
                          role="tab"
                          type="button"
                          aria-selected={tab === value}
                          aria-controls={`${value}-panel`}
                          tabIndex={tab === value ? 0 : -1}
                          onClick={() => setTab(value)}
                          onKeyDown={(e) => {
                            if (
                              [
                                "ArrowLeft",
                                "ArrowRight",
                                "Home",
                                "End",
                              ].includes(e.key)
                            ) {
                              e.preventDefault();
                              const n =
                                e.key === "Home"
                                  ? 0
                                  : e.key === "End"
                                    ? 1
                                    : 1 - i;
                              setTab(n ? "original" : "explanation");
                              tabs.current[n]?.focus();
                            }
                          }}
                        >
                          {i ? "Original report" : "Explanation"}
                        </button>
                      ))}
                    </div>
                    <div className="result-actions">
                      <button
                        type="button"
                        aria-label="Copy explanation"
                        title="Copy explanation"
                        onClick={copy}
                      >
                        <Icon name="copy" size={17} />
                      </button>
                      <button
                        type="button"
                        aria-label="Download explanation"
                        title="Download explanation"
                        onClick={download}
                      >
                        <Icon name="download" size={18} />
                      </button>
                    </div>
                  </div>
                  <div
                    id="explanation-panel"
                    role="tabpanel"
                    aria-labelledby="explanation-tab"
                    hidden={tab !== "explanation"}
                    tabIndex={0}
                  >
                    <article className="summary-section">
                      <span className="tiny-label">THE SHORT VERSION</span>
                      <h4>In everyday words</h4>
                      <p>
                        {result.summary ||
                          "No summary was returned. Review the original report."}
                      </p>
                    </article>
                    <article className="findings-section">
                      <h4>
                        <Icon name="document" size={16} /> Key findings
                      </h4>
                      {result.key_findings.length ? (
                        <ul>
                          {result.key_findings.map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="muted">
                          No findings were returned. This does not confirm a
                          normal result.
                        </p>
                      )}
                    </article>
                    <article className="next-section">
                      <h4>
                        <Icon name="arrow" size={16} /> Next steps to discuss
                      </h4>
                      {result.recommendations.length ? (
                        <ul>
                          {result.recommendations.map((r, i) => (
                            <li key={i}>{r}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="muted">
                          Bring your report and questions to your clinician.
                        </p>
                      )}
                    </article>
                  </div>
                  <div
                    id="original-panel"
                    role="tabpanel"
                    aria-labelledby="original-tab"
                    hidden={tab !== "original"}
                    tabIndex={0}
                  >
                    <span className="tiny-label">YOUR SUBMITTED TEXT</span>
                    <pre className="original-text">{original}</pre>
                  </div>
                  <div className="result-disclaimer">
                    <Icon name="shield" size={17} />
                    <p>{result.disclaimer || DISCLAIMER}</p>
                  </div>
                </div>
              )}
            </section>
          </div>
          <div className="workspace-status" role="status" aria-live="polite">
            {notice}
          </div>
        </section>
        <section
          className="how-section page-width"
          id="how-it-works"
          aria-labelledby="how-title"
        >
          <div className="section-heading">
            <div>
              <span className="eyebrow">A SIMPLER WAY THROUGH</span>
              <h2 id="how-title">
                From “what does this mean?”
                <br />
                to a better conversation.
              </h2>
            </div>
            <p>
              Understanding your report is a starting point.
              <br />
              Your care team helps you decide what comes next.
            </p>
          </div>
          <div className="how-grid">
            {[
              [
                "Bring the words.",
                "Paste a report excerpt and select its type. Remove personal details before sending.",
              ],
              [
                "Find the meaning.",
                "Read a structured explanation, key findings, and any clearly marked limitations.",
              ],
              [
                "Keep asking.",
                "Compare with the original. Take your explanation and questions to your clinician.",
              ],
            ].map(([title, body], i) => (
              <article key={title}>
                <span className="how-number">0{i + 1} /</span>
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="care-note page-width">
          <div className="care-note-icon">
            <Icon name="shield" size={25} />
          </div>
          <div>
            <h2>
              A companion for understanding.
              <br />
              Your clinician for care.
            </h2>
            <p>
              AI can miss context and make mistakes. MedExplain AI is an
              educational portfolio project, not a diagnostic tool. It doesn’t
              replace a conversation with a qualified healthcare professional.
            </p>
          </div>
          <span className="care-note-signature">
            A little clarity.
            <br />
            <em>A more human conversation.</em>
          </span>
        </section>
      </main>
      <footer className="site-footer page-width">
        <a href="#top" aria-label="MedExplain AI home">
          <Brand />
        </a>
        <span>
          A project by{" "}
          <a
            href="https://github.com/cura4you"
            target="_blank"
            rel="noopener noreferrer"
          >
            cura4you
          </a>
        </span>
        <a
          className="source-link"
          href="https://github.com/cura4you/MedExplain_AI"
          target="_blank"
          rel="noopener noreferrer"
        >
          View the project <Icon name="external" size={14} />
        </a>
      </footer>
    </>
  );
}
