import '../css/filter.css'
// import { Menu, Input } from 'antd';
// import React, { useState } from 'react';
// const { SubMenu } = Menu;

// export default function MenuComponent({ filterOptions, handleInputChange, handleMenuAction }) {

//     const handleModeChange = (filterType, operator, mode, event) => {
//         event.stopPropagation(); // prevent event from bubbling up to parent elements
//         handleInputChange(filterType, operator, filterOptions[filterType][operator].value, mode);
//     };

//     return (
//         <Menu>
//             {Object.keys(filterOptions).map((filterType) => (
//                 <SubMenu key={filterType} title={filterType}>
//                     {Object.keys(filterOptions[filterType]).map((operator) => (
//                         <Menu.Item key={`${filterType}-${operator}`}>
//                             <div>
//                                 {operator}
//                                 <Input
//                                     type="text"
//                                     value={filterOptions[filterType][operator].value}
//                                     onClick={(e) => e.stopPropagation()}
//                                     onChange={(e) => handleInputChange(filterType, operator, e.target.value, filterOptions[filterType][operator].mode)}
//                                 />
//                                 <div>
//                                     <button className='button button-text' onClick={(e) => handleModeChange(filterType, operator, 'all', e)}>All</button>
//                                     <button className='button button-text' onClick={(e) => handleModeChange(filterType, operator, 'any', e)}>Any</button>
//                                 </div>
//                                 <button className='button button-text' onClick={() => handleMenuAction(filterType, operator)}>
//                                     Apply
//                                 </button>
//                             </div>
//                         </Menu.Item>
//                     ))}
//                 </SubMenu>
//             ))}
//         </Menu>
//     );
// }
import { Menu, Input } from 'antd';
import React, { useState } from 'react';
const { SubMenu } = Menu;

export default function MenuComponent({ filterOptions, handleInputChange, handleMenuAction }) {
    const [activeButton, setActiveButton] = useState({});

    const handleModeChange = (filterType, operator, mode, event) => {
        event.stopPropagation(); // prevent event from bubbling up to parent elements
        handleInputChange(filterType, operator, filterOptions[filterType][operator].value, mode);
        setActiveButton({ filterType, operator, mode }); // set the active button
    };

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
                                    value={filterOptions[filterType][operator].value}
                                    onClick={(e) => e.stopPropagation()}
                                    onChange={(e) => handleInputChange(filterType, operator, e.target.value, filterOptions[filterType][operator].mode)}
                                />
                                <button
                                    className={`button button-text ${activeButton.filterType === filterType && activeButton.operator === operator && activeButton.mode === 'all' ? 'active' : ''}`}
                                    onClick={(e) => handleModeChange(filterType, operator, 'all', e)}
                                >
                                    All
                                </button>
                                <button
                                    className={`button button-text ${activeButton.filterType === filterType && activeButton.operator === operator && activeButton.mode === 'any' ? 'active' : ''}`}
                                    onClick={(e) => handleModeChange(filterType, operator, 'any', e)}
                                >
                                    Any
                                </button>
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
