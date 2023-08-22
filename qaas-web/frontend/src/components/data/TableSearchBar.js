import React, { useState } from 'react';
import { AutoComplete } from 'antd';

function TableSearchBar({ data, columns, onSearchSelect }) {
    const [searchResults, setSearchResults] = useState([]);

    const handleSearch = (searchText) => {
        const results = [];
        let foundInAnyColumn = false;  // track if the searchText is found in any column

        columns.forEach(column => {
            data.some(row => {
                const value = typeof column.accessor === 'function' ? column.accessor(row) : row[column.accessor];
                if (value && value.toString().toLowerCase().includes(searchText.toLowerCase())) {
                    foundInAnyColumn = true;
                    if (!results.some(result => result.Header === column.Header)) {
                        results.push({ Header: column.Header, SearchText: searchText });
                    }
                    return true;  // Stops match is found 
                }
                return false;  // Continue the loop
            });
        });

        // If searchText is found in any column, add an aggregated result
        if (foundInAnyColumn) {
            results.push({ Header: 'All', SearchText: searchText });
        }

        setSearchResults(results);
    };


    return (
        <AutoComplete
            style={{ width: 200 }}
            onSearch={handleSearch}
            onSelect={onSearchSelect}
            className="table-search-input"
            placeholder="Search..."
        >
            {searchResults.map((result, index) => (
                <AutoComplete.Option key={result.Header + index} value={`${result.SearchText} in ${result.Header}`}>
                    {`${result.SearchText} in ${result.Header}`}
                </AutoComplete.Option>

            ))}
        </AutoComplete>
    );
}

export default TableSearchBar;
