import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import LineGraph from './LineGrapah';
import { minMaxLineLabelPlugin } from '../GraphPlugin';
Chart.register(...registerables);


export default function UnicorePerfGFlopsLineGraph() {
    const [chartData, setChartData] = useState(null);


    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_unicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                setChartData(preparedData);



            })

    }, [])





    const processRawData = (rawData) => {
        const pointStyles = ['circle', 'rectRot', 'triangle', 'rect'];
        let pointStyleIndex = 0;
        const preparedData = {
            labels: rawData['Apps'].map((app) => `${app}`),
            datasets: Object.keys(rawData).filter(key => key !== 'Apps').map(key => {
                const style = pointStyles[pointStyleIndex % pointStyles.length];
                pointStyleIndex++;
                return {
                    label: key,
                    data: rawData[key],
                    fill: false,
                    pointStyle: style,
                    pointRadius: 5,


                };
            })
        };
        return preparedData;
    };

    if (chartData === null) {
        return <div>Loading Unicore GFLops graph...</div>;
    }


    const chartOptions = {
        plugins: {
            legend: {
                labels: {
                    usePointStyle: true,  // use the point style as legend symbol
                }
            },
            title: {
                display: true,
                text: 'Unicore Performance: GFlops',

            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'apps',
                }
            },

            y: {
                title: {
                    display: true,
                    text: 'GFlops',
                }
            }
        }
    };



    return (
        <div className='graphContainer'>
            <LineGraph
                data={chartData}
                options={chartOptions}
                plugins={[minMaxLineLabelPlugin]}
            />
        </div>
    );


}