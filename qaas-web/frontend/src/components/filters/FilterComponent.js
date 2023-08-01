import React, { useState } from 'react';
import AppliedFilters from './AppliedFilters';
import FilterMenu from './FilterMenu';
const initialFilters = {
    "Loops: Vectorization Ratio (%)": {
        'less than': { value: '', mode: 'all' },
        'bigger than': { value: '', mode: 'all' },
        'equal to': { value: '', mode: 'all' }
    },
    "Global: Total Time (s)": {
        'less than': { value: '', mode: 'all' },
        'bigger than': { value: '', mode: 'all' },
        'equal to': { value: '', mode: 'all' }
    },
    "Global: Array Access Efficiency (%)": {
        'less than': { value: '', mode: 'all' },
        'bigger than': { value: '', mode: 'all' },
        'equal to': { value: '', mode: 'all' }
    }
};
const backendFilterMap = {
    "Loops: Vectorization Ratio (%)": "vectorization ratio",
    "Global: Total Time (s)": "total time",
    "Global: Array Access Efficiency (%)": "vectorization ratio",
};
export default function FilterComponent({ onFilter }) {
    const [filters, setFilters] = useState(initialFilters);
    const [appliedFilters, setAppliedFilters] = useState([]);

    const applyFilter = (filterType, operator) => {
        if (filterType && operator && filters[filterType][operator].value !== '') {
            const newFilter = {
                type: backendFilterMap[filterType],
                operator: operator,
                value: filters[filterType][operator].value,
                mode: filters[filterType][operator].mode
            };

            const newFilters = [...appliedFilters, newFilter];
            setAppliedFilters(newFilters);
            onFilter(newFilters);
        }
    }


    // handle input change
    const handleInputChange = (filterType, operator, value, mode) => {
        setFilters(prevState => ({
            ...prevState,
            [filterType]: {
                ...prevState[filterType],
                [operator]: { value: value, mode: mode }
            }
        }));
    };


    const removeFilter = (indexToRemove) => {
        const updatedFilters = appliedFilters.filter((_, index) => index !== indexToRemove);
        setAppliedFilters(updatedFilters);

        // Re-filter the data
        onFilter(updatedFilters);
    };

    return (
        <div>
            <h2>Filters</h2>

            <FilterMenu
                filterOptions={filters}
                applyFilter={applyFilter}
                handleInputChange={handleInputChange}
            />
            <AppliedFilters appliedFilters={appliedFilters} onRemoveFilter={removeFilter} />
        </div>
    );
}
