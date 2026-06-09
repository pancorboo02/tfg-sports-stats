import { useNavigate } from 'react-router-dom';
import { getQueryHistory } from './utils/queryHistory';
import { useEffect, useState } from 'react';
import mayordomo from './assets/mayordomo.png';
import './App.css';

function Home() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const loadHistory = async () => {
      const data = await getQueryHistory();
      setHistory(data);
    };

    loadHistory();
  }, []);

  const navigate = useNavigate();

  const handleSubmit = () => {
    if (!question.trim()) return;

    navigate(`/ask?q=${encodeURIComponent(question)}`);
  };

  const clearHistory = async () => {
    await fetch('http://127.0.0.1:8005/query-history', {
      method: 'DELETE',
    });

    setHistory([]);
  };

  return (
    <div className="home-container">
      <div className="assistant-header">
        <h1 className="home-title">Pregunta al agente SebastIAn</h1>
        <img
          src={mayordomo}
          alt="Agente SebastIAn"
          className="mayordomo-image"
        />
      </div>

      <p className="home-subtitle">
        Consulta estadísticas de fútbol usando lenguaje natural
      </p>

      <div className="ai-search-box">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ej: máximos goleadores de la Premier League"
          className="ai-search-input"
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSubmit();
            }
          }}
        />

        <button className="ai-search-button" onClick={handleSubmit}>
          Preguntar
        </button>
      </div>

      {history.length > 0 && (
        <div className="query-history">
          <div className="history-header">
            <h3>Consultas recientes</h3>

            <button onClick={clearHistory} className="clear-history-btn">
              Limpiar historial
            </button>
          </div>
          {history.map((item, i) => (
            <div
              key={i}
              className="history-item"
              onClick={() =>
                navigate(`/ask?q=${encodeURIComponent(item.question)}`)
              }
            >
              {item.question}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Home;
