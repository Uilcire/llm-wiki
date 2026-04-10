import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import AskPage from './pages/AskPage';
import KnowledgePage from './pages/KnowledgePage';
import IngestPage from './pages/IngestPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <h2>LLM Wiki</h2>
          <NavLink to="/">Ask</NavLink>
          <NavLink to="/knowledge">Knowledge</NavLink>
          <NavLink to="/ingest">Ingest</NavLink>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<AskPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/ingest" element={<IngestPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
