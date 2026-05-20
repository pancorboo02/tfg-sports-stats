export const queryColumnsMap = {
  name: 'Jugador',
  team_name: 'Equipo',
  nationality: 'Nacionalidad',
  pos: 'Posición',
  season: 'Temporada',
  competition: 'Competición',

  goals: 'Goles',
  assists: 'Asistencias',

  matches: 'Partidos',
  wins: 'Victorias',
  draws: 'Empates',
  losses: 'Derrotas',
  points: 'Puntos',

  goals_for: 'GF',
  goals_against: 'GC',
  goal_diff: 'DG',

  shots: 'Tiros',
  shots_on_target: 'Tiros a puerta',

  'Playing Time_MP': 'Partidos',
  'Playing Time_Starts': 'Titularidades',
  'Playing Time_Min': 'Minutos',
  'Playing Time_90s': '90s',

  'Performance_G+A': 'G+A',
  'Performance_G-PK': 'Goles sin penalti',
  Performance_PK: 'Penaltis',
  Performance_PKatt: 'Penaltis intentados',
  Performance_CrdY: 'Amarillas',
  Performance_CrdR: 'Rojas',

  'Per 90 Minutes_Gls': 'Goles /90',
  'Per 90 Minutes_Ast': 'Asistencias /90',
  'Per 90 Minutes_G+A': 'G+A /90',
  'Per 90 Minutes_G-PK': 'Goles sin penalti /90',
  'Per 90 Minutes_G+A-PK': 'G+A sin penaltis /90',

  'Standard_SoT%': 'Precisión tiro %',
  'Standard_Sh/90': 'Tiros /90',
  'Standard_SoT/90': 'Tiros puerta /90',
  'Standard_G/Sh': 'Conversión tiro',
  'Standard_G/SoT': 'Conversión puerta',

  Standard_PK: 'Penaltis',
  Standard_PKatt: 'Penaltis intentados',
};

export function formatColumnName(column) {
  if (queryColumnsMap[column]) {
    return queryColumnsMap[column];
  }

  return column.replaceAll('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}
