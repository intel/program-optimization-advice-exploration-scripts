import React, { useState } from "react";
// import ReactTable from "react-table-6";

// import "react-table-6/react-table.css";
import '../css/table.css'
function Table({ data, columns, SubComponent, expanded, onExpandedChange, defaultPageSize, onPageChange, onPageSizeChange, numPages }) {
    const [filterInput, setFilterInput] = useState("");
    const handleFilterChange = (e) => {
        const value = e.target.value || undefined;
        setFilterInput(value);
    };
    const filteredData = filterInput
        ? data.filter((row) =>
            Object.values(row).some(
                (cell) =>
                    cell !== undefined &&
                    cell.toString().toLowerCase().includes(filterInput.toLowerCase())
            )
        )
        : data;
    return (
        <div className="table-container">
            <input
                value={filterInput}
                onChange={handleFilterChange}
                placeholder={"Search..."}
                className="table-search-input"
            />
            {/* <ReactTable
                data={filteredData}
                columns={columns}
                defaultPageSize={defaultPageSize || 10}
                className="-striped -highlight"
                expanded={expanded}
                onExpandedChange={(newExpanded) => onExpandedChange(newExpanded)}
                SubComponent={SubComponent}
                onPageChange={onPageChange}
                onPageSizeChange={onPageSizeChange}
                pages={numPages}


            /> */}
        </div>
    );
}

export default Table;