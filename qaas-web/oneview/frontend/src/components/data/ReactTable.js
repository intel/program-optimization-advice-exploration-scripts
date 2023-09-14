import React, { useState, useCallback } from "react";
import { useTable, useExpanded } from "react-table";
import '../css/table.css'

function ReactTable({ columns, data, SubComponent, onExpandedChange }) {
    const [localExpanded, setLocalExpanded] = useState({});

    const toggleRowExpand = useCallback((rowId) => {
        setLocalExpanded(prevState => {
            const newState = { ...prevState };
            if (newState[rowId]) {
                delete newState[rowId];
            } else {
                newState[rowId] = true;
            }
            onExpandedChange(newState);  // Notify the parent component
            return newState;
        });
    }, [onExpandedChange]);

    const adjustedColumns = [
        {
            Header: 'Expand',
            id: 'expander',
            Cell: ({ row }) => (
                <button onClick={() => toggleRowExpand(row.id)}>
                    {localExpanded[row.id] ? "Collapse" : "Expand"}
                </button>
            )
        },
        ...columns
    ];



    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow
    } = useTable({
        columns: adjustedColumns,
        data,
        initialState: { expanded: localExpanded },  // Set the initial expanded state
    }, useExpanded);  // Use the useExpanded hook



    return (
        <table {...getTableProps()}>
            <thead>
                {headerGroups.map(headerGroup => (
                    <tr {...headerGroup.getHeaderGroupProps()}>
                        {headerGroup.headers.map(column => (
                            <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody {...getTableBodyProps()}>
                {rows.map(row => {
                    prepareRow(row);
                    return (
                        <React.Fragment key={row.id}>
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => (
                                    <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                                ))}
                            </tr>
                            {localExpanded[row.id] && (
                                <tr>
                                    <td colSpan={columns.length + 1}>
                                        {/* {SubComponent(row)} */}
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    );
                })}
            </tbody>
        </table>
    );
}

export default ReactTable;
