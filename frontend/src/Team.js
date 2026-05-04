import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import StatsChart from './components/StatsChart';
import { formatSeason } from './utils/formatSeason';
import Standings from './components/Standings';

function Team() {
  const { name } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [season, setSeason] = useState(null);
  const [selectedStat, setSelectedStat] = useState('goals');

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/team/${name}`)
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

  if (!current) return <div>Cargando temporada...</div>;
  console.log(current);
  return (
    <div style={{ padding: 20 }}>
      {/* 🔙 VOLVER */}
      <button onClick={() => navigate(-1)}>⬅️ Volver</button>

      {/* HEADER */}
      <h1>{name}</h1>

      {/* SELECTOR TEMPORADA */}
      <select value={season} onChange={(e) => setSeason(e.target.value)}>
        {seasons.map((s, i) => (
          <option key={i} value={s}>
            {formatSeason(s)}
          </option>
        ))}
      </select>

      {/* SELECTOR STAT */}
      <select
        value={selectedStat}
        onChange={(e) => setSelectedStat(e.target.value)}
      >
        <option value="goals">Goles</option>
        <option value="shots">Tiros</option>
        <option value="shots_on_target">Tiros a puerta</option>
      </select>

      {/* STATS */}
      <div className="stats-grid">
        <div className="stat-card">
          ⚽<h3>{current.goals}</h3>
          <p>Goles</p>
        </div>

        <div className="stat-card">
          🎯
          <h3>{current.shots_on_target}</h3>
          <p>Tiros a puerta</p>
        </div>

        <div className="stat-card">
          📊
          <h3>{current.shots}</h3>
          <p>Tiros</p>
        </div>
      </div>

      {/* GRÁFICO */}
      <StatsChart data={data} stat={selectedStat} />

      <Standings
        competition={current.league}
        season={current.season}
        teamName={name}
      />
    </div>
  );
}

export default Team;
