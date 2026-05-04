const posMap = {
  GK: 'Portero',
  DF: 'Defensa',
  MF: 'Centrocampista',
  FW: 'Delantero',
};

export function formatPosition(pos) {
  if (!pos) return '';

  return pos
    .split(',')
    .map((p) => posMap[p] || p)
    .join(' / ');
}
