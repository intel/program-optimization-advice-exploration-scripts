import React, { useState, useEffect } from 'react';
import Histogram from './Histogram';
import axios from 'axios';
import { useSelectionContext } from '../contexts/SelectionContext';
function TotalTimeSpeedupGraph({ open }) {
    const { selectedRows, baseline } = useSelectionContext();

    const [graphData, setGraphData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [open]);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const result = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/compute_speed_up_data_using_baseline_ov`, {
                selectedRows,
                baseline
            });
            setGraphData(result.data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setIsLoading(false);
    };

    if (isLoading || !graphData) {
        return <p>Loading graph...</p>;
    }


    const data = {
        labels: graphData.labels,
        datasets: [
            {
                label: 'Speedup',
                data: graphData.speedup,
                backgroundColor: 'rgba(255,99,132,0.2)',

            }
        ],
    };



    return (

        <Histogram data={data} />

    );
}

export default TotalTimeSpeedupGraph;
