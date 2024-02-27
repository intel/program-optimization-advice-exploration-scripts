import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import { } from '../GraphPlugin';
import PlotlyLineGraph from './PlotlyLineGraph';
import { getProcessorColor, getProcessorPointStyle, plotStyle, baseLineLayout, getAppName } from '../../Constants';
import { createMultileMinMaxAnnotations } from '../GraphPlugin';
Chart.register(...registerables);


export default function MulticorePerfGFlopsLineGraph() {
    const [chartData, setChartData] = useState(null);
    const [annotations, setAnnotations] = useState([]);


    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_multicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                const newAnnotations = createMultileMinMaxAnnotations(preparedData);
                setChartData(preparedData);
                setAnnotations(newAnnotations)



            })

    }, [])



    function getProcessor(processorName) {
        let processType = '';
        const nameLower = processorName.toLowerCase();

        if (nameLower.includes('icl')) {
            processType = 'ICL';
        } else if (nameLower.includes('spr')) {
            processType = 'SPR';
        }

        return processType;
    }
    const processRawData = (rawData) => {
        const { Apps, ...processors } = rawData;
        const transformedApps = Apps.map(app => getAppName(app));

        return Object.keys(processors).map(processor => {
            const processorData = processors[processor];
            const processType = getProcessor(processor);
            const symbol = getProcessorPointStyle(processType); // get the point symbol 
            const color = getProcessorColor(processType);
            const isTotalGFlops = processor.toLowerCase().includes('total');
            const yAxis = isTotalGFlops ? 'y' : 'y2';
            return {
                type: 'scatter',
                mode: 'markers+lines',
                name: processor,
                x: transformedApps,
                y: processorData.map(value => value === null ? undefined : value),
                yaxis: yAxis,
                line: {
                    color: color,
                    dash: isTotalGFlops ? 'solid' : 'dash'
                },
                marker: {
                    symbol: symbol,
                    color: color,
                    size: 8,
                },
                hovertemplate: `%{x}: %{y:.2f}<extra>${processor}</extra>`

            };
        });
    };


    if (chartData === null) {
        return <div>Loading MulticoreS GFLops graph...</div>;
    }


    const chartLayout = {
        ...baseLineLayout,

        yaxis: {
            title: 'Total Gf',
            type: 'log',
            tickvals: [0, 5, 10, 20, 50, 100, 500, 2000],
            ticktext: ['0', '5', '10', '20', '50', '100', '500', '2000'],
            range: [0, Math.log10(2000)],//a bit more space to show the text


        },
        yaxis2: {
            title: 'Gf/core',
            type: 'linear',
            overlaying: 'y',
            side: 'right',
            tickvals: [0, 10, 20, 30, 40],
            ticktext: ['0', '10', '20', '30', '40'],
            range: [0, 40],
        },

        annotations: annotations,


    };


    return (
        <div className='graphContainer'>
            <PlotlyLineGraph
                data={chartData}
                layout={chartLayout}
            />
            <div className="plot-title" id='figmpperf'>
                Fig. MPperf &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Multicore Performance: Total System Gf vs. Gf/core

            </div>
        </div>
    );


}