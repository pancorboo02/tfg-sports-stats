import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Navbar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      fetch(`http://127.0.0.1:8000/search?q=${query}`)
        .then((res) => res.json())
        .then((data) => setResults(data));
    }, 300);

    return () => clearTimeout(timeout);
  }, [query]);

  return (
    <div className="navbar">
      <h2 className="logo" onClick={() => navigate('/')}>
        SmartStats
      </h2>

      <div className="search-wrapper">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar jugador o equipo..."
          className="search-input"
          onKeyDown={(e) => {
            if (e.key === 'ArrowDown') {
              setSelectedIndex((prev) =>
                prev < results.length - 1 ? prev + 1 : prev
              );
            }

            if (e.key === 'ArrowUp') {
              setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
            }

            if (e.key === 'Enter' && selectedIndex >= 0) {
              const selected = results[selectedIndex];

              if (selected.type === 'player') {
                navigate(`/player/${encodeURIComponent(selected.name)}`);
              }

              setResults([]);
              setQuery('');
              setSelectedIndex(-1);
            }
          }}
        />

        {results.length > 0 && (
          <ul className="results-dropdown">
            {results.map((r, i) => (
              <li
                key={i}
                className={`result-item ${i === selectedIndex ? 'active' : ''}`}
                onClick={() => {
                  if (r.type === 'player') {
                    navigate(`/player/${encodeURIComponent(r.name)}`);
                    setResults([]);
                    setQuery('');
                  } else if (r.type === 'team') {
                    navigate(`/team/${encodeURIComponent(r.name)}`);
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
      </div>
    </div>
  );
}

export default Navbar;
