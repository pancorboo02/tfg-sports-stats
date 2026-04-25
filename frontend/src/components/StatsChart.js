import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

import { statsMap } from '../utils/statsMap';

function StatsChart({ data, stat }) {
  const formattedData = [...data]
    .sort((a, b) => a.season - b.season)
    .map((d) => ({
      season: d.season,
      value: d[stat] || 0,
    }));

  // 🔥 TOOLTIP PERSONALIZADO
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            background: '#1e1e1e',
            padding: '10px',
            borderRadius: '8px',
            color: 'white',
          }}
        >
          <p>Temporada: {label}</p>
          <p>
            {statsMap[stat]?.label}: {payload[0].value}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: 320, marginTop: '30px' }}>
      <h3>{statsMap[stat]?.label} por temporada</h3>

      <ResponsiveContainer>
        <BarChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="season" tick={{ fill: '#ccc' }} />

          <YAxis tick={{ fill: '#ccc' }} />

          {/* 🔥 AQUÍ ESTABA EL FALLO: ahora sí usamos CustomTooltip */}
          <Tooltip content={<CustomTooltip />} />

          <Bar
            dataKey="value"
            fill={statsMap[stat]?.color || '#8884d8'}
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default StatsChart;
