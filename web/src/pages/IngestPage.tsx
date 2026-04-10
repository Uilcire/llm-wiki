import { useState } from 'react';
import { createSource, extractSource } from '../api';

export default function IngestPage() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleIngest() {
    if (!content.trim()) return;
    setLoading(true);
    setStatus('Importing...');
    try {
      // Step 1: create source → document → chunks → embedding
      const source = await createSource({
        type: 'text',
        title: title || undefined,
        content,
      });
      setStatus(`Source created (id=${source.id}). Extracting knowledge...`);

      // Step 2: extract entities, claims, wiki, thoughts, links
      const result = await extractSource(source.id);
      setStatus(
        `Done! Extracted: ${result.entities_new} new entities, ` +
        `${result.entities_reused} reused, ${result.claims} claims, ` +
        `${result.wiki_entries} wiki entries, ${result.thought_entries} thoughts, ` +
        `${result.links} links`
      );
      setTitle('');
      setContent('');
    } catch (err) {
      setStatus(`Error: ${err}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <h1>Ingest</h1>
      <div className="ingest-form">
        <input
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="Title (optional)"
        />
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          placeholder="Paste text content here..."
          rows={12}
        />
        <button onClick={handleIngest} disabled={loading}>
          {loading ? 'Processing...' : 'Import & Extract'}
        </button>
      </div>
      {status && <div className="status-box">{status}</div>}
    </div>
  );
}
