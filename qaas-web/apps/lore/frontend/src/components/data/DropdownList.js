import React, { useState } from 'react';
import '../css/loop.css';
import AccordionComponent from './AccordionComponent';

const DropdownList = ({ data, titleKey, children }) => {
    return (
        <div>
            {Object.entries(data).map(([key, value], index) => (
                <AccordionComponent title={titleKey(key, value)} key={index}>
                    {children(key, value)}
                </AccordionComponent>
            ))}
        </div>
    );
};

export default DropdownList;
