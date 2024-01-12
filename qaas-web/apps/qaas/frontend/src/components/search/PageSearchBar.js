import React, { useState } from 'react';
import { AutoComplete } from 'antd';
import { mainDrawerItems } from '../sidebar/WelcomePageTableOfContentsDrawer';
import { useNavigate } from 'react-router-dom';
import { extractContentFromComponentList } from './util';
import { layoutRoutes } from '../QaaSRouting';

const routeMappings = extractContentFromComponentList(layoutRoutes);

const getSnippetAroundQuery = (content, query) => {
    const queryLower = query.toLowerCase();
    const words = content.split(/\s+/);
    const queryIndex = words.findIndex(word => word.toLowerCase().includes(queryLower));

    if (queryIndex === -1) {
        return ""; //  not found
    }

    const startIndex = Math.max(0, queryIndex - 3);
    const endIndex = Math.min(words.length, queryIndex + 4); // +4 because slice doesn't include the end index

    const snippetStart = startIndex > 0 ? '... ' : '';
    const snippetEnd = endIndex < words.length ? ' ...' : '';

    const snippet = words.slice(startIndex, endIndex).join(' ');

    return snippetStart + snippet + snippetEnd;
};


const searchItems = (query) => {
    return routeMappings
        .filter(({ content }) => content.toLowerCase().includes(query.toLowerCase()))
        .map(({ path, content }) => ({
            path,
            snippet: getSnippetAroundQuery(content, query, 100) //  snippet length
        }));
};
function PageSearchBar() {
    const [searchText, setSearchText] = useState(""); // search input value

    const [searchResults, setSearchResults] = useState([]);
    const navigate = useNavigate();

    const handleSearch = (searchText) => {
        setSearchText(searchText);
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
            style={{ width: 400 }}
            onSearch={handleSearch}
            onSelect={onSearchSelect}
            className="page-search-input"
            placeholder="Search pages..."
            value={searchText}
        >
            {searchResults.map((result, index) => (
                <AutoComplete.Option key={index} value={result.path}>
                    {result.path.split('/').pop()}:     {result.snippet}
                </AutoComplete.Option>
            ))}
        </AutoComplete>
    );
}

export default PageSearchBar;
