import React from "react";
import { useTable, useExpanded, usePagination } from "react-table";
import '../css/table.css';

function CustomReactTable({ columns, data, SubComponent }) {
    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        prepareRow,
        //for pagnination
        page, // instead of 'rows'
        canPreviousPage,
        canNextPage,
        pageOptions,
        pageCount,
        gotoPage,
        nextPage,
        previousPage,
        setPageSize,
        state: { pageIndex, pageSize },
    } = useTable(
        {
            columns,
            autoResetHiddenColumns: false,
            data,
            initialState: { pageIndex: 0 },

        },
        useExpanded,
        usePagination

    );
    return (
        <div className="table-container">


            <table {...getTableProps()}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {SubComponent && <th></th>}  {/* conditionally add extra header cell for the button */}
                            {/* header inherit color set in constant */}
                            {headerGroup.headers.map(column => (
                                <th
                                    {...column.getHeaderProps()}
                                    style={{ backgroundColor: column.color ? column.color : 'inherit' }}
                                >
                                    {column.render('Header')}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>

                <tbody {...getTableBodyProps()}>
                    {page.map((row, i) => {
                        prepareRow(row);
                        return (
                            <React.Fragment key={i}>
                                <tr {...row.getRowProps()}>
                                    {SubComponent && (
                                        <td>
                                            <span {...row.getToggleRowExpandedProps()}>
                                                {row.isExpanded ? '👇' : '👉'}
                                            </span>
                                        </td>
                                    )}
                                    {row.cells.map((cell) => {
                                        //title is for tool tip
                                        return (
                                            <td title={cell.value} {...cell.getCellProps()}>
                                                {cell.render('Cell')}
                                            </td>
                                        );
                                    })}

                                </tr>
                                {row.isExpanded ? (
                                    <tr>
                                        <td colSpan={columns.length + 1}>
                                            {console.log("Expanded row data:", row)}

                                            <SubComponent row={row} />
                                        </td>
                                    </tr>
                                ) : null}
                            </React.Fragment>
                        );
                    })}
                </tbody>

            </table>
            <div>

                <button onClick={() => previousPage()} disabled={!canPreviousPage}>
                    {'<'}
                </button>{' '}
                <button onClick={() => nextPage()} disabled={!canNextPage}>
                    {'>'}
                </button>{' '}

                <span>
                    Page{' '}
                    <strong>
                        {pageIndex + 1} of {pageOptions.length}
                    </strong>{' '}
                </span>

                <select
                    value={pageSize}
                    onChange={e => {
                        setPageSize(Number(e.target.value));
                    }}
                >
                    {[10, 20, 30, 40, 50].map(pageSize => (
                        <option key={pageSize} value={pageSize}>
                            Show {pageSize}
                        </option>
                    ))}
                </select>
            </div>

        </div>

    );
}

export default CustomReactTable;
