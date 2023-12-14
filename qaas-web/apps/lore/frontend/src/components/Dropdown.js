import React, { useState } from 'react';

const Dropdown = ({ options }) => {
    const [selectedOption, setSelectedOption] = useState(options[0]);

    const handleSelect = (event) => {
        setSelectedOption(event.target.value);
    };

    return (
        <select className="dropdown" value={selectedOption} onChange={handleSelect}>
            {options.map((option, index) => (
                <option key={index} value={option}>
                    {option}
                </option>
            ))}
        </select>
    );
};

export default Dropdown;