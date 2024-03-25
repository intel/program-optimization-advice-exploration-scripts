import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import { createMinMaxAnnotations } from '../GraphPlugin';
import PlotlyLineGraph from './PlotlyLineGraph';
import { getProcessorColor, getProcessorPointStyle, plotStyle, baseLineLayout, getAppName, formatValue, REACT_APP_API_BASE_URL } from '../../Constants';
Chart.register(...registerables);


export default function UnicorePerfGFlopsLineGraph() {
    const [chartData, setChartData] = useState(null);
    const [annotations, setAnnotations] = useState([]);

    //set raw data first time
    useEffect(() => {
        axios.get(`${REACT_APP_API_BASE_URL}/get_qaas_unicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                const newAnnotations = createMinMaxAnnotations(preparedData);
                setChartData(preparedData);
                setAnnotations(newAnnotations)



            })

    }, [])




    const processRawData = (rawData) => {
        const { Apps, ...processors } = rawData;
        //no data
        if (!Apps || Apps.length === 0) {
            return [];
        }
        const transformedApps = Apps.map(app => getAppName(app));
        return Object.keys(processors).map(processor => {

            const processorData = processors[processor];
            const symbol = getProcessorPointStyle(processor); // get the point symbol 
            const color = getProcessorColor(processor);
            console.log("processors", processorData, processor, symbol, color, transformedApps)
            return {
                type: 'scatter',
                mode: 'markers+lines',
                name: processor,
                x: transformedApps,
                y: processorData.map(value => value === null ? undefined : formatValue(value)),
                line: {
                    color: color,
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
        return <div>Loading Unicore GFLops graph...</div>;
    }

    const chartLayout = {
        ...baseLineLayout,


        yaxis: {
            title: 'GFlops',
            type: 'log',
            tickvals: [1, 2, 5, 10, 20, 30],
            ticktext: ['1', '2', '5', '10', '20', '30'],
            range: [0, 1.6],


        },

        annotations: annotations,

    };



    return (
        <div className='graphContainer'>

            <PlotlyLineGraph
                data={chartData}
                layout={chartLayout}
            />
            <div className="plot-title" id='figuni'>
                Fig. uni&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Performance [Gf] of 7 miniapps on 4 current unicore processors

            </div>
        </div>
    );


}