import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { countryMap } from './utils/countries';
import StatsChart from './components/StatsChart';
import { statsMap } from './utils/statsMap';
import { formatSeason } from './utils/formatSeason';
import { formatPosition } from './utils/positionsMap';
import playerPlaceholder from './assets/player-placeholder.png';
import { formatAge } from './utils/formatAge';
import './App.css';

function Player() {
  const { name } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [season, setSeason] = useState(null);
  const [selectedStat, setSelectedStat] = useState('goals');

  useEffect(() => {
    window.scrollTo(0, 0);
    fetch(`http://127.0.0.1:8001/player/${name}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        if (data.length > 0) {
          setSeason(data[0].season);
        }
      });
  }, [name]);

  if (data.length === 0) return <div>Cargando...</div>;

  const seasons = [...new Set(data.map((d) => d.season))];

  const current = data.find((d) => Number(d.season) === Number(season));
  const teamData = current.team_data ? current.team_data.split('||') : [];

  if (!current) return <div>Cargando temporada...</div>;

  return (
    <div style={{ padding: '20px' }}>
      {/* HEADER */}
      <div className="player-header">
        <img src={playerPlaceholder} alt={name} className="player-avatar" />

        <div>
          <h1>{name}</h1>
          <p>
            {formatAge(current.age)}
            {' · '}
            {countryMap[current.nationality] || current.nationality}
            {' · '}
            {formatPosition(current.pos)}
            {' · '}
            Nacido en {current.born ?? 'N/D'}
          </p>
        </div>
      </div>

      <div className="player-teams">
        {teamData.map((item, index) => {
          const [team, logo] = item.split('@@');

          return (
            <div
              key={index}
              className="player-team"
              onClick={() => navigate(`/team/${encodeURIComponent(team)}`)}
            >
              {logo && (
                <img src={logo} alt={team} className="player-team-logo" />
              )}

              <span>{team}</span>
            </div>
          );
        })}
      </div>

      {/* SELECTOR TEMPORADA */}
      <select value={season} onChange={(e) => setSeason(e.target.value)}>
        {seasons.map((s, i) => (
          <option key={i} value={s}>
            {formatSeason(s)}
          </option>
        ))}
      </select>

      {/* SELECTOR STAT (arrelgado) */}
      <select
        value={selectedStat}
        onChange={(e) => setSelectedStat(e.target.value)}
      >
        {Object.entries(statsMap).map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>

      {/* STATS PRINCIPALES */}
      <div className="stats-grid">
        <div className="stat-card">
          <span>⚽</span>
          <h3>{current.goals}</h3>
          <p>Goles</p>
        </div>

        <div className="stat-card">
          <span>🎯</span>
          <h3>{current.assists}</h3>
          <p>Asistencias</p>
        </div>

        <div className="stat-card">
          <span>📅</span>
          <h3>{current.matches_played}</h3>
          <p>Partidos jugados</p>
        </div>

        <div className="stat-card">
          <span>⏱️</span>
          <h3>{current.minutes}</h3>
          <p>Minutos</p>
        </div>

        <div className="stat-card">
          <span>🟨</span>
          <h3>{current.yellow_cards}</h3>
          <p>Amarillas</p>
        </div>

        <div className="stat-card">
          <span>🟥</span>
          <h3>{current.red_cards}</h3>
          <p>Rojas</p>
        </div>
      </div>

      {/* GRÁFICO */}
      <StatsChart data={data} stat={selectedStat} />
    </div>
  );
}

export default Player;
