export function formatSeason(season) {
  const s = String(season);

  // Caso tipo 2021 → 2020-21
  if (s.length === 4 && s.startsWith('20')) {
    const year = parseInt(s);
    return `${year - 1}-${s.slice(2)}`;
  }

  // Caso tipo 2425 → 2024-25
  if (s.length === 4) {
    const start = '20' + s.slice(0, 2);
    const end = s.slice(2);
    return `${start}-${end}`;
  }

  return season;
}
