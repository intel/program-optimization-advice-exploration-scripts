import React, { useEffect } from "react";
import { useTable } from "react-table";
import '../../css/table.css';
function CustomReactTable({ columns, data, getRowProps, getCellProps }) {
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
    } = useTable({
        columns,
        data,
    });


    return (
        <div className="table-container">


            <table {...getTableProps()}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th
                                    {...column.getHeaderProps()}
                                    className="custom-header"
                                >
                                    {column.render('Header')}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>

                <tbody {...getTableBodyProps()}>
                    {rows.map((row, i) => {
                        prepareRow(row);
                        return (
                            // give entire row some props
                            <tr {...row.getRowProps(getRowProps ? getRowProps(row) : {})} key={i}>
                                {/* give cell some props */}
                                {row.cells.map((cell) => {
                                    return (
                                        <td
                                            {...cell.getCellProps(getCellProps ? getCellProps(cell) : {})}
                                            key={cell.column.id}
                                        >
                                            {cell.render('Cell')}
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>

            </table>


        </div>

    );
}

export default CustomReactTable;
