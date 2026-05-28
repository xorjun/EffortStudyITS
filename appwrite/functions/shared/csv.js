export function csvEscape(value) {
  if (value === null || value === undefined) {
    return '';
  }

  const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
  if (/[",\n]/.test(stringValue)) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }
  return stringValue;
}

export function toCsv(rows) {
  return rows.map((row) => row.map(csvEscape).join(',')).join('\n');
}
