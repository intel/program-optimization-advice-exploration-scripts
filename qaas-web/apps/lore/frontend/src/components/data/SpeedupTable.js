import Table from './table';
import React, { useState } from 'react';
import MutationPage from '../MutationPage';
import axios from 'axios';

export default function SpeedupTable({ data, current_src_loop_id }) {


    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentRow, setCurrentRow] = useState(null);
    const [mutationPerformanceData, setMutationPerformanceData] = useState([]);

    const handleViewDetailsButtonClick = (row) => {
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_lore_mutated_execution_cycels_for_specific_mutation`, {
            current_src_loop_id: current_src_loop_id,
            mutation_number: row['mutation'],
            base_ref: row['base_ref'],
            min_base_ref: row['min_base_ref']
        })
            .then(response => {
                setMutationPerformanceData(response.data);
                setCurrentRow(row);
                setIsModalOpen(true);
            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    };

    const handleOk = () => {
        setIsModalOpen(false);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };
    // flatten data to match the expected structure
    const flattenedData = data.map((item, index) => ({
        mutation: index,
        ...item[Object.keys(item)[0]]
    }));


    const formatNumber = value => {
        if (value === "Not Available") return value;
        const num = parseFloat(value);
        return isNaN(num) ? value : num.toFixed(2);
    };

    const tablecolumns = [
        {
            Header: 'Action',
            id: 'button',
            Cell: ({ row }) => (
                <div className="table-action">
                    <button className="table-action-button" onClick={() => handleViewDetailsButtonClick(row._original)}>View Details</button>

                </div>

            ),
            width: 100,
        },
        {
            Header: 'Mutation #',
            accessor: 'mutation',
        },

        {
            Header: 'Speedupr',
            accessor: d => formatNumber(d.speedup_r),
            id: 'speedup_r'
        },
        {
            Header: 'Speedupm',
            accessor: d => formatNumber(d.speedup_m),
            id: 'speedup_m'
        },
        {
            Header: 'Reference(cc)',
            accessor: 'base'
        },
        {
            Header: 'Scalar(cc)',
            accessor: 'novec'
        },

        {
            Header: 'SSE(cc)',
            accessor: 'sse'
        },
        {
            Header: 'AVX(cc)',
            accessor: 'avx'
        },
        {
            Header: 'AVX2(cc)',
            accessor: 'avx2'
        },

    ];


    return (
        <div>
            <Table
                data={flattenedData}
                columns={tablecolumns}
                defaultPageSize={5}
            />
            {isModalOpen && current_src_loop_id && (
                <MutationPage
                    open={isModalOpen}
                    data={currentRow}
                    mutationPerformanceData={mutationPerformanceData}
                    onOk={handleOk}
                    onCancel={handleCancel}
                    current_src_loop_id={current_src_loop_id}


                />
            )}
        </div>
    );
}
