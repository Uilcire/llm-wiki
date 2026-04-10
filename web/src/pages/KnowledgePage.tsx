import { useState, useEffect } from 'react';
import { listEntities, listClaims, listWikiEntries, listThoughtEntries } from '../api';

type Tab = 'entities' | 'claims' | 'wiki' | 'thoughts';

export default function KnowledgePage() {
  const [tab, setTab] = useState<Tab>('entities');
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    const fetchers = {
      entities: listEntities,
      claims: listClaims,
      wiki: listWikiEntries,
      thoughts: listThoughtEntries,
    };
    fetchers[tab]().then(setData).finally(() => setLoading(false));
  }, [tab]);

  return (
    <div className="page">
      <h1>Knowledge</h1>
      <div className="tabs">
        {(['entities', 'claims', 'wiki', 'thoughts'] as Tab[]).map(t => (
          <button
            key={t}
            className={tab === t ? 'tab active' : 'tab'}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="data-list">
          {data.length === 0 && <p className="empty">No items yet.</p>}

          {tab === 'entities' && data.map((e: any) => (
            <div key={e.id} className="card">
              <span className="badge">{e.type}</span>
              <strong>{e.name}</strong>
              {e.aliases?.aliases?.length > 0 && (
                <span className="aliases">aka: {e.aliases.aliases.join(', ')}</span>
              )}
            </div>
          ))}

          {tab === 'claims' && data.map((c: any) => (
            <div key={c.id} className="card">
              <span className="badge">{c.status}</span>
              <p>{c.content}</p>
              {c.confidence && <span className="meta">confidence: {c.confidence}</span>}
            </div>
          ))}

          {tab === 'wiki' && data.map((w: any) => (
            <div key={w.id} className="card">
              <span className="badge">{w.status}</span>
              <strong>{w.title}</strong>
              <p>{w.summary}</p>
            </div>
          ))}

          {tab === 'thoughts' && data.map((t: any) => (
            <div key={t.id} className="card">
              <span className="badge">{t.type}</span>
              <strong>{t.summary}</strong>
              {t.content && <p>{t.content}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
