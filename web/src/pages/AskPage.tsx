import { useState } from 'react';
import { askQuestion } from '../api';

interface Citation {
  chunk_id: number;
  quote: string;
  source_title: string | null;
}

interface Answer {
  query: string;
  answer: string;
  supporting_evidence: string[];
  inferred_points: string[];
  citations: Citation[];
  uncertainty: string;
}

export default function AskPage() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if (!query.trim()) return;
    setLoading(true);
    setAnswer(null);
    try {
      const data = await askQuestion(query);
      setAnswer(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Ask</h1>
      <div className="search-bar">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a question..."
        />
        <button onClick={handleAsk} disabled={loading}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {answer && (
        <div className="answer-card">
          <section>
            <h2>回答</h2>
            <p>{answer.answer}</p>
          </section>

          {answer.supporting_evidence.length > 0 && (
            <section>
              <h3>证据</h3>
              <ul>
                {answer.supporting_evidence.map((e, i) => (
                  <li key={i} className="evidence">"{e}"</li>
                ))}
              </ul>
            </section>
          )}

          {answer.inferred_points.length > 0 && (
            <section>
              <h3>推导</h3>
              <ul>
                {answer.inferred_points.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </section>
          )}

          {answer.citations.length > 0 && (
            <section>
              <h3>引用</h3>
              {answer.citations.map((c, i) => (
                <div key={i} className="citation">
                  {/* <span className="chunk-badge">Chunk {c.chunk_id}</span> */}
                  {c.source_title && <span className="source-badge">{c.source_title}</span>}
                  <span className="quote">"{c.quote}"</span>
                </div>
              ))}
            </section>
          )}

          {answer.uncertainty !== 'None' && (
            <section>
              <h3>不确定性</h3>
              <p className="uncertainty">{answer.uncertainty}</p>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
