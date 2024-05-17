import React from "react";
import { useTable } from "react-table";
import '../../css/table.css';

function SingleRowTable({ columns, data }) {
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

    // only one row of data
    const firstRow = rows[0];
    prepareRow(firstRow);

    return (
        <div className="table-container">
            <table {...getTableProps()}>
                <tbody {...getTableBodyProps()}>

                    {firstRow.cells.map((cell, i) => {
                        //  two cells per row
                        if (i % 2 === 0) {
                            const nextCell = firstRow.cells[i + 1];
                            return (
                                <tr key={i}>
                                    <th {...cell.getCellProps()} className="custom-header">
                                        {cell.column.render('Header')}
                                    </th>
                                    <td {...cell.getCellProps()}>
                                        {cell.render('Cell')}
                                    </td>
                                    {nextCell && (
                                        <>
                                            <th {...nextCell.getCellProps()} className="custom-header">
                                                {nextCell.column.render('Header')}
                                            </th>
                                            <td {...nextCell.getCellProps()}>
                                                {nextCell.render('Cell')}
                                            </td>
                                        </>
                                    )}
                                </tr>
                            );
                        }
                        return null; // for odd cells, return null because they are already rendered
                    })}
                </tbody>
            </table>
        </div>
    );
}

export default SingleRowTable;
