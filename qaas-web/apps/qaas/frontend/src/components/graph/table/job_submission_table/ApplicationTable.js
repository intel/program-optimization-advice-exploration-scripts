import React, { useState, useEffect, useMemo } from 'react';
import Table from './table';
import '../../../css/table.css';
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from '../../../Constants';
const ApplicationTable = React.memo(({ data }) => {


    const handleBestCompilersComparisonButtonClick = async (timestamp) => {
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/generate_ov_best_compilers_comparison`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:');
        }

    };
    const handleBestCompilerVSOriginalButtonClick = async (timestamp) => {
        const newWindow = window.open(`#/generated?loading=true`, "_blank");

        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/generate_ov_best_compiler_vs_orig`, { 'timestamp': timestamp })
            //send user to new page
            newWindow.location.href = `#/generated?loading=false`;


        } catch (error) {
            console.error('Error fetching data:');
        }

    };


    const fetchSubTableData = async (qaas_timestamp) => {
        try {
            const response = await axios.post(`${REACT_APP_API_BASE_URL}/get_job_submission_subtable_data`, { 'qaas_timestamp': qaas_timestamp });
            return response.data;
        } catch (error) {
            console.error('Error fetching sub-table data:');
            return [];
        }
    };
    // add color to colums
    const columns = [


        { Header: 'Application', accessor: 'app_name', },
        { Header: 'Best Compiler', accessor: 'best_compiler' },
        { Header: 'Best Speedup', accessor: 'best_speedup' },

        { Header: 'Best Time', accessor: 'best_time' },
        {
            Header: 'Best Compiler vs Default Compiler',
            id: 'comparison-best-compiler-vs-orig',
            isAction: true,
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleBestCompilerVSOriginalButtonClick(row.original.qaas_timestamp)}>See Details</button>
                </div>

            ),
        },
        {
            Header: 'Best Compilers Comparison',
            id: 'comparison-best-compilers-comparison',
            isAction: true,
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleBestCompilersComparisonButtonClick(row.original.qaas_timestamp)}>See Details</button>
                </div>

            ),
        },
        { Header: 'Machine', accessor: 'machine' },
        { Header: 'Archicture', accessor: 'arch' },
        { Header: 'Timestamp', accessor: 'qaas_timestamp' },


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