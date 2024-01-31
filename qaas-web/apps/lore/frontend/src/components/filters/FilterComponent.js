import React, { useState } from 'react';
import AppliedFilters from './AppliedFilters';
import FilterMenu from './FilterMenu';
const initialFilters = {
    "hardware vendor": { 'is': '' },
    "number of mutation": { 'less than': '', 'bigger than': '', 'equal to': '' }
};

export default function FilterComponent({ onFilter }) {
    const [filters, setFilters] = useState(initialFilters);
    const [appliedFilters, setAppliedFilters] = useState([]);

    const applyFilter = (filterType, operator) => {
        if (filterType && operator && filters[filterType][operator] !== '') { // Ensuring the value can be 0
            const newFilter = { type: filterType, operator: operator, value: filters[filterType][operator] };

            // prepare new state
            const newFilters = [...appliedFilters, newFilter];

            // set state
            setAppliedFilters(newFilters);

            // use new state directly
            onFilter(newFilters);
        }
    }

    // handle input change
    const handleInputChange = (filterType, operator, value) => {
        setFilters(prevState => ({
            ...prevState,
            [filterType]: {
                ...prevState[filterType],
                [operator]: value
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
