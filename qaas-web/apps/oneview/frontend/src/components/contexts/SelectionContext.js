import React, { createContext, useContext, useState } from 'react';

const SelectionContext = createContext();

export const useSelectionContext = () => useContext(SelectionContext);

export const SelectionProvider = ({ children }) => {
    const [selectedRows, setSelectedRows] = useState([]);


    const handleRowSelection = (event, rowInfo) => {
        console.log(rowInfo)
        setSelectedRows(prevSelectedRows => {
            const selected = event.target.checked;
            const newSelectedRows = selected
                ? [...prevSelectedRows, rowInfo.original]
                : prevSelectedRows.filter(row => row !== rowInfo.original);
            return newSelectedRows;
        });
    }

    return (
        <SelectionContext.Provider value={{ selectedRows, handleRowSelection }}>
            {children}
        </SelectionContext.Provider>
    );
};
