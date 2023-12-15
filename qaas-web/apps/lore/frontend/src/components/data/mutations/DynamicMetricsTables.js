import React, { useState, useEffect } from 'react';
import Table from '../table';
import axios from 'axios';

export default function DynamicMetricsTables({ current_src_loop_id, current_mutation_number }) {


    const [derivedMetricsData, setDerivedMetricsData] = useState([]);
    const [dynamicInstrCntsData, setDynamicInstrCntsData] = useState([]);
    const [hardwareDynamicMetricsData, setHardwareDynamicMetricsData] = useState([]);

    useEffect(() => {
        axios.post(`${process.env.REACT_APP_API_BASE_URL}/get_lore_dynamic_metrics_for_specific_mutation`, {
            current_src_loop_id: current_src_loop_id,
            current_mutation_number: current_mutation_number

        })
            .then(response => {
                const { derived_metrics, dynamic_instr_cnts, hardware_dynamic_metrics } = response.data;
                setDerivedMetricsData(derived_metrics);
                setDynamicInstrCntsData(dynamic_instr_cnts);
                setHardwareDynamicMetricsData(hardware_dynamic_metrics);

            })
            .catch(error => {
                console.error('Error fetching data: ', error);
            });
    }, [current_src_loop_id, current_mutation_number]);

    const columns = [
        { Header: 'Metric', accessor: 'metric' },
        { Header: 'Reference', accessor: 'base' },
        { Header: 'Scalar', accessor: 'novec' },
        { Header: 'SSE', accessor: 'sse' },
        { Header: 'AVX', accessor: 'avx' },
        { Header: 'AVX2', accessor: 'avx2' },
    ];

    return (
        <div>
            <div>
                <h4 id="ttl3" >Hardware Dynamic Counters</h4>
            </div>
            <Table
                data={hardwareDynamicMetricsData}
                columns={columns}
                defaultPageSize={5}

            />
            <div>
                <h4 id="ttl3" >Derived Metrics</h4>
            </div>
            <Table
                data={derivedMetricsData}
                columns={columns}
                defaultPageSize={5}

            />

            <div>
                <h4 id="ttl3" >Dynamic Instruction Counts</h4>
            </div>
            <Table
                data={dynamicInstrCntsData}
                columns={columns}
                defaultPageSize={5}

            />


        </div>
    );
}
