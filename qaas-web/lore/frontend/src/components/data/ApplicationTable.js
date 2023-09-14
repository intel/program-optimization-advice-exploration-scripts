import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import ApplicationSubTable from './ApplicationSubTable';

function ApplicationTable({ data, isLoading, page, pageSize, onPageChange, onPageSizeChange, numPages }) {

    const [expanded, setExpanded] = useState({});


    //called when the data row is clicked
    const renderSubComponent = (row) => {

        return (
            <div style={{ padding: "20px" }}>
                <ApplicationSubTable data={row['run_data']}
                    workload={row['workload']}
                    program={row['program']}
                    workload_version={row['version']}
                />
            </div>
        );
    };

    const handleExpandedChange = (newExpanded) => {
        setExpanded(newExpanded);
    };


    const columns = [

        {
            Header: 'Workload',
            accessor: 'workload'
        },
        {
            Header: 'Version',
            accessor: 'version'
        },
        {
            Header: 'Program',
            accessor: 'program'
        },
        {
            Header: '# of Loops',
            accessor: 'n_loops'
        },

        {
            Header: 'Commit ID',
            accessor: 'commit_id'
        },

    ];


    return (
        <div className="center">

            {isLoading ? (
                // Render "loading..." message when data is being fetched
                <div>Loading...</div>
            ) : (
                // Render the table when data fetch is complete
                <Table
                    data={data}
                    columns={columns}
                    SubComponent={(row) => renderSubComponent(row.original)}
                    expanded={expanded}
                    onExpandedChange={handleExpandedChange}
                    defaultPageSize={pageSize}
                    page={page}
                    pageSize={pageSize}
                    onPageChange={onPageChange}
                    onPageSizeChange={onPageSizeChange}
                    numPages={numPages}

                />
            )}

        </div>
    );
}

export default ApplicationTable;
