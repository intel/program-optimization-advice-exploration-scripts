import React, { useEffect, useState } from "react";
import { useTable, useExpanded, usePagination } from "react-table";
import '../../../css/table.css';
import { formatValue } from "../../../Constants";
function NestedTable({ columns, data, hiddenColumns, columnFilters, setColumnFilters, fetchSubTableData, SubTableComponent }) {
    //keep track loaded data for each row
    const [loadedData, setLoadedData] = useState({});
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
        state: { pageIndex, pageSize, expanded },
        setHiddenColumns,
        toggleRowExpanded,
        visibleColumns,
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

    //called when expand finger button is clicked
    const handleRowExpand = async (row) => {
        //if row is expanded
        const isExpanded = !!expanded[row.id];
        // toggle row first
        toggleRowExpanded(row.id, !isExpanded);

        // if row is being expanded and data is not already loaded
        if (!expanded[row.id] && !loadedData[row.id]) {
            try {
                const subData = await fetchSubTableData(row.original['qaas_timestamp']);
                setLoadedData(prev => ({ ...prev, [row.id]: subData }));
            } catch (error) {
                console.error('Error fetching sub-table data:', error);
            }
        }
    };

    const renderExpandedRowContent = (rowId) => {
        const rowData = loadedData[rowId];
        if (!rowData) {
            return <div>Loading...</div>;
        }

        return <SubTableComponent data={rowData} />;

    };




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
                            {SubTableComponent && <th>Show All Compiler Speedups</th>}   {/* conditionally add extra header cell for the button */}
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
                                                console.log("value", value)
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
                                                <option value={value}>{formatValue(value)}</option>
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
                                    {/* include the expand/collapse button with handleRowExpand */}
                                    {SubTableComponent && (
                                        <td>
                                            <span {...row.getToggleRowExpandedProps()} onClick={() => handleRowExpand(row)} >
                                                {row.isExpanded ? '👇' : '👉'}
                                            </span>
                                        </td>
                                    )}
                                    {/* render and format the value  */}
                                    {row.cells.map((cell) => {
                                        //title is for tool tip
                                        const isActionColumn = cell.column.isAction;


                                        const formattedValue = formatValue(cell.value);
                                        return (
                                            <td title={cell.value} {...cell.getCellProps()}>
                                                {isActionColumn ? cell.render('Cell') : formattedValue}
                                            </td>
                                        );
                                    })}
                                </tr>
                                {expanded[row.id] && (
                                    <tr>
                                        <td colSpan={visibleColumns.length + 1}>
                                            {renderExpandedRowContent(row.id)}
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

export default NestedTable;
