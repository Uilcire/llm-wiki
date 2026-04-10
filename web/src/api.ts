const BASE = '/api';

export async function askQuestion(q: string) {
  const res = await fetch(`${BASE}/ask?q=${encodeURIComponent(q)}`);
  return res.json();
}

export async function searchChunks(q: string) {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(q)}`);
  return res.json();
}

export async function createSource(data: { type: string; title?: string; content?: string }) {
  const res = await fetch(`${BASE}/sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function extractSource(sourceId: number) {
  const res = await fetch(`${BASE}/sources/${sourceId}/extract`, { method: 'POST' });
  return res.json();
}

export async function listEntities() {
  const res = await fetch(`${BASE}/entities`);
  return res.json();
}

export async function listClaims() {
  const res = await fetch(`${BASE}/claims`);
  return res.json();
}

export async function listWikiEntries() {
  const res = await fetch(`${BASE}/wiki`);
  return res.json();
}

export async function listThoughtEntries() {
  const res = await fetch(`${BASE}/thoughts`);
  return res.json();
}
