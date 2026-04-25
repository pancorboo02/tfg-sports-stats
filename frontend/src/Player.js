import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { countryMap } from './utils/countries';
import StatsChart from './components/StatsChart';
import { statsMap } from './utils/statsMap';

function Player() {
  const { name } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [season, setSeason] = useState(null);
  const [selectedStat, setSelectedStat] = useState('goals');

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/player/${name}`)
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

  return (
    <div style={{ padding: '20px' }}>
      {/* 🔙 VOLVER */}
      <button onClick={() => navigate(-1)}>⬅️ Volver</button>

      {/* HEADER */}
      <h1>{name}</h1>
      <p>
        {countryMap[current.nationality] || current.nationality} · {current.pos}
      </p>

      {/* SELECTOR TEMPORADA */}
      <select value={season} onChange={(e) => setSeason(e.target.value)}>
        {seasons.map((s, i) => (
          <option key={i} value={s}>
            {s}
          </option>
        ))}
      </select>

      {/* SELECTOR STAT (CORREGIDO) */}
      <select
        value={selectedStat}
        onChange={(e) => setSelectedStat(e.target.value)}
      >
        {Object.entries(statsMap).map(([key, obj]) => (
          <option key={key} value={key}>
            {obj.label}
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
          <h3>{current['Playing Time_MP']}</h3>
          <p>Partidos</p>
        </div>

        <div className="stat-card">
          <span>⏱️</span>
          <h3>{current['Playing Time_Min']}</h3>
          <p>Minutos</p>
        </div>
      </div>

      {/* STATS SECUNDARIAS */}
      <div style={{ marginTop: '20px' }}>
        <p>🟨 Amarillas: {current['Performance_CrdY']}</p>
        <p>🟥 Rojas: {current['Performance_CrdR']}</p>
        <p>⚽+🎯 G+A: {current['Performance_G+A']}</p>
      </div>

      {/* GRÁFICO */}
      <StatsChart data={data} stat={selectedStat} />
    </div>
  );
}

export default Player;
