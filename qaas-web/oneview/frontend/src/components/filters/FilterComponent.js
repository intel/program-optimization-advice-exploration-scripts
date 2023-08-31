// FilterComponent.js
import React, { useState, useEffect } from 'react';
import FilterMenu from './FilterMenu';
import '../css/filter.css'
import { Row, Col } from 'antd';
export default function FilterComponent({ onFilter, filters, setFilters }) {

    const [selectedFilters, setSelectedFilters] = useState([]);


    //count how many filters are selected
    useEffect(() => {
        let selected = [];
        for (const category in filters) {
            for (const filterType in filters[category]) {
                const filter = filters[category][filterType];
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
        setSelectedFilters(selected);
    }, [filters]);

    const applyFilter = () => {
        onFilter(selectedFilters);
    }
    const handleInputChange = (category, filterType, attribute, value) => {
        setFilters(prevState => ({
            ...prevState,
            [category]: {
                ...prevState[category],
                [filterType]: {
                    ...prevState[category][filterType],
                    [attribute]: value
                }
            }
        }));
    };



    return (
        <div>
            <h2>Filters</h2>
            <Row>
                {Object.keys(filters).map((category) => (
                    <Col key={category}>
                        <FilterMenu
                            category={category}
                            filterOptions={filters[category]}
                            handleInputChange={handleInputChange}
                        />
                    </Col>
                ))}
            </Row>

            <button onClick={applyFilter}>Apply {selectedFilters.length} Filters</button>

        </div>
    );
}