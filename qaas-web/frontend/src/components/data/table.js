import React, { useState } from "react";
import ReactTable from "react-table-6";
import TableSearchBar from "./TableSearchBar";
import "react-table-6/react-table.css";
import '../css/table.css'

function Table({ data, columns, SubComponent, expanded, onExpandedChange, defaultPageSize }) {
    const [filterInput, setFilterInput] = useState("");

    console.log(filterInput)
    const filteredData = filterInput
        ? (() => {
            const [searchText, header] = filterInput.split(" in ");
            const column = columns.find(col => col.Header === header);
            return data.filter(row => {
                const value = typeof column.accessor === 'function' ? column.accessor(row) : row[column.accessor];
                return value && value.toString().toLowerCase().includes(searchText.toLowerCase());
            });
        })()
        : data;

    return (
        <div className="table-container">
            <TableSearchBar
                data={data}
                columns={columns}
                onSearchSelect={(value) => setFilterInput(value)}
            />

            <ReactTable
                data={filteredData}
                columns={columns}
                defaultPageSize={defaultPageSize || 10}
                className="-striped -highlight"
                expanded={expanded}
                onExpandedChange={(newExpanded) => onExpandedChange(newExpanded)}
                SubComponent={SubComponent}
                getTheadThProps={() => {
                    return {
                        className: "wrap-text"
                    };
                }}
            />
        </div>
    );
}

export default Table;