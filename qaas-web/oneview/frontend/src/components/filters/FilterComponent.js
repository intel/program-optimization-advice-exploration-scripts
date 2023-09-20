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