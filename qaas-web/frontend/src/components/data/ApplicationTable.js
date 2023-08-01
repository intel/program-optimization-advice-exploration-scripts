import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';

function ApplicationTable({ data, isLoading, selectedRows, setSelectedRows, baseline, setBaseline }) {

    const [expanded, setExpanded] = useState({});


    //called when the data row is clicked
    const renderSubComponent = (row) => {

        return (
            <div style={{ padding: "20px" }}>
                <ApplicationSubTable data={row['run_data']} setSelectedRows={setSelectedRows} selectedRows={selectedRows}
                    baseline={baseline} setBaseline={setBaseline} />
            </div>
        );
    };

    const handleExpandedChange = (newExpanded) => {
        setExpanded(newExpanded);
    };


    const columns = [
        { Header: 'Workload', accessor: 'workload' },
        { Header: 'Program', accessor: 'program' },
        { Header: 'Experiment Name', accessor: 'experiment_name' },
        { Header: 'Commit ID', accessor: 'commit_id' },
        { Header: 'Total Time(s)', accessor: 'Total Time(s)' },
        { Header: 'Profiled Time(s)', accessor: 'Profiled Time(s)' },
        { Header: 'Time in analyzed loops (%)', accessor: 'Time in analyzed loops (%)' },
        { Header: 'Time in user code (%)', accessor: 'Time in user code (%)' },
        { Header: 'Compilation Options Score (%)', accessor: 'Compilation Options Score (%)' },
        { Header: 'Perfect Flow Complexity', accessor: 'Perfect Flow Complexity' },
        { Header: 'Iterations Count', accessor: 'Iterations Count' },
        { Header: 'Array Access Efficiency (%)', accessor: 'Array Access Efficiency (%)' },
        { Header: 'Perfect OpenMP + MPI + Pthread', accessor: 'Perfect OpenMP + MPI + Pthread' },
        { Header: 'Perfect OpenMP + MPI + Pthread + Perfect Load Distribution', accessor: 'Perfect OpenMP + MPI + Pthread + Perfect Load Distribution' },
        { Header: 'No Scalar Integer Potential Speedup', accessor: 'No Scalar Integer Potential Speedup' },
        { Header: 'Nb Loops to get 80%', accessor: 'Nb Loops to get 80%' },
        { Header: 'FP Vectorised Potential Speedup', accessor: 'FP Vectorised Potential Speedup' },
        { Header: 'Fully Vectorised Potential Speedup', accessor: 'Fully Vectorised Potential Speedup' },
        { Header: 'Data In L1 Cache Potential Speedup', accessor: 'Data In L1 Cache Potential Speedup' },
        { Header: 'FP Arithmetic Only Potential Speedup', accessor: 'FP Arithmetic Only Potential Speedup' },
        { Header: 'Number of Cores', accessor: 'Number of Cores' },
        { Header: 'Compilation Options', accessor: 'Compilation Options' },
        { Header: 'Model Name', accessor: 'Model Name' }
    ];

    return (
        <div className="center">

            <Table
                data={data}
                columns={columns}
                SubComponent={(row) => renderSubComponent(row.original)}
                expanded={expanded}
                onExpandedChange={handleExpandedChange}
            />

        </div>
    );
}

export default ApplicationTable;
