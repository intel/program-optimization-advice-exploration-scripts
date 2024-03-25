import React from 'react';
import { useState, useEffect } from 'react';
import Histogram from './Histogram'
import axios from 'axios';
import { REACT_APP_API_BASE_URL } from '../Constants';
export default function MutationSpeedupGraph({ vendor_data }) {


    const [mutationSpeedupData, setMutationSpeedupData] = useState(null);


    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.post(`${REACT_APP_API_BASE_URL}/get_lore_speedups_for_specific_mutation`, {
                    vendor_data: vendor_data
                })
                return response.data;
            } catch (error) {
                console.error('Error fetching data: ', error);
            }
        };

        fetchData().then(data => {
            const graphData = {
                labels: ['AVX', 'AVX2', 'SSE', 'Scalar', 'Base'],
                datasets: [
                    {
                        label: 'Speedup R',
                        data: data.speedup_r,
                    },
                    {
                        label: 'Speedup M',
                        data: data.speedup_m,
                    }
                ]
            };
            setMutationSpeedupData(graphData);
        });

    }, [vendor_data]);

    return (
        <div>

            {mutationSpeedupData && <div className='speedup-graph-container'><Histogram data={mutationSpeedupData} /> </div>}
        </div>
    )
}