import { useEffect, useState } from 'react';
import './Standings.css';

function Standings({ competition, season, teamName }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

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
      <h3>Clasificación</h3>

      <table className="standings-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Equipo</th>
            <th>Pts</th>
            <th>GF</th>
            <th>GC</th>
            <th>DG</th>
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
                <td>{team.team_name}</td>
                <td>{team.points}</td>
                <td>{team.goals_for}</td>
                <td>{team.goals_against}</td>
                <td>{team.goal_diff}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default Standings;
