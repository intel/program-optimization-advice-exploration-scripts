import React, { useState, useEffect } from 'react';
import { Menu, Select, Checkbox } from 'antd';
import { AppstoreOutlined, DownOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { updateFilterSelection } from './FilterConstant';
const { SubMenu } = Menu;
import { resetFiltersRecursive } from './FilterConstant';
const { Option } = Select;
const FilterMenu = ({ selectedFilters, setSelectedFilters, applyFilters }) => {
    const [shouldApplyFilters, setShouldApplyFilters] = useState(false);


    //set the state whne clicked
    const onSelectionChange = (item, isChecked) => {
        const newFilters = updateFilterSelection(selectedFilters, item.id, isChecked);
        setSelectedFilters(newFilters);

    };

    const resetFiltersHandler = () => {
        const resetState = resetFiltersRecursive(selectedFilters);
        setSelectedFilters(resetState);
        setShouldApplyFilters(true)

    };

    useEffect(() => {
        if (shouldApplyFilters) {
            applyFilters();
            setShouldApplyFilters(false); // apply reset
        }
    }, [shouldApplyFilters]);



    //resursive call to render the selections
    const renderMenuItems = (items) => {
        return items.map((item, index) => {
            if (item.children) {
                return (
                    <SubMenu key={index} title={item.text}  >
                        {renderMenuItems(item.children)}
                    </SubMenu>
                );
            } else {
                return (
                    <Menu.Item key={item.path} >
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <Checkbox
                                checked={item.selected}
                                onChange={(e) => onSelectionChange(item, e.target.checked)}
                            />
                            <span>{item.text}</span>


                        </div>
                    </Menu.Item>
                );
            }
        });
    };

    return (
        <div >
            <div className="filter-menu-container">
                {selectedFilters.map((filterCategory, index) => (
                    <div className="filter-box" key={index} style={{ marginBottom: '16px' }}>
                        {filterCategory.text}
                        <Menu
                            mode="inline"
                            title={filterCategory.text}
                        >
                            {renderMenuItems(filterCategory.children)}
                        </Menu>
                    </div>
                ))}
            </div>
            <button className='default-button' onClick={applyFilters}>Filter</button>
            <button className='default-button' onClick={resetFiltersHandler}>Reset</button>
        </div>
    );
};

export default FilterMenu;
