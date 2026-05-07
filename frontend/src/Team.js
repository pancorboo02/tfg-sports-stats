import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import StatsChart from './components/StatsChart';
import { formatSeason } from './utils/formatSeason';
import Standings from './components/Standings';
import { teamStatsMap } from './utils/teamStatsMap';
import { teamStatsInfo } from './utils/teamStatsInfo';

function Team() {
  const { name } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState([]);
  const [season, setSeason] = useState(null);
  const [competition, setCompetition] = useState(null);
  const [selectedStat, setSelectedStat] = useState('goals');
  const [standings, setStandings] = useState([]);

  // 🔥 cargar datos del equipo
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/team/${name}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);

        if (data.length > 0) {
          setSeason(data[0].season);
          setCompetition(data[0].competition); // 🔥 IMPORTANTE: usar competition
        }
      });
  }, [name]);

  // 🔥 cargar standings
  useEffect(() => {
    if (!competition || !season) return;

    fetch(
      `http://127.0.0.1:8000/standings?competition=${encodeURIComponent(
        competition
      )}&season=${season}`
    )
      .then((res) => res.json())
      .then((data) => setStandings(data))
      .catch((err) => console.error('Standings error:', err));
  }, [competition, season]);

  if (data.length === 0) return <div>Cargando...</div>;

  // 🔥 obtener competiciones únicas
  const competitions = [...new Set(data.map((d) => d.competition))];

  // 🔥 temporadas filtradas por competición
  const seasons = [
    ...new Set(
      data.filter((d) => d.competition === competition).map((d) => d.season)
    ),
  ];

  // 🔥 datos filtrados por competición
  const filteredData = data.filter((d) => d.competition === competition);

  // 🔥 temporada actual
  const current = filteredData.find((d) => Number(d.season) === Number(season));

  if (!current) return <div>No hay datos para esta competición</div>;

  // 🔥 standings del equipo
  const teamStanding = standings.find((t) => t.team_name === name);

  return (
    <div style={{ padding: 20 }}>
      {/* 🔙 VOLVER */}
      <button onClick={() => navigate(-1)}>⬅️ Volver</button>

      {/* HEADER */}
      <h1>{name}</h1>

      {/* 🔥 FILTRO COMPETICIÓN */}
      <select
        value={competition || ''}
        onChange={(e) => {
          setCompetition(e.target.value);
          setSeason(null); // reset temporada
        }}
      >
        {competitions.map((c, i) => (
          <option key={i} value={c}>
            {c}
          </option>
        ))}
      </select>

      {/* 🔥 FILTRO TEMPORADA */}
      <select value={season || ''} onChange={(e) => setSeason(e.target.value)}>
        {seasons.map((s, i) => (
          <option key={i} value={s}>
            {formatSeason(s)}
          </option>
        ))}
      </select>

      {/* 🔥 STATS PRINCIPALES */}
      <div className="stats-grid">
        <div className="stat-card">
          ⚽<h3>{current.goals}</h3>
          <p>Goles</p>
        </div>

        {teamStanding && (
          <>
            <div className="stat-card">
              🟢
              <h3>{teamStanding.wins}</h3>
              <p>Victorias</p>
            </div>

            <div className="stat-card">
              ⚪<h3>{teamStanding.draws}</h3>
              <p>Empates</p>
            </div>

            <div className="stat-card">
              🔴
              <h3>{teamStanding.losses}</h3>
              <p>Derrotas</p>
            </div>
          </>
        )}
      </div>

      {/* 🔥 SELECTOR STAT */}
      <select
        value={selectedStat}
        onChange={(e) => setSelectedStat(e.target.value)}
      >
        {Object.entries(teamStatsMap).map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>

      {/* 🔥 INFO STAT */}
      <div style={{ marginTop: '8px', fontSize: '13px', color: '#aaa' }}>
        {teamStatsInfo[selectedStat]}
      </div>

      {/* 📊 GRÁFICO */}
      <StatsChart data={filteredData} stat={selectedStat} />

      {/* 🏆 CLASIFICACIÓN */}
      {standings.length > 0 ? (
        <Standings competition={competition} season={season} teamName={name} />
      ) : (
        <p style={{ marginTop: '20px', color: '#aaa' }}>
          No hay clasificación disponible
        </p>
      )}
    </div>
  );
}

export default Team;
