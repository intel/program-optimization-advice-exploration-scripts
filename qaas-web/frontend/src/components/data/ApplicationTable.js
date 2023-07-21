import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';

function ApplicationTable({ data, isLoading, selectedRows, setSelectedRows }) {

    const [expanded, setExpanded] = useState({});


    //called when the data row is clicked
    const renderSubComponent = (row) => {

        return (
            <div style={{ padding: "20px" }}>
                <ApplicationSubTable data={row['run_data']} setSelectedRows={setSelectedRows} selectedRows={selectedRows} />
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
            Header: 'Commit ID',
            accessor: 'commit_id'
        },

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
