import React, { useState, useEffect, useMemo } from 'react';
import Table from './table';
import '../../../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';

const ApplicationTable = React.memo(({ data }) => {


    const handleBestCompilersComparisonButtonClick = async (timestamp) => {
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/generate_ov_best_compilers_comparison`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:', error);
        }

    };
    const handleBestCompilerVSOriginalButtonClick = async (timestamp) => {
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/generate_ov_best_compiler_vs_orig`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:', error);
        }

    };


    const fetchSubTableData = async (qaas_timestamp) => {
        try {
            console.log("timestamp", qaas_timestamp)
            const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_job_submission_subtable_data`, { 'qaas_timestamp': qaas_timestamp });
            return response.data;
        } catch (error) {
            console.error('Error fetching sub-table data:', error);
            return [];
        }
    };
    // add color to colums
    const columns = [
        {
            Header: 'Action Compilers Comparison',
            id: 'comparison-best-compilers-comparison',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleBestCompilersComparisonButtonClick(row.original.qaas_timestamp)}>See OV Best Compilers Comparison</button>
                </div>

            ),
        },
        {
            Header: 'Action Best Compiler VS Orig',
            id: 'comparison-best-compiler-vs-orig',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleBestCompilerVSOriginalButtonClick(row.original.qaas_timestamp)}>See OV Best Compiler vs Original Comparison</button>
                </div>

            ),
        },
        { Header: 'Application', accessor: 'app_name', },
        { Header: 'Timestamp', accessor: 'qaas_timestamp' },
        { Header: 'Machine', accessor: 'machine' },
        { Header: 'Archicture', accessor: 'arch' },
        { Header: 'Best Compiler', accessor: 'best_compiler' },
        { Header: 'Best Time', accessor: 'best_time' },

    ];;



    return (
        <div >

            <div className="center">
                <Table
                    data={data}
                    columns={columns}
                    defaultPageSize={10}
                    fetchSubTableData={fetchSubTableData}
                    SubTableComponent={ApplicationSubTable}
                />
            </div>
        </div>
    );
})


export default ApplicationTable;