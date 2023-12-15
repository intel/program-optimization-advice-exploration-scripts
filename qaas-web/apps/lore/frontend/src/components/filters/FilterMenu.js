import { Dropdown } from 'antd';
import React, { useState } from 'react';
import MenuComponent from './MenuComponent';
import { DownOutlined } from '@ant-design/icons';

export default function FilterMenu({ filterOptions, applyFilter, handleInputChange }) {
    return (
        <Dropdown overlay={<MenuComponent filterOptions={filterOptions} handleInputChange={handleInputChange} handleMenuAction={applyFilter} />}>
            <a className="ant-dropdown-link" onClick={e => e.preventDefault()}>
                Select Filter <DownOutlined />
            </a>
        </Dropdown>
    );
}
