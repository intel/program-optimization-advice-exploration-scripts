import React, { useState, useEffect } from "react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

import Table from "./table";
function ApplicationSubTable({ data, workload, program, workload_version }) {

    //will pass specfici loop data
    const handleButtonClick = async (data) => {
        // Call your backend API here and fetch data
        const queryString = new URLSearchParams({ ...data, workload, program, workload_version, loading: 'false' }).toString();

        const newWindow = window.open(`/loop?${queryString}`, "_blank");
        // try {
        //     const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_html_by_timestamp`, { 'timestamp': timestamp })
        //     //send user to new page
        //     newWindow.location.href = "/generated?loading=false";

        // } catch (error) {
        //     console.error('Error fetching data:', error);
        // }

    };


    const columns = [

        {
            Header: 'Action',
            id: 'button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleButtonClick(row._original)}>View Details</button>
                </div>

            ),
            width: 100,
        },
        {
            Header: 'File',
            accessor: 'file'
        },
        {
            Header: 'Function',
            accessor: 'function'
        },
        {
            Header: 'Line',
            accessor: 'line'
        },
        {
            Header: 'Pluto',
            accessor: 'pluto'
        },
        {
            Header: '# of Mutations',
            accessor: 'n_mutations'
        },
    ];

    return (
        <Table
            data={data}
            columns={columns}
            defaultPageSize={10}
        />
    );
}

export default ApplicationSubTable;