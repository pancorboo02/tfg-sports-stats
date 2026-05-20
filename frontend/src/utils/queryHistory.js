export const getQueryHistory = async () => {
  const res = await fetch('http://127.0.0.1:8000/query-history');

  return await res.json();
};
