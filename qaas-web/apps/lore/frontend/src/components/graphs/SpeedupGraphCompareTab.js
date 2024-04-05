import React, { useState, useEffect } from "react";
import SpeedupGraph from "./SpeedupGraph";
import TabSelector from "../data/TabSelector";
import axios from 'axios';
import Histogram from './Histogram'
import { RANGES } from "../Constants";
import { getCompilerColor, REACT_APP_API_BASE_URL } from "../Constants";

export default function SpeedupGraphCompareTab({ current_src_loop_id, data }) {


    const [activeTab, setActiveTab] = useState('Evolution of baseline performance');
    const [baselinePerformanceData, setBaselinePerformanceData] = useState(null);
    const [mutationPerformanceData, setMutationPerformanceData] = useState(null);
    const tabs = ['Evolution of baseline performance', 'Evolution of best mutation performance', 'Evolution of different compilers performance'];

    useEffect(() => {
        // Fetch both datasets
        axios.post(`${REACT_APP_API_BASE_URL}/get_performance_data_for_specific_loop`, {
            current_src_loop_id

        })
            .then(response => {
                setBaselinePerformanceData(prepareDataForGraph(response.data.baseline));
                setMutationPerformanceData(prepareDataForGraph(response.data.mutation));
            })
            .catch(error => {
                console.error('Error fetching performance data:', error);
            });
    }, []);

    const prepareDataForGraph = (data) => {
        const datasets = Object.keys(data).map((key, index) => ({
            label: key,
            data: data[key],
            fill: false,
        }));

        return { datasets };
    }

    if (!baselinePerformanceData || !mutationPerformanceData) {
        return <div>Loading...</div>;
    }

    //prepare historgram for speedup r for differetn compiler
    const generateDataForCompiler = (compilersData, compilerName) => {
        let speedupData = [];
        for (let d of compilersData[compilerName]) {
            speedupData.push(d[Object.keys(d)[0]].speedup_r);
        }

        // Generate histogram data
        return RANGES.map(range => {
            if (range.includes('>')) {
                const min = parseFloat(range.split('>')[1]);
                return speedupData.filter(speed => speed > min).length;
            } else {
                const [min, max] = range.split('-').map(Number);
                return speedupData.filter(speed => speed >= min && speed < max).length;
            }
        });
    };

    const chartData = {
        labels: RANGES,
        datasets: Object.keys(data).map(compilerName => ({

            label: `${compilerName}`,
            data: generateDataForCompiler(data, compilerName),
            borderColor: getCompilerColor(compilerName.split(' ')[0]), // give color based on the label
            backgroundColor: getCompilerColor(compilerName.split(' ')[0])
        })),
        xAxis: 'Range',
        yAxis: 'Count Speedup R',
    };
    // console.log(data)

    return (
        <div className="component-background">
            <TabSelector activeTab={activeTab} setActiveTab={setActiveTab} tabs={tabs} />
            <div className="sub-tab-container">
                {activeTab === 'Evolution of baseline performance' && <SpeedupGraph data={baselinePerformanceData} />}
                {activeTab === 'Evolution of best mutation performance' && <SpeedupGraph data={mutationPerformanceData} />}
                {activeTab === 'Evolution of different compilers performance' && <div className='speedup-graph-container'>
                    <Histogram data={chartData} /> </div>}

            </div>
        </div>
    )
}
