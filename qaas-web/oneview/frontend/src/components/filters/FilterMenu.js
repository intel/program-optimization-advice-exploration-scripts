import React from 'react';
import { Collapse, Select, Input, Space, Checkbox } from 'antd';

const { Panel } = Collapse;

export default function FilterMenu({ category, filterOptions, handleInputChange, resetFilters }) {
    const renderOperatorSelector = (category, subCategory, filterType) => {
        if (filterOptions[subCategory][filterType].operator === 'like') {
            return <p>Like</p>
        }
        if (filterOptions[subCategory][filterType].operator === 'is') {
            return <p>is</p>
        }
        return (
            <Select
                defaultValue={filterOptions[subCategory][filterType].operator}
                onChange={(selectedChoice) => {
                    handleInputChange(category, subCategory, filterType, 'value', selectedChoice);
                }}
            >
                <Select.Option value="less than">Less Than</Select.Option>
                <Select.Option value="bigger than">Bigger Than</Select.Option>
                <Select.Option value="equal to">Equal To</Select.Option>
            </Select>
        )
    }
    const renderChoicesDropdown = (category, subCategory, filterType) => {
        if (filterOptions[subCategory][filterType].operator === 'is') {
            return (
                <Select
                    placeholder="Select"
                    value={filterOptions[subCategory][filterType].value || "Select"}
                    onChange={(selectedChoice) => handleInputChange(category, subCategory, filterType, 'value', selectedChoice)}


                >

                    {filterOptions[subCategory][filterType].choices.map(choice => (
                        <Select.Option value={choice}>{choice}</Select.Option>
                    ))}
                </Select>
            );
        }
    }

    const renderModeSelector = (category, subCategory, filterType) => {
        if (category !== 'Global') {
            return (
                <Select
                    defaultValue={filterOptions[subCategory][filterType].mode}
                    onChange={(mode) => handleInputChange(category, subCategory, filterType, 'mode', mode)}
                >
                    <Select.Option value="all">All</Select.Option>
                    <Select.Option value="any">Any</Select.Option>
                </Select>
            )
        }
    }
    const subCategories = filterOptions;
    return (
        <Collapse className="panel-container">
            <Panel header={category} key={category} className="panel">
                {Object.keys(subCategories).map((subCategory) => (
                    // each subcategory
                    <Collapse key={subCategory}>
                        <Panel header={subCategory} key={subCategory}>
                            {Object.keys(subCategories[subCategory]).map((filterType) => (
                                <Space key={filterType} className="space-container">
                                    <Checkbox
                                        checked={!resetFilters && filterOptions[subCategory][filterType].selected}

                                        onChange={(e) => handleInputChange(category, subCategory, filterType, 'selected', e.target.checked)}
                                    />
                                    <span>{filterType}</span>
                                    {renderOperatorSelector(category, subCategory, filterType)}
                                    {/* conditionally render a input or selection based on the opertaor */}
                                    {filterOptions[subCategory][filterType].operator === 'is' ?
                                        renderChoicesDropdown(category, subCategory, filterType) :
                                        <Input
                                            value={subCategories[subCategory][filterType].value}
                                            onChange={(e) => handleInputChange(category, subCategory, filterType, 'value', e.target.value)}
                                        />
                                    }
                                    {renderModeSelector(category, subCategory, filterType)}
                                </Space>
                            ))}
                        </Panel>
                    </Collapse>
                ))}
            </Panel>
        </Collapse>
    );
}
