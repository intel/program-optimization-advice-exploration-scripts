
import React, { useState, useEffect } from 'react';
import { TOGGLE_BUTTON_COLOR_SCHEME, APPLICATION_TABLE_COLUMNS } from '../Constants';
import '../css/table.css'
const ToggleButton = ({ groupName, label, hiddenChildColumns, toggleGroup, color, columns }) => {
    const [isGroupExpanded, setIsGroupExpanded] = useState(false);
    const handleToggleGroup = () => {
        toggleGroup(groupName);
        setIsGroupExpanded(!isGroupExpanded);
    };
    const buttonText = isGroupExpanded ? 'Hide' : 'Show';
    return (
        <button
            onClick={handleToggleGroup}
            style={{ backgroundColor: color }}
            className='table-action-button'
        >
            {buttonText} {label}
        </button>
    );
};

export const GroupToggleButton = ({ hiddenChildColumns, toggleGroup }) => {

    return (

        <div className="toggle-buttons">
            <div className="toggle-buttons">
                <ToggleButton
                    groupName="runInfo"
                    label="Run Info"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[0]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "runInfo")?.columns || []}


                />
                <ToggleButton
                    groupName="time"
                    label="Time"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[1]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "time")?.columns || []}
                />


                {/* <ToggleButton
                    groupName="globalScore"
                    label="Global Score"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[1]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "globalScore")?.columns || []}


                /> */}
                <ToggleButton
                    groupName="speedup"
                    label="Speedup"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[2]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "speedup")?.columns || []}


                />
                <ToggleButton
                    groupName="experiment_summary"
                    label="Experiment Summary"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[3]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "experimentSummary")?.columns || []}


                />
            </div>
        </div>


    );

}