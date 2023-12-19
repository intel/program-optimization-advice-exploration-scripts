import React, { useEffect } from "react";
import { useTable, useExpanded, usePagination } from "react-table";
import '../css/table.css';
import { useSearchFilters } from "../hooks/useSearchFilters";
function CustomReactTable({ columns, data, SubComponent, hiddenColumns, columnFilters, setColumnFilters }) {
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
        setHiddenColumns,
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
    useEffect(() => {
        setHiddenColumns(hiddenColumns || []);  // set the hidden columns whenever the prop changes
    }, [hiddenColumns, setHiddenColumns]);


    //not empty values will be shown in select
    function uniqueValuesForColumn(columnId, data) {
        const values = new Set(data.map(row => row[columnId]).filter(Boolean));
        return [...values];
    }


    return (
        <div className="table-container">

            {/* componet to pagniation and show number of lines */}
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
                                    {/* drop down box to conditionally get a list of values and when user click it will filter the rows */}
                                    {
                                        uniqueValuesForColumn(column.id, data).length > 0 &&
                                        <select
                                            onChange={e => {
                                                const value = e.target.value;
                                                if (value === "") {
                                                    const newFilters = { ...columnFilters };
                                                    delete newFilters[column.id];
                                                    setColumnFilters(newFilters);
                                                } else {
                                                    setColumnFilters({ ...columnFilters, [column.id]: value });
                                                }
                                            }}
                                            className="select-dropdown"
                                        >
                                            <option value="select" hidden>Select</option>
                                            <option value="">All</option>
                                            {uniqueValuesForColumn(column.id, data).map(value => (
                                                <option value={value}>{value}</option>
                                            ))}
                                        </select>
                                    }
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
                                {console.log("expanded", row.isExpanded)}
                                {row.isExpanded ? (
                                    <tr>
                                        <td colSpan={columns.length + 1}>
                                            <SubComponent row={row} />
                                        </td>
                                    </tr>
                                ) : null}
                            </React.Fragment>
                        );
                    })}
                </tbody>

            </table>


        </div>

    );
}

export default CustomReactTable;
