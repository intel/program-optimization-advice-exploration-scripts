import React, { useState } from 'react';
import { AutoComplete } from 'antd';

function TableSearchBar({ data, columns, onSearchSelect }) {
    const [searchResults, setSearchResults] = useState([]);

    const handleSearch = (searchText) => {
        const results = [];

        data.forEach(row => {
            columns.forEach(column => {
                const value = typeof column.accessor === 'function' ? column.accessor(row) : row[column.accessor];
                if (value && value.toString().toLowerCase().includes(searchText.toLowerCase())) {
                    if (!results.some(result => result.Header === column.Header)) {
                        results.push({ Header: column.Header, SearchText: searchText });
                    }
                }
            });
        });

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
