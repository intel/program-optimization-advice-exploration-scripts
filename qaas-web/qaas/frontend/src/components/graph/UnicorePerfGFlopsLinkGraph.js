import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import LineGraph from './LineGrapah';
Chart.register(...registerables);


export default function UnicorePerfGFlopsLinkGraph() {
    const [chartData, setChartData] = useState(null);
    const [percentDiffs, setPercentDiffs] = useState(null);


    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_unicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                setChartData(preparedData);

                const calculatedDiffs = calculatePercentDiffs(rawData);
                setPercentDiffs(calculatedDiffs);

            })

    }, [])



    const calculatePercentDiffs = (rawData) => {
        const percentDiffs = {};

        rawData['Apps'].forEach((app, index) => {
            const values = Object.keys(rawData)
                .filter(key => key !== 'Apps')
                .map(key => rawData[key][index])
                .filter(val => val != null);  // remove null or undefined values

            const minVal = Math.min(...values);
            const maxVal = Math.max(...values);
            let percentDiff = ((maxVal - minVal) / minVal) * 100;

            percentDiffs[app] = isFinite(percentDiff) ? percentDiff : 0;
        });
        return percentDiffs;
    };

    const processRawData = (rawData) => {
        const pointStyles = ['circle', 'star', 'triangle', 'rect'];
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


                };
            })
        };
        return preparedData;
    };

    if (chartData === null || percentDiffs == null) {
        return <div>Loading Unicore GFLops graph...</div>;
    }

    const minMaxLineLablePlugin = {
        id: 'minMax',
        afterDraw: (chart) => {

            const ctx = chart.ctx;
            ctx.fillStyle = 'black';

            const xAxis = chart.scales['x'];
            const yAxis = chart.scales['y'];

            chart.data.labels.forEach((label, index) => {
                let minValue = Math.min(...chart.data.datasets.map(dataset => dataset.data[index]).filter(value => value !== null)); // find min value for each index
                const x = xAxis.getPixelForValue(label, index) - 15;
                const y = yAxis.getPixelForValue(minValue) + 5; // position the text  below the min value

                const percentDiff = percentDiffs[label] || 0;  // get from state or whatever data structure

                ctx.fillText(`${percentDiff.toFixed(2)}%`, x, y);
            });
        }

    }

    const chartOptions = {
        plugins: {
            title: {
                display: true,
                text: 'Unicore Performance: GFlops',

            },
        }
    };



    // Inside your component
    return (
        <div className='graphContainer'>
            <LineGraph
                data={chartData}
                options={chartOptions}
                plugins={[minMaxLineLablePlugin]}
            />
        </div>
    );


}