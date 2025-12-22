import { useState } from 'react'

type AnalyzeResponse = {
  summary: string
  key_findings: string[]
  recommendations: string[]
  disclaimer: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const App = () => {
  const [reportText, setReportText] = useState('')
  const [reportType, setReportType] = useState('radiology')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!reportText.trim()) {
      setError('Paste a report to analyze.')
      return
    }
    setError('')
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_text: reportText,
          report_type: reportType,
        }),
      })

      if (!response.ok) {
        throw new Error(`Request failed with ${response.status}`)
      }

      const data = (await response.json()) as AnalyzeResponse
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">MedExplain AI</p>
          <h1>Translate clinical language into calm, human guidance.</h1>
          <p className="lede">
            Paste a medical report, choose the report type, and get a structured explanation
            with safety-forward recommendations.
          </p>
        </div>
        <div className="badge">Safety-first summaries</div>
      </header>

      <main className="panel-grid">
        <section className="panel">
          <h2>Report input</h2>
          <label className="field">
            <span>Report type</span>
            <select value={reportType} onChange={(event) => setReportType(event.target.value)}>
              <option value="radiology">Radiology</option>
              <option value="lab">Lab</option>
              <option value="clinical">Clinical</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="field">
            <span>Paste report</span>
            <textarea
              value={reportText}
              onChange={(event) => setReportText(event.target.value)}
              placeholder="Example: The report notes mild cardiomegaly and no acute disease."
              rows={8}
            />
          </label>
          {error && <div className="error">{error}</div>}
          <button className="primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze report'}
          </button>
        </section>

        <section className="panel results">
          <h2>Explanation</h2>
          {!result && !loading && (
            <div className="empty-state">
              <p>Results will appear here after analysis.</p>
              <ul>
                <li>Plain-language summary</li>
                <li>Key findings in bullet form</li>
                <li>Safe next steps and disclaimer</li>
              </ul>
            </div>
          )}
          {result && (
            <div className="result-grid">
              <article>
                <h3>Summary</h3>
                <p>{result.summary}</p>
              </article>
              <article>
                <h3>Key findings</h3>
                <ul>
                  {result.key_findings.map((finding) => (
                    <li key={finding}>{finding}</li>
                  ))}
                </ul>
              </article>
              <article>
                <h3>Recommendations</h3>
                <ul>
                  {result.recommendations.map((rec) => (
                    <li key={rec}>{rec}</li>
                  ))}
                </ul>
              </article>
              <article className="disclaimer">
                <h3>Disclaimer</h3>
                <p>{result.disclaimer}</p>
              </article>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
