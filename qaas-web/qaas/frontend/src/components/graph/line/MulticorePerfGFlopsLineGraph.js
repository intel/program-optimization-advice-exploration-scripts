import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import LineGraph from './LineGrapah';
import { minMaxMultipleLineLabelPlugin, multicorePerformanceHtmlLegendPlugin } from '../GraphPlugin';
import { getProcessorColor } from '../../Constants';
Chart.register(...registerables);


export default function MulticorePerfGFlopsLineGraph() {
    const [chartData, setChartData] = useState(null);


    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_multicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                setChartData(preparedData);



            })

    }, [])




    //create 2 groups one for total gflops and one for gflops per core
    const processRawData = (rawData) => {
        const styles = {
            'ICL': {
                borderColor: getProcessorColor('ICL'),
                backgroundColor: getProcessorColor('ICLLIGHT'),
                pointStyle: 'circle',
            },
            'SPR': {
                borderColor: getProcessorColor('SPR'),
                backgroundColor: getProcessorColor('SPRLIGHT'),
                pointStyle: 'rectRot',
            }
        };
        const datasets = Object.keys(rawData).filter(key => key !== 'Apps').map(key => {
            const isICLData = key.includes('ICL');
            const isCoreData = key.includes('per-core');

            // Determine the style based on ICL or SPR data
            const dataSetStyle = isICLData ? styles['ICL'] : styles['SPR'];

            return {
                label: key,
                data: rawData[key],
                fill: false,
                borderColor: dataSetStyle.borderColor,
                backgroundColor: dataSetStyle.backgroundColor,
                // Apply dashed line if it's core data, solid otherwise
                borderDash: isCoreData ? [5, 5] : [],
                pointStyle: dataSetStyle.pointStyle,
                pointRadius: 5,
            };
        });

        return {
            labels: rawData['Apps'],
            datasets: datasets
        };
    };

    if (chartData === null) {
        return <div>Loading MulticoreS GFLops graph...</div>;
    }


    const chartOptions = {
        plugins: {
            legend: {
                display: false,

            },

        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Fig. MPperf          Multicore Performance: System vs per-core GFlops',
                    font: {
                        size: 24
                    },
                    padding: {
                        top: 30,
                        bottom: 30
                    }
                }
            },

            y: {
                type: 'logarithmic',

                title: {
                    display: true,
                    text: 'GFlops',


                },
                ticks: {
                    min: 10,
                    max: 2000,
                    // For a category axis, the val is the index so the lookup via getLabelForValue is needed
                    callback: function (val, index, values) {
                        // Hide every 2nd tick label
                        const ticks = [10, 20, 50, 100, 500, 2000]
                        if (ticks.includes(val)) {
                            return val;
                        }
                    },
                }

            }
        }
    };


    console.log("chartdata", chartData)
    return (
        <div className='graphContainer'>
            <LineGraph
                data={chartData}
                options={chartOptions}
                plugins={[minMaxMultipleLineLabelPlugin, multicorePerformanceHtmlLegendPlugin]}
            />
            <div id="js-legend" className="chart-legend"></div>

        </div>
    );


}