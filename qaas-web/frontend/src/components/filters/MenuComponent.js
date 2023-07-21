import { Menu, Input } from 'antd';
import React, { useState } from 'react';
const { SubMenu } = Menu;
import '../css/filter.css'

export default function MenuComponent({ filterOptions, handleInputChange, handleMenuAction }) {
    return (
        <Menu>
            {Object.keys(filterOptions).map((filterType) => (
                <SubMenu key={filterType} title={filterType}>
                    {Object.keys(filterOptions[filterType]).map((operator) => (
                        <Menu.Item key={`${filterType}-${operator}`}>
                            <div>
                                {operator}
                                <Input
                                    type="text"
                                    value={filterOptions[filterType][operator]}
                                    onClick={(e) => e.stopPropagation()}
                                    onChange={(e) => handleInputChange(filterType, operator, e.target.value)}
                                />
                                <button className='button button-text' onClick={() => handleMenuAction(filterType, operator)}>
                                    Apply
                                </button>
                            </div>
                        </Menu.Item>
                    ))}
                </SubMenu>
            ))}
        </Menu>
    );
}
