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

  matches_played: 'Partidos',
  starts: 'Titularidades',
  minutes: 'Minutos',
  matches_90s: '90s',

  goal_contributions: 'G+A',
  non_penalty_goal_contributions: 'G+A sin Penaltis',
  non_penalty_goals: 'Goles sin penaltis',
  penalties_scored: 'Penaltis marcados',
  penalties_attempted: 'Penaltis intentados',
  yellow_cards: 'Tarjetas amarillas',
  red_cards: 'Tarjetas rojas',

  per90_goals: 'Goles /90',
  per90_assists: 'Asistencias /90',
  per90_goal_contributions: 'G+A /90',
  per90_non_penalty_goals: 'Goles sin penalti /90',
  per90_non_penalty_goal_contributions: 'G+A sin penaltis /90',

  shot_accuracy: 'Precisión tiro %',
  shots_per90: 'Tiros /90',
  shots_on_target_per90: 'Tiros puerta /90',
  goals_per_shot: 'Conversión tiro',
  goals_per_shot_on_target: 'Conversión puerta',
};

export function formatColumnName(column) {
  if (queryColumnsMap[column]) {
    return queryColumnsMap[column];
  }

  return column.replaceAll('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}
