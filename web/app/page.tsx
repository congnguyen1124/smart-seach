'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';

type SearchItem = {
  id: string;
  title: string;
  description: string;
  tags: string[];
  score: number;
};

type SearchResponse = {
  query: string;
  mode: 'keyword';
  threshold: number;
  count: number;
  items: SearchItem[];
};

type HealthResponse = {
  status: string;
  storage: string;
  embedding_provider: string;
  embedding_dimension: number;
};

const QUICK_SEARCHES = [
  'postgresql pgvector semantic search docker',
  'flutter riverpod architecture',
  'python api testing containers',
];

const INITIAL_QUERY = QUICK_SEARCHES[0];
const SCORE_THRESHOLD = 0.4;

function scoreBand(score: number) {
  if (score > 0.75) return 'high';
  if (score >= 0.5) return 'medium';
  return 'low';
}

export default function Home() {
  const [query, setQuery] = useState(INITIAL_QUERY);
  const [limit, setLimit] = useState(10);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [elapsed, setElapsed] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const runSearch = useCallback(
    async (nextQuery: string) => {
      const normalizedQuery = nextQuery.trim();
      if (!normalizedQuery) return;

      setLoading(true);
      setError(null);
      const startedAt = performance.now();

      try {
        const response = await fetch('/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: normalizedQuery,
            mode: 'keyword',
            threshold: SCORE_THRESHOLD,
            limit,
          }),
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.message ?? payload.error ?? 'Search failed');
        }
        setResult(payload as SearchResponse);
        setElapsed(Math.max(1, Math.round(performance.now() - startedAt)));
      } catch (searchError) {
        setError(
          searchError instanceof Error
            ? searchError.message
            : 'Search is temporarily unavailable',
        );
      } finally {
        setLoading(false);
      }
    },
    [limit],
  );

  useEffect(() => {
    void fetch('/api/status')
      .then((response) => response.json())
      .then((payload: HealthResponse) => setHealth(payload))
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    const initialSearch = window.setTimeout(() => {
      void runSearch(INITIAL_QUERY);
    }, 0);

    return () => window.clearTimeout(initialSearch);
  }, [runSearch]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runSearch(query);
  }

  function chooseQuickSearch(value: string) {
    setQuery(value);
    void runSearch(value);
  }

  return (
    <main>
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="Smart Video Search home">
          <span className="brand-mark">S</span>
          <span>Smart Video Search</span>
        </a>
        <div className="runtime-pill">
          <span
            className={health?.status === 'ok' ? 'status-dot' : 'status-dot off'}
          />
          {health?.status === 'ok' ? 'Search engine online' : 'Connecting'}
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow">Keyword ranking, clearly scored</div>
        <h1>
          Find the right video, <span>faster.</span>
        </h1>
        <p className="hero-copy">
          Search titles, descriptions, and tags. Every result explains its
          keyword coverage with a transparent score and a strict 40% cutoff.
        </p>

        <form className="search-panel" onSubmit={submit}>
          <div className="search-row">
            <label className="search-input-wrap">
              <span className="search-icon" aria-hidden="true">⌕</span>
              <span className="sr-only">Search videos by keyword</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Enter keywords, topics, or technologies…"
                maxLength={500}
              />
            </label>
            <button type="submit" disabled={loading || !query.trim()}>
              {loading ? 'Searching…' : 'Search videos'}
            </button>
          </div>

          <div className="controls-row">
            <div className="threshold-summary">
              <span className="threshold-icon">≥</span>
              Minimum score <strong>40%</strong>
              <span className="threshold-note">Lower matches are hidden</span>
            </div>
            <label className="limit-control">
              <span>Results</span>
              <select
                value={limit}
                onChange={(event) => setLimit(Number(event.target.value))}
              >
                <option value={6}>6</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </label>
          </div>
        </form>

        <div className="quick-searches" aria-label="Suggested searches">
          <span>Try</span>
          {QUICK_SEARCHES.map((suggestion) => (
            <button key={suggestion} onClick={() => chooseQuickSearch(suggestion)}>
              {suggestion}
            </button>
          ))}
        </div>
      </section>

      <section className="results-section" aria-live="polite">
        <div className="results-heading">
          <div>
            <p className="section-kicker">Keyword results</p>
            <h2>
              {result ? `${result.count} ranked matches` : 'Searching your library'}
            </h2>
          </div>
          <div className="query-meta">
            {elapsed !== null && <span>{elapsed} ms</span>}
            <span>{health?.storage ?? 'PostgreSQL + pgvector'}</span>
          </div>
        </div>

        <div className="score-legend" aria-label="Score color thresholds">
          <strong>Score threshold</strong>
          <span className="legend-item high"><i /> Green &gt; 75%</span>
          <span className="legend-item medium"><i /> Yellow 50–75%</span>
          <span className="legend-item low"><i /> Red 40–&lt;50%</span>
          <span className="legend-cutoff">Below 40% hidden</span>
        </div>

        {error && <div className="error-state">{error}</div>}

        <div className="results-grid">
          {loading && !result
            ? Array.from({ length: 3 }).map((_, index) => (
                <div className="result-card skeleton" key={index} />
              ))
            : result?.items.map((item, index) => {
                const band = scoreBand(item.score);
                return (
                  <article className={`result-card ${band}`} key={item.id}>
                    <div className="card-topline">
                      <span className="result-index">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      <div className={`score-badge ${band}`}>
                        <span>{Math.round(item.score * 100)}%</span>
                        match
                      </div>
                    </div>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                    <div className="tags">
                      {item.tags.map((tag) => (
                        <span key={tag}>{tag}</span>
                      ))}
                    </div>
                    <div
                      className={`score-track ${band}`}
                      aria-label={`Keyword score ${item.score.toFixed(2)}`}
                    >
                      <span style={{ width: `${item.score * 100}%` }} />
                    </div>
                  </article>
                );
              })}
        </div>

        {!loading && result?.items.length === 0 && (
          <div className="empty-state">
            <strong>No results reached the 40% threshold.</strong>
            <span>Try fewer keywords or use a more specific topic.</span>
          </div>
        )}
      </section>

      <footer>
        <span>Smart Video Search</span>
        <span>TypeScript · Flask · PostgreSQL · pgvector</span>
      </footer>
    </main>
  );
}
