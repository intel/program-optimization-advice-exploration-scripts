import React from 'react';
import { Tag } from 'antd';
import '../css/filter.css'
const AppliedFilters = ({ appliedFilters = [], onRemoveFilter }) => (
    <div>
        <h3>Applied Filters</h3>
        <div>
            {[...appliedFilters].map((filter, index) => (
                <Tag
                    key={index}
                    closable
                    onClose={(e) => {
                        // Prevent tag click navigation
                        e.preventDefault();
                        onRemoveFilter(index);
                    }}
                    className='filter-tag'
                >
                    {filter.mode} <span className='emphasize'>{filter.type}</span> {filter.operator} <span className='emphasize'>{filter.value}</span>

                </Tag>
            ))}
        </div>
    </div>
);

export default AppliedFilters;
