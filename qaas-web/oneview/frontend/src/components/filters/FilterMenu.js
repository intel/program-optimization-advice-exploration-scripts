import React from 'react';
import { Collapse, Select, Input, Space, Checkbox } from 'antd';

const { Panel } = Collapse;

export default function FilterMenu({ category, filterOptions, handleInputChange }) {

    const renderOperatorSelector = (category, filterType) => {
        if (filterOptions[filterType].operator === 'like') {
            return <p>Like</p>
        }
        return (
            <Select
                defaultValue={filterOptions[filterType].operator}
                onChange={(operator) => handleInputChange(category, filterType, 'operator', operator)}
            >
                <Select.Option value="less than">Less Than</Select.Option>
                <Select.Option value="bigger than">Bigger Than</Select.Option>
                <Select.Option value="equal to">Equal To</Select.Option>
            </Select>
        )
    }

    const renderModeSelector = (category, filterType) => {
        if (category !== 'Global') {
            return (
                <Select
                    defaultValue={filterOptions[filterType].mode}
                    onChange={(mode) => handleInputChange(category, filterType, 'mode', mode)}
                >
                    <Select.Option value="all">All</Select.Option>
                    <Select.Option value="any">Any</Select.Option>
                </Select>
            )
        }
    }

    return (
        <Collapse className="panel-container">
            <Panel header={category} key={category} className="panel">
                {Object.keys(filterOptions).map((filterType) => (
                    <Space key={filterType} className="space-container" >
                        <Checkbox
                            onChange={(e) => handleInputChange(category, filterType, 'selected', e.target.checked)}
                        />
                        <span>{filterType}</span>
                        {renderOperatorSelector(category, filterType)}
                        <Input
                            value={filterOptions[filterType].value}
                            onChange={(e) => handleInputChange(category, filterType, 'value', e.target.value)}
                        />
                        {renderModeSelector(category, filterType)}
                    </Space>
                ))}
            </Panel>
        </Collapse>
    );
}
