import React, { useState, useEffect } from "react";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { REACT_APP_API_BASE_URL } from "../Constants";
import Table from "./table";
function ApplicationSubTable({ application_id, workload, program, workload_version }) {

    const [loopdata, setLoopData] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const result = await axios.post(`${REACT_APP_API_BASE_URL}/get_application_subtable_info_lore`, { application_id: application_id });
            setLoopData(result.data.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };
    if (!loopdata || loopdata.length <= 0) {
        return <div>Loading...</div>
    }
    //will pass specfici loop data
    const handleButtonClick = async (data) => {

        // Call your backend API here and fetch data
        const queryString = new URLSearchParams({ ...data, workload, program, workload_version, loading: 'false' }).toString();
        console.log(queryString)
        navigate(`/loop?${queryString}`);
        // window.open(`/loop?${queryString}`, '_blank');

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
            Header: '# of Mutations',
            accessor: 'n_mutations'
        },
    ];


    return (
        <Table
            data={loopdata}
            columns={columns}
            defaultPageSize={10}
        />
    );
}

export default ApplicationSubTable;