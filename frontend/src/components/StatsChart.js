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
import { formatSeason } from '../utils/formatSeason';
import { LabelList } from 'recharts';
import { teamStatsMap } from '../utils/teamStatsMap';

function StatsChart({ data, stat }) {
  const formattedData = [...data]
    .sort((a, b) => a.season - b.season)
    .map((d) => ({
      season: formatSeason(d.season),
      value: d[stat] || 0,
    }));

  // TOOLTIP PERSONALIZADO
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

  const renderCustomLabel = (props) => {
    const { x, y, width, height, value } = props;

    // Si la barra es muy pequeña, lo dejamos arriba (afuera)
    if (height < 30) {
      return (
        <text
          x={x + width / 2}
          y={y - 8}
          textAnchor="middle"
          fill="#ccc"
          fontSize={14}
        >
          {value}
        </text>
      );
    }

    // Barra grande -> Texto dentro
    return (
      <text
        x={x + width / 2}
        // Cambia el 15 por 25 o 30 para bajarlo más
        y={y + 25}
        textAnchor="middle"
        fill="white"
        fontWeight="bold"
        fontSize={20} // Un tamaño de 20-24 suele quedar bien
      >
        {value}
      </text>
    );
  };

  return (
    <div style={{ width: '100%', height: 320, marginTop: '30px' }}>
      <h3>{teamStatsMap[stat]} por temporada</h3>

      <ResponsiveContainer>
        <BarChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="season" tick={{ fill: '#ccc' }} />

          <YAxis tick={{ fill: '#ccc' }} />

          <Tooltip content={<CustomTooltip />} />

          <Bar
            dataKey="value"
            fill={statsMap[stat]?.color || '#8884d8'}
            radius={[6, 6, 0, 0]}
          >
            <LabelList dataKey="value" content={renderCustomLabel} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default StatsChart;
