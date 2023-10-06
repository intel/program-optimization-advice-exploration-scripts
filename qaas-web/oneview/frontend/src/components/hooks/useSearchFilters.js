import { useState } from 'react';

export function useSearchFilters(initialData, columns) {
    const [globalFilter, setGlobalFilter] = useState("");
    const [columnFilters, setColumnFilters] = useState({});

    const filteredData = initialData.filter(row => {
        // Global filter
        if (globalFilter) {
            if (Object.values(row).some(value =>
                value && value.toString().toLowerCase().includes(globalFilter.toLowerCase())
            )) {
                return true;
            }
        }

        // Column filters
        for (const [col, filterValue] of Object.entries(columnFilters)) {
            if (!row[col] || !row[col].toString().toLowerCase().includes(filterValue.toLowerCase())) {
                return false;
            }
        }

        return true;
    });

    return { filteredData, setGlobalFilter, setColumnFilters };
}
