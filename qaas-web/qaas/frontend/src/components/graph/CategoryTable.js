import React from 'react';
import { useTable } from 'react-table';

const CategoryTable = ({ columns, data }) => {
    const tableInstance = useTable({ columns, data });

    const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = tableInstance;

    return (
        <table {...getTableProps()} style={{ border: '1px solid black' }}>
            <thead>
                {headerGroups.map((headerGroup) => (
                    <tr {...headerGroup.getHeaderGroupProps()} style={{ backgroundColor: 'lightgray' }}>
                        {headerGroup.headers.map((column) => (
                            <th {...column.getHeaderProps()} style={{ padding: '10px', border: '1px solid black' }}>
                                {column.render('Header')}
                            </th>
                        ))}
                    </tr>
                ))}
            </thead>
            <tbody {...getTableBodyProps()}>
                {rows.map((row) => {
                    prepareRow(row);
                    return (
                        <tr {...row.getRowProps()}>
                            {row.cells.map((cell) => (
                                <td
                                    {...cell.getCellProps()}
                                    style={{ padding: '10px', border: '1px solid black' }}
                                    dangerouslySetInnerHTML={{
                                        __html: highlightText(cell.value, 'Value 2'),
                                    }}
                                />
                            ))}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

// Helper function to highlight text within a cell
const highlightText = (text, highlight) => {
    const regex = new RegExp(`(${highlight})`, 'gi');
    return text.replace(regex, '<span style="background-color: yellow;">$1</span>');
};

export default CategoryTable;
