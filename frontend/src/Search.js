import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './App.css';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [competition, setCompetition] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);

      const url = competition
        ? `http://127.0.0.1:8000/search?q=${query}&competition=${competition}`
        : `http://127.0.0.1:8000/search?q=${query}`;

      fetch(url)
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
  }, [query, competition]);

  return (
    <div className="container">
      <h1 className="titulo">TFG Sports Stats</h1>

      <div style={{ position: 'relative', width: '400px' }}>
        <div className="search-bar">
          <select
            value={competition}
            onChange={(e) => {
              setCompetition(e.target.value);
              setResults([]); // limpia resultados antiguos
            }}
          >
            <option value="">Todas las ligas</option>
            <option value="Premier League">Premier League</option>
            <option value="La Liga">La Liga</option>
            <option value="Serie A">Serie A</option>
            <option value="Bundesliga">Bundesliga</option>
            <option value="Ligue 1">Ligue 1</option>
          </select>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar jugador o equipo..."
            className="search-input"
          />
        </div>
        {results.length > 0 && (
          <ul className="results-dropdown">
            {results.map((r, i) => (
              <li
                key={i}
                className="result-item"
                onClick={() => {
                  if (r.type === 'player') {
                    navigate(`/player/${encodeURIComponent(r.name)}`);
                  } else if (r.type === 'team') {
                    navigate(`/team/${encodeURIComponent(r.name)}`);
                  }
                }}
              >
                <span>
                  {r.type === 'player' ? '👤' : '🏟️'} {r.name}
                  {r.type === 'team' && r.competition && (
                    <span
                      style={{
                        marginLeft: '6px',
                        color: '#aaa',
                        fontSize: '12px',
                      }}
                    >
                      ({r.competition})
                    </span>
                  )}
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
