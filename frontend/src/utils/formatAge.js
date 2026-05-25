export function formatAge(age) {
  if (!age) return 'N/D';

  const parts = age.split('-');

  if (parts.length !== 2) {
    return age;
  }

  const years = parts[0];
  const days = parts[1];

  return `${years} años ${days} días`;
}
