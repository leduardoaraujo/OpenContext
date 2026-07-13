import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const examples = ['What is activation?', 'How should retention be interpreted?', 'Show me the evidence for cohorts.']

export default function App() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function indexCorpus() {
    setError('')
    const response = await fetch(`${API}/documents/index`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({path: 'examples/knowledge'}) })
    if (!response.ok) throw new Error('Could not index the example corpus.')
  }

  async function ask(event) {
    event?.preventDefault()
    if (!query.trim()) return
    setBusy(true); setError('')
    try {
      await indexCorpus()
      const response = await fetch(`${API}/ask`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query, top_k: 4}) })
      if (!response.ok) throw new Error('The API returned an error.')
      setAnswer(await response.json())
    } catch (cause) { setError(cause.message) } finally { setBusy(false) }
  }

  return <main className="shell">
    <nav><div className="brand"><span className="mark">◌</span><span>OpenContext</span></div><span className="nav-note">the GAV Insights engine</span></nav>
    <section className="hero"><p className="eyebrow">OPEN SOURCE RAG ENGINE</p><h1>Ask questions.<br /><em>Keep the context.</em></h1><p className="intro">The open source retrieval engine behind GAV Insights. Every answer below is assembled from indexed evidence and returned with its provenance.</p></section>
    <section className="workspace">
      <div className="query-card"><div className="card-label">QUERY THE KNOWLEDGE BASE</div><form onSubmit={ask}><textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder="What would you like to understand?" rows="3" /><button disabled={busy}>{busy ? 'Retrieving…' : 'Retrieve context →'}</button></form><div className="examples">{examples.map((item) => <button key={item} onClick={() => setQuery(item)}>{item}</button>)}</div></div>
      {error && <div className="error">{error}</div>}
      {answer && <section className="result"><div className="result-head"><div><div className="card-label">GROUNDED RESPONSE</div><h2>{answer.confidence === 'grounded' ? 'Context found' : 'Not enough context'}</h2></div><span className={`confidence ${answer.confidence}`}>{answer.confidence}</span></div><p className="answer">{answer.answer}</p><div className="card-label source-label">EVIDENCE TRAIL · {answer.sources.length} SOURCES</div><div className="sources">{answer.sources.map((source) => <article className="source" key={`${source.path}-${source.heading}`}><div><strong>{source.heading}</strong><span>{source.path}</span></div><span className="score">{source.score.toFixed(2)}</span><p>{source.excerpt}</p></article>)}</div></section>}
      {!answer && !busy && <div className="empty"><span>01</span><p>Index the sample corpus, then ask a question to see retrieval and provenance in one place.</p></div>}
    </section>
    <footer><span>OpenContext · retrieval-only by default</span><span>Python · FastAPI · React</span></footer>
  </main>
}
