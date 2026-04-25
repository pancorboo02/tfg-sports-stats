import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);

      fetch(`http://127.0.0.1:8000/search?q=${query}`)
        .then((res) => res.json())
        .then((data) => {
          setResults(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error('Error:', err);
          setLoading(false);
        });
    }, 300);

    return () => clearTimeout(timeout);
  }, [query]);

  return (
    <div className="container">
      <h1 className="titulo">TFG Sports Stats</h1>

      <div style={{ position: 'relative', width: '300px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar jugador o equipo..."
          className="search-input"
        />

        {results.length > 0 && (
          <ul className="results-dropdown">
            {results.map((r, i) => (
              <li
                key={i}
                className="result-item"
                onClick={() => {
                  if (r.type === 'player') {
                    navigate(`/player/${encodeURIComponent(r.name)}`);
                  }
                }}
              >
                <span>
                  {r.type === 'player' ? '👤' : '🏟️'} {r.name}
                </span>
                <span className="type">{r.type}</span>
              </li>
            ))}
          </ul>
        )}

        {loading && <div className="loading">Buscando...</div>}
      </div>
    </div>
  );
}

export default Search;
