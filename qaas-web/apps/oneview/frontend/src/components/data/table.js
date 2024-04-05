import React, { useState } from "react";
import TableSearchBar from "./TableSearchBar";
import '../css/table.css'
import { useMemo } from 'react';
import CustomReactTable from "./CustomReactTable";
import { useSearchFilters } from "../hooks/useSearchFilters";
function Table({ data, columns, SubComponent, defaultPageSize, hiddenColumns }) {

    const [filterInput, setFilterInput] = useState("");
    const { filteredData, setColumnFilters, columnFilters } = useSearchFilters(data);

    //the columns are now nested
    function flattenColumns(columns) {
        return columns.reduce((acc, column) => {
            if (column.columns) {
                return acc.concat(flattenColumns(column.columns).map(subCol => ({
                    ...subCol,
                    color: column.color || subCol.color // If the parent column has a color, give it to child 
                })));
            } else {

                return acc.concat(column);
            }
        }, []);
    }
    const flattenedCols = useMemo(() => flattenColumns(columns), [columns]);
    // console.log("Rendering table with columns:", JSON.stringify(columns, null, 2));

    return (
        <div >
            <TableSearchBar
                data={data}
                columns={flattenedCols}
                onSearchSelect={(value) => setFilterInput(value)}
            />
            <div className="table-container">
                <CustomReactTable
                    columns={columns}
                    data={filteredData}
                    hiddenColumns={hiddenColumns}

                    SubComponent={SubComponent}
                    setColumnFilters={setColumnFilters}
                    columnFilters={columnFilters}
                />
            </div>
        </div>
    );
}

export default Table;