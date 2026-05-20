import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Navbar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [competition, setCompetition] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      const url = competition
        ? `http://127.0.0.1:8000/search?q=${query}&competition=${competition}`
        : `http://127.0.0.1:8000/search?q=${query}`;

      fetch(url)
        .then((res) => res.json())
        .then((data) => setResults(data))
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeout);
  }, [query, competition]);

  const handleNavigation = (item) => {
    if (item.type === 'player') {
      navigate(`/player/${encodeURIComponent(item.name)}`);
    } else if (item.type === 'team') {
      navigate(`/team/${encodeURIComponent(item.name)}`);
    }

    setResults([]);
    setQuery('');
    setSelectedIndex(-1);
  };

  return (
    <div className="navbar">
      <h2 className="logo" onClick={() => navigate('/')}>
        SmartStats
      </h2>

      <div className="search-wrapper">
        <div className="modern-search">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar jugador o equipo..."
            className="modern-search-input"
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
                handleNavigation(results[selectedIndex]);
              }
            }}
          />

          <select
            className="competition-filter"
            value={competition}
            onChange={(e) => setCompetition(e.target.value)}
          >
            <option value="">Competición</option>
            <option value="Premier League">Premier League</option>
            <option value="La Liga">La Liga</option>
            <option value="Serie A">Serie A</option>
            <option value="Bundesliga">Bundesliga</option>
            <option value="Ligue 1">Ligue 1</option>
          </select>
        </div>

        {results.length > 0 && (
          <ul className="results-dropdown">
            {results.map((r, i) => (
              <li
                key={i}
                className={`result-item ${i === selectedIndex ? 'active' : ''}`}
                onClick={() => handleNavigation(r)}
              >
                <span>
                  <div className="search-result-left">
                    {r.type === 'team' && r.logo_url ? (
                      <img
                        src={r.logo_url}
                        alt={r.name}
                        className="search-team-logo"
                      />
                    ) : (
                      <span className="search-player-icon">👤</span>
                    )}

                    <span>{r.name}</span>
                  </div>
                </span>

                <span className="type">{r.type}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div style={{ width: '120px' }} />
    </div>
  );
}

export default Navbar;
