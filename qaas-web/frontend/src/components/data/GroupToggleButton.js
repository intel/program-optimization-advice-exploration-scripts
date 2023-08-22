
import React from 'react';
import { TOGGLE_BUTTON_COLOR_SCHEME, APPLICATION_TABLE_COLUMNS } from '../Constants';

const ToggleButton = ({ groupName, label, hiddenChildColumns, toggleGroup, color, columns }) => {
    const areChildColumnsHidden = columns.some(col => hiddenChildColumns.includes(col.id));
    console.log(areChildColumnsHidden)
    return (
        <button
            onClick={() => toggleGroup(groupName)}
            style={{ backgroundColor: color, color: 'black' }}
            className='table-action-button'

        >
            {areChildColumnsHidden ? 'Show' : 'Hide'} {label}
        </button>
    );
};

export const GroupToggleButton = ({ hiddenChildColumns, toggleGroup }) => {

    return (

        <div className="toggle-buttons">
            <div className="toggle-buttons">
                <ToggleButton
                    groupName="time"
                    label="Time"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[0]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "time")?.columns || []}


                />
                <ToggleButton
                    groupName="globalScore"
                    label="Global Score"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[1]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "globalScore")?.columns || []}


                />
                <ToggleButton
                    groupName="speedup"
                    label="Speedup"
                    hiddenChildColumns={hiddenChildColumns}
                    toggleGroup={toggleGroup}
                    color={TOGGLE_BUTTON_COLOR_SCHEME[2]}
                    columns={APPLICATION_TABLE_COLUMNS.find(col => col.groupName === "speedup")?.columns || []}


                />
                <ToggleButton
                    groupName="experimentSummary"
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