import React, { useState } from "react";
import ReactTable from "react-table-6";
import TableSearchBar from "./TableSearchBar";
import "react-table-6/react-table.css";
import '../css/table.css'
import { useMemo } from 'react';

function Table({ data, columns, SubComponent, expanded, onExpandedChange, defaultPageSize }) {
    const [filterInput, setFilterInput] = useState("");

    const filteredData = filterInput ? (() => {
        const [searchText, header] = filterInput.split(" in ");
        const flattenedCols = flattenColumns(columns);

        const matchingColumns = header === 'All' ? flattenedCols : [flattenedCols.find(col => col.Header === header)];

        return data.filter(row => {
            return matchingColumns.some(column => {
                const value = typeof column.accessor === 'function' ? column.accessor(row) : row[column.accessor];
                return value && value.toString().toLowerCase().includes(searchText.toLowerCase());
            });
        });
    })() : data;


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

    return (
        <div className="table-container">
            <TableSearchBar
                data={data}
                columns={flattenedCols}
                onSearchSelect={(value) => setFilterInput(value)}
            />

            <ReactTable
                data={filteredData}
                columns={columns}
                defaultPageSize={defaultPageSize || 10}
                className="-striped -highlight ReactTable"
                expanded={expanded}
                onExpandedChange={(newExpanded) => onExpandedChange(newExpanded)}
                SubComponent={SubComponent}

                getTheadThProps={(state, rowInfo, column) => {
                    return {
                        style: column.color ? { backgroundColor: column.color } : {},
                        className: "wrap-text"
                    };
                }}
            />
        </div>
    );
}

export default Table;