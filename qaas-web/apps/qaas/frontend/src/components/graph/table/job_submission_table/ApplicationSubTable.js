import React from "react";
import axios from 'axios';
import Table from "./table";
const ApplicationSubTable = React.memo(({ data }) => {

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


    const columns = [

        {
            Header: 'Action',
            id: 'button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleButtonClick(row.original.run_timestamp)}>See OV Report</button>
                </div>

            ),
            width: 100,
        },
        { Header: 'Timestamp', accessor: 'run_timestamp' },
        { Header: 'MPI Threads', accessor: 'mpi' },
        { Header: 'OMP Threads', accessor: 'omp' },
        { Header: 'GFlops', accessor: 'gflops' },
        { Header: 'Compiler', accessor: 'compiler' },
        { Header: 'Time', accessor: 'time' },
    ];

    return (
        <Table
            data={data}
            columns={columns}
            defaultPageSize={5}
        />
    );
})

export default ApplicationSubTable;