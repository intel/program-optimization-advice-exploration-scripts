import React, { createContext, useContext, useState } from 'react';

const SelectionContext = createContext();

export const useSelectionContext = () => useContext(SelectionContext);

//this context class is for select and select baseline 
export const SelectionProvider = ({ children }) => {
    const [selectedRows, setSelectedRows] = useState([]);
    const [baseline, setBaseline] = useState(null);

    const handleRowSelection = (event, rowInfo) => {
        setSelectedRows(prevSelectedRows => {
            const selected = event.target.checked;
            const newSelectedRows = selected
                ? [...prevSelectedRows, rowInfo.original]
                : prevSelectedRows.filter(row => row !== rowInfo.original);
            return newSelectedRows;
        });
    }
    const handleBaselineSelection = (rowInfo, rowIndex) => {
        setBaseline(prevBaseline => {
            // cannot just user objs to compare
            return JSON.stringify(prevBaseline) === JSON.stringify(rowInfo) ? null : rowInfo;

        });
    };

    return (
        <SelectionContext.Provider value={{ selectedRows, handleRowSelection, baseline, handleBaselineSelection }}>
            {children}
        </SelectionContext.Provider>
    );
};
