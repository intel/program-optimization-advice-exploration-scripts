import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import ApplicationSubTable from './ApplicationSubTable';
import axios from 'axios';

function ApplicationTable({ selectedRows, setSelectedRows }) {

    const [data, setData] = useState([]);
    const [expanded, setExpanded] = useState({});

    useEffect(() => {
        //get the data
        const fetchData = async () => {
            try {
                console.log(process.env.REACT_APP_API_BASE_URL)
                const result = await axios.get(`/api/get_application_table_info_ov`);
                setData(result.data.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }

        };
        fetchData();
    }, []);

    //called when the select box is clicked or unclicked


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
