import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import playerPlaceholder from './assets/player-placeholder.png';
import { useNavigate } from 'react-router-dom';
import { formatColumnName } from './utils/queryColumnsMap';

function Ask() {
  const [searchParams] = useSearchParams();

  const question = searchParams.get('q');

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`http://127.0.0.1:8005/ask?question=${encodeURIComponent(question)}`)
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        setLoading(false);
      });
  }, [question]);

  if (loading) {
    return <div style={{ padding: '20px' }}>Generando consulta...</div>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>{question}</h1>

      {/* <h3>SQL generado</h3>

      <pre>{data?.sql}</pre> */}

      {data?.error ? (
        <div>
          <h3>Error</h3>
          <pre>{data.error}</pre>
        </div>
      ) : (
        <div>
          <h3>Resultados</h3>

          {data?.results?.length > 0 && (
            <table className="ai-results-table">
              <thead>
                <tr>
                  {Object.keys(data.results[0])
                    .filter((key) => key !== 'team_logo')
                    .map((key) => (
                      <th key={key}>{formatColumnName(key)}</th>
                    ))}
                </tr>
              </thead>

              <tbody>
                {data.results.map((row, i) => (
                  <tr key={i}>
                    {Object.entries(row).map(([key, value], j) => (
                      <td key={j}>
                        {key === 'name' ? (
                          <div
                            className="ai-player-cell ai-clickable"
                            onClick={() =>
                              navigate(`/player/${encodeURIComponent(value)}`)
                            }
                          >
                            <img
                              src={playerPlaceholder}
                              alt={value}
                              className="ai-player-mini"
                            />

                            <span>{value}</span>
                          </div>
                        ) : key === 'team_name' ? (
                          <div
                            className="ai-player-cell ai-clickable"
                            onClick={() =>
                              navigate(`/team/${encodeURIComponent(value)}`)
                            }
                          >
                            {row.team_logo && (
                              <img
                                src={row.team_logo}
                                alt={value}
                                className="ai-team-logo"
                              />
                            )}

                            <span>{value}</span>
                          </div>
                        ) : key === 'team_logo' ? null : (
                          value
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

export default Ask;
