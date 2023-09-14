import React, { useState, useEffect } from "react";
import Histogram from "./Histogram";
import { Modal } from 'antd';
import axios from 'axios';
import { RANGES } from "../Constants";
import { DEFAULT_COLOR_SCHEME } from "../Constants";
export default function AllLoopsSpeedupRangeGraph() {
    const [data, setData] = useState(null);
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const fetchData = () => {
        setLoading(true);

        axios.get(`${process.env.REACT_APP_API_BASE_URL}/lore_get_all_speedup_range`)
            .then(response => {
                setData(response.data);
                setOpen(true);
                setLoading(false)

            })
            .catch(error => {
                console.error('Error fetching performance data:', error);
                setLoading(false)
            });
    }



    // This function aggregates all speedup_r values for a compiler across all loop IDs
    const gatherAllSpeedupRForCompiler = (data, compilerName) => {
        let speedupDataList = [];

        // Iterate through all loop IDs
        for (let loopID of Object.keys(data)) {
            const compilersData = data[loopID];
            const compilerData = compilersData[compilerName];

            if (compilerData) {
                for (let mutation of compilerData) {
                    for (let mutationData of Object.values(mutation)) {
                        speedupDataList.push(mutationData.speedup_r);
                    }
                }
            }
        }

        return speedupDataList;
    };

    const generateDataForCompiler = (data, compilerName) => {
        const allSpeedupR = gatherAllSpeedupRForCompiler(data, compilerName);

        // Generate histogram data
        return RANGES.map(range => {
            if (range.includes('>')) {
                const min = parseFloat(range.split('>')[1]);
                return allSpeedupR.filter(speed => speed > min).length;
            } else {
                const [min, max] = range.split('-').map(Number);
                return allSpeedupR.filter(speed => speed >= min && speed < max).length;
            }
        });
    };

    const chartData = data ? {
        labels: RANGES,
        datasets: Object.keys(data[Object.keys(data)[0]]) // Assuming first loopID has all compilers
            .map((compilerName, index) => ({
                label: `${compilerName}`,
                data: generateDataForCompiler(data, compilerName),
                fill: false,
                backgroundColor: DEFAULT_COLOR_SCHEME[index % DEFAULT_COLOR_SCHEME.length]
            })),
        xAxis: 'Range',
        yAxis: 'Count Speedup R',
    } : null;

    return (

        <div >

            <button onClick={fetchData}>
                Show All Speedup Range Count Graph
            </button>
            <Modal
                title="All speedup range count"
                open={open}
                onCancel={() => setOpen(false)}
                onOk={() => setOpen(false)}
            >
                <Histogram data={chartData} />
            </Modal>

        </div>
    )
}
