import React, { useState, useEffect } from 'react';
import Table from './table';
import '../css/table.css'
import axios from 'axios';
function MutationTable({ current_src_loop_id }) {

    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);



    useEffect(() => {
        //get the data
        const fetchData = async () => {
            setIsLoading(true);
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_mutation_data_for_specific_loop`, {
                current_src_loop_id
            })
                .then(response => {
                    setData(response.data);
                })
                .catch(error => {
                    console.error('Error fetching data: ', error);
                });
            setIsLoading(false);

        };
        fetchData();
    }, []);

    const columns = [

        {
            Header: 'Mutation Number',
            accessor: 'mutation'
        },
        {
            Header: 'Transformation Sequence',
            accessor: 'trans_seq'
        },
        {
            Header: 'Interchange',
            accessor: 'interchange'
        },
        {
            Header: 'Tiling',
            accessor: 'tiling'
        },
        {
            Header: 'Distribution',
            accessor: 'distrubution'
        },

        {
            Header: 'Unrolling',
            accessor: 'unrolling'
        },
        {
            Header: 'Unroll-jam',
            accessor: 'unroll_jam'
        },

    ];


    return (
        <div className="center">

            {isLoading ? (
                // Render "loading..." message when data is being fetched
                <div>Loading...</div>
            ) : (
                // Render the table when data fetch is complete
                <>
                    <Table
                        data={data}
                        columns={columns}
                        defaultPageSize={5}
                    />


                </>
            )}

        </div>
    );
}

export default MutationTable;
