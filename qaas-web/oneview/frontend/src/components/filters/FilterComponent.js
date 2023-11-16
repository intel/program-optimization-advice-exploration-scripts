// FilterComponent.js
import React, { useState, useEffect } from 'react';
import FilterMenu from './FilterMenu';
import '../css/filter.css'
import { Row, Col } from 'antd';
import { INITIAL_FILTERS } from './InitialFilter';

export default function FilterComponent({ onFilter, filters, setFilters }) {

    const [selectedFilters, setSelectedFilters] = useState([]);
    const [resetFilters, setResetFilters] = useState(false);


    //count how many filters are selected
    useEffect(() => {
        let selected = [];
        for (const category in filters) {
            for (const subCategory in filters[category]) {
                for (const filterType in filters[category][subCategory]) {
                    const filter = filters[category][subCategory][filterType];
                    if (filter.selected && filter.value !== '') {
                        selected.push({
                            type: filter.accessor,
                            operator: filter.operator,
                            value: filter.value,
                            mode: filter.mode
                        });
                    }
                }
            }
        }
        setSelectedFilters(selected);
    }, [filters]);


    //reset filters check
    useEffect(() => {
        if (resetFilters) {
            setResetFilters(false);  // reset the reset state after it has been processed
        }
    }, [resetFilters]);




    const applyFilter = () => {
        onFilter(selectedFilters);
    }
    const handleInputChange = (category, subCategory, filterType, attribute, value) => {

        setFilters(prevState => {
            const newState = {
                ...prevState,
                [category]: {
                    ...prevState[category],
                    [subCategory]: {
                        ...prevState[category][subCategory],
                        [filterType]: {
                            ...prevState[category][subCategory][filterType],
                            [attribute]: value
                        }
                    }
                }
            };
            return newState;
        });

    };

    const resetAllFilters = () => {
        setFilters(INITIAL_FILTERS);
        setSelectedFilters([])
        setResetFilters(true);
    };


    return (
        <div>
            <h2>Filters</h2>
            <Row gutter={16}>
                {Object.keys(filters).map((category) => (
                    <Col key={category}>
                        <FilterMenu
                            category={category}
                            filterOptions={filters[category]}
                            handleInputChange={handleInputChange}
                            resetFilters={resetFilters}
                        />
                    </Col>
                ))}
            </Row>

            <button onClick={applyFilter}>Apply {selectedFilters.length} Filters</button>
            <button onClick={resetAllFilters}>Reset Filters</button>

        </div>
    );
}