import React, { useState } from 'react';
import { AutoComplete } from 'antd';
import { mainDrawerItems } from '../sidebar/WelcomePageTableOfContentsDrawer';
import { useNavigate } from 'react-router-dom';

//get drawer items flatten to a searable list
const flattenDrawerItems = (items) => {
    let flatItems = [];

    items.forEach(item => {
        flatItems.push({ path: item.path, text: item.text });

        if (item.children) {
            flatItems = [...flatItems, ...flattenDrawerItems(item.children)];
        }
    });

    return flatItems;
};

const allDrawerItems = flattenDrawerItems(mainDrawerItems);
const searchItems = (query) => {
    return allDrawerItems.filter(item =>
        item.text.toLowerCase().includes(query.toLowerCase())
    );
};


function PageSearchBar() {
    const [searchResults, setSearchResults] = useState([]);
    const navigate = useNavigate();

    const handleSearch = (searchText) => {
        const results = searchItems(searchText);
        setSearchResults(results);
    };

    const onSearchSelect = (value) => {
        // Find the selected item based on value
        const selectedItem = searchResults.find(item => item.path === value);
        if (selectedItem) {
            navigate(selectedItem.path);
        }
    };

    return (
        <AutoComplete
            style={{ width: 200 }}
            onSearch={handleSearch}
            onSelect={onSearchSelect}
            className="page-search-input"
            placeholder="Search pages..."
        >
            {searchResults.map((result, index) => (
                <AutoComplete.Option key={index} value={result.path}>
                    {result.text}
                </AutoComplete.Option>
            ))}
        </AutoComplete>
    );
}

export default PageSearchBar;
