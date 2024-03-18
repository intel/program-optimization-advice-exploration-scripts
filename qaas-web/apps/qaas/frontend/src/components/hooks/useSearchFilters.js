import { useState } from 'react';

export function useSearchFilters(initialData) {
    const [columnFilters, setColumnFilters] = useState({});

    const filteredData = initialData.filter(row => {
        for (const [col, filterValue] of Object.entries(columnFilters)) {
            if (!row[col] || !row[col].toString().toLowerCase().includes(filterValue.toLowerCase())) {
                return false;
            }
        }
        return true;
    });

    return { filteredData, setColumnFilters, columnFilters };
}
