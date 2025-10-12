import dayjs from 'dayjs';

/**
 * Export data to CSV file
 */
export const exportToCSV = (data: any[], filename: string) => {
  if (!data || data.length === 0) {
    return;
  }

  // Convert data to CSV format
  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(','), // Header row
    ...data.map((row) =>
      headers.map((header) => {
        const value = row[header];
        // Handle values with commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    ),
  ];

  const csv = csvRows.join('\n');
  
  // Add BOM for UTF-8 encoding (for Excel compatibility)
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}_${dayjs().format('YYYYMMDD_HHmmss')}.csv`;
  link.click();
  
  // Clean up
  URL.revokeObjectURL(link.href);
};

/**
 * Export data to Excel (requires xlsx library)
 * Install: npm install xlsx
 */
export const exportToExcel = (data: any[], filename: string) => {
  // This is a placeholder for xlsx library integration
  // For now, fallback to CSV
  exportToCSV(data, filename);
  
  // With xlsx library:
  // import * as XLSX from 'xlsx';
  // const ws = XLSX.utils.json_to_sheet(data);
  // const wb = XLSX.utils.book_new();
  // XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  // XLSX.writeFile(wb, `${filename}_${dayjs().format('YYYYMMDD')}.xlsx`);
};

