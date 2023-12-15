import React from 'react';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';

const TooltipComponent = ({ id, children, content }) => {
    return (
        <>
            <span className='tooltip-trigger' data-tooltip-id={id}>
                {children}
            </span>
            <Tooltip className='tooltip-box' id={id}>
                {content}
            </Tooltip>
        </>
    );
};

export default TooltipComponent;
