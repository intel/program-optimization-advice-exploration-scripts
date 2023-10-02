import React from "react";
import { useTable } from "react-table";
import '../css/table.css';

function CustomReactTable({ columns, data, SubComponent, expanded, onExpandedChange }) {
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow
    } = useTable({
        columns,
        data
    });

    const toggleRow = (rowId) => {
        const newExpanded = { ...expanded };
        newExpanded[rowId] = !newExpanded[rowId];
        onExpandedChange(newExpanded);  // Update the parent component
    };

    return (
        <div className="table-container">

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
                    {rows.map((row, i) => {
                        prepareRow(row);
                        return (
                            <React.Fragment key={i}>
                                <tr {...row.getRowProps()}>
                                    {row.cells.map((cell) => {
                                        return <td {...cell.getCellProps()}>{cell.render("Cell")}</td>;
                                    })}
                                </tr>
                                {expanded[row.id] && (
                                    <tr>
                                        <td colSpan={columns.length}>
                                            <SubComponent row={row} />
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        );
                    })}
                </tbody>
            </table>
        </div>

    );
}

export default CustomReactTable;
