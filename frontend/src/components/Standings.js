import { useEffect, useState } from 'react';
import './Standings.css';
import leagueLogos from '../utils/leagueLogos';
import { useNavigate } from 'react-router-dom';

function Standings({ competition, season, teamName }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!competition || !season) return;

    setLoading(true);

    fetch(
      `http://127.0.0.1:8000/standings?competition=${competition}&season=${season}`
    )
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => {
        setData([]);
        setLoading(false);
      });
  }, [competition, season]);

  if (loading) return <p>Cargando clasificación...</p>;
  console.log('STANDINGS PARAMS:', competition, season);
  if (!data || data.length === 0) {
    return (
      <p style={{ marginTop: '20px', color: '#aaa' }}>
        No hay clasificación disponible
      </p>
    );
  }

  return (
    <div className="standings-container">
      <div className="league-header">
        <img
          src={leagueLogos[competition]}
          alt={competition}
          className="league-logo"
        />

        <h2>{competition}</h2>
      </div>

      <table className="standings-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Equipo</th>
            <th>PJ</th>
            <th>PG</th>
            <th>PE</th>
            <th>PP</th>
            <th>GF</th>
            <th>GC</th>
            <th>DG</th>
            <th>Pts</th>
          </tr>
        </thead>

        <tbody>
          {data.map((team, i) => {
            const isCurrent =
              team.team_name.toLowerCase() === teamName.toLowerCase();

            let rowClass = '';

            if (i < 4) rowClass += ' champions';
            if (i >= data.length - 3) rowClass += ' relegation';
            if (isCurrent) rowClass += ' highlight';

            return (
              <tr key={i} className={rowClass}>
                <td>{i + 1}</td>
                <td>
                  <div
                    className="standings-team"
                    onClick={() =>
                      navigate(`/team/${encodeURIComponent(team.team_name)}`)
                    }
                  >
                    {team.logo_url && (
                      <img
                        src={team.logo_url}
                        alt={team.team_name}
                        className="standings-logo"
                      />
                    )}

                    <span>{team.team_name}</span>
                  </div>
                </td>
                <td>{team.matches}</td>
                <td>{team.wins}</td>
                <td>{team.draws}</td>
                <td>{team.losses}</td>
                <td>{team.goals_for}</td>
                <td>{team.goals_against}</td>
                <td>{team.goal_diff}</td>
                <td>{team.points}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default Standings;
