import React, { useState, useEffect, useCallback } from "react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Table from "./table";
import { useSelectionContext } from "../contexts/SelectionContext";
// const ApplicationSubTable = React.memo(({ data, selectedRows, baseline, setBaseline, handleRowSelection }) => {
const ApplicationSubTable = React.memo(({ data, baseline, setBaseline }) => {
    const { selectedRows, handleRowSelection } = useSelectionContext();

    const navigate = useNavigate();
    const handleButtonClick = async (timestamp) => {
        // Call your backend API here and fetch data
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_html_by_timestamp`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:', error);
        }

    };

    const handleBaselineRowSelection = (event, rowInfo) => {
        if (rowInfo) {
            const selected = event.target.checked;

            if (selected) {
                setBaseline(rowInfo.original);
            } else {
                setBaseline(null);
            }
        }
    };
    const columns = [
        {
            Header: 'Select',
            id: 'selection',
            Cell: ({ row }) => (
                <div className="table-action">
                    <input
                        type="checkbox"
                        checked={selectedRows.some(selectedRow => selectedRow === row.original)}
                        onChange={(e) => handleRowSelection(e, row)}
                    />
                </div>
            ),
            width: 50,

        },
        {
            Header: 'Select Baseline',
            id: 'selection_baseline',
            Cell: ({ row }) => (
                <div className="table-action">
                    <input
                        type="checkbox"
                        checked={baseline === row.original}
                        onChange={(e) => handleBaselineRowSelection(e, row)}
                    />
                </div>
            ),
            width: 100,

        },
        {
            Header: 'Action',
            id: 'button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleButtonClick(row.original.timestamp)}>View Details</button>
                </div>

            ),
            width: 100,
        },
        {
            Header: 'Timestamp',
            accessor: 'timestamp'
        },
        {
            Header: 'Machine',
            accessor: 'machine'
        },
        {
            Header: 'Data',
            accessor: 'data'
        },
    ];
    console.log("subtable got rendered")

    return (
        <Table
            data={data}
            columns={columns}
            defaultPageSize={5}
        />
    );
})

export default ApplicationSubTable;