import React, { useState, useEffect, useMemo } from 'react';
import Table from './table';
import '../../../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';

const ApplicationTable = React.memo(({ data }) => {


    const handleButtonClick = async (timestamp) => {
        // Call your backend API here and fetch data
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_comparison_html_by_timestamp`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:', error);
        }

    };
    // add color to colums
    const columns = [
        {
            Header: 'Action',
            id: 'comparison-report-button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleButtonClick(row.original.qaas_timestamp)}>See OV Comparison Report</button>
                </div>

            ),
        },
        { Header: 'Application', accessor: 'app_name', },
        { Header: 'Timestamp', accessor: 'qaas_timestamp' },
        { Header: 'Archicture', accessor: 'arch' },
        { Header: 'Model', accessor: 'model' },
    ];;


    const renderSubComponent = (row) => {
        return (
            <ApplicationSubTable data={row.row['run_data']} />
        );
    };




    return (
        <div >

            <div className="center">
                <Table
                    data={data}
                    columns={columns}
                    SubComponent={(row) => renderSubComponent(row)}
                    defaultPageSize={10}
                />
            </div>
        </div>
    );
})


export default ApplicationTable;