import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import ApplicationSubTable from './ApplicationSubTable';

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


    const formatNumber = value => {
        if (value === "Not Available") return value;
        const num = parseFloat(value);
        return isNaN(num) ? value : num.toFixed(2);
    };

    const columns = [
        { Header: 'Workload', accessor: 'workload', id: 'workload' },
        { Header: 'Program', accessor: 'program', id: 'program' },
        { Header: 'Experiment Name', accessor: 'experiment_name', id: 'experiment_name' },
        { Header: 'Commit ID', accessor: 'commit_id', id: 'commit_id' },
        { Header: 'Compilation Options', accessor: 'compilation_flags', id: 'compilation_flags' },
        { Header: 'Model Name', accessor: 'model_name', id: 'model_name' },
        { Header: 'Number of Cores', accessor: d => formatNumber(d.number_of_cores), id: 'number_of_cores' },
        { Header: 'Total Time(s)', accessor: d => formatNumber(d.total_time), id: 'total_time' },
        { Header: 'Profiled Time(s)', accessor: d => formatNumber(d.profiled_time), id: 'profiled_time' },
        { Header: 'Time in analyzed loops (%)', accessor: d => formatNumber(d.time_in_analyzed_loops), id: 'time_in_analyzed_loops' },
        { Header: 'Time in user code (%)', accessor: d => formatNumber(d.time_in_user_code), id: 'time_in_user_code' },
        { Header: 'Compilation Options Score (%)', accessor: d => formatNumber(d.compilation_options_score), id: 'compilation_options_score' },
        { Header: 'Perfect Flow Complexity', accessor: d => formatNumber(d.perfect_flow_complexity), id: 'perfect_flow_complexity' },
        { Header: 'Iterations Count', accessor: d => formatNumber(d.iterations_count), id: 'iterations_count' },
        { Header: 'Array Access Efficiency (%)', accessor: d => formatNumber(d.array_access_efficiency), id: 'array_access_efficiency' },
        { Header: 'Perfect OpenMP + MPI + Pthread', accessor: d => formatNumber(d.perfect_openmp_mpi_pthread), id: 'perfect_openmp_mpi_pthread' },
        { Header: 'Perfect OpenMP + MPI + Pthread + Perfect Load Distribution', accessor: d => formatNumber(d.perfect_openmp_mpi_pthread_load_distribution), id: 'perfect_openmp_mpi_pthread_load_distribution' },
        { Header: 'No Scalar Integer Potential Speedup', accessor: d => formatNumber(d.speedup_if_clean), id: 'speedup_if_clean' },
        { Header: 'FP Vectorised Potential Speedup', accessor: d => formatNumber(d.speedup_if_fp_vect), id: 'speedup_if_fp_vect' },
        { Header: 'Fully Vectorised Potential Speedup', accessor: d => formatNumber(d.speedup_if_fully_vectorised), id: 'speedup_if_fully_vectorised' },
        { Header: 'FP Arithmetic Only Potential Speedup', accessor: d => formatNumber(d.speedup_if_FP_only), id: 'speedup_if_FP_only' },

    ];



    return (
        <div className="center">

            <Table
                data={data}
                columns={columns}
                SubComponent={(row) => renderSubComponent(row.original)}
                expanded={expanded}
                onExpandedChange={handleExpandedChange}
                getTheadThProps={() => {
                    return {
                        className: "wrap-text"
                    };
                }}
            />

        </div>
    );
}

export default ApplicationTable;