import React, { useState, useEffect } from 'react';
import axios from "axios";
import { Chart, registerables } from "chart.js"
import { createMinMaxAnnotations } from '../GraphPlugin';
import PlotlyLineGraph from './PlotlyLineGraph';
import { getProcessorColor, getProcessorPointStyle, plotStyle, baseLineLayout } from '../../Constants';
Chart.register(...registerables);


export default function UnicorePerfGFlopsLineGraph() {
    const [chartData, setChartData] = useState(null);
    const [annotations, setAnnotations] = useState([]);

    //set raw data first time
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_qaas_unicore_perf_gflops_data`)
            .then((response) => {

                const rawData = response.data
                const preparedData = processRawData(rawData);
                console.log(preparedData)
                const newAnnotations = createMinMaxAnnotations(preparedData);
                setChartData(preparedData);
                setAnnotations(newAnnotations)



            })

    }, [])




    const processRawData = (rawData) => {
        const { Apps, ...processors } = rawData;
        return Object.keys(processors).map(processor => {
            const processorData = processors[processor];
            const symbol = getProcessorPointStyle(processor); // get the point symbol 
            const color = getProcessorColor(processor);
            return {
                type: 'scatter',
                mode: 'markers+lines',
                name: processor,
                x: Apps,
                y: processorData.map(value => value === null ? undefined : value),
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
            tickvals: [1, 2, 5, 10, 20, 40],
            ticktext: ['1', '2', '5', '10', '20', '40'],
            range: [0, 2],


        },

        annotations: annotations,

    };



    return (
        <div className='graphContainer'>

            <PlotlyLineGraph
                data={chartData}
                layout={chartLayout}
            />
            <div className="plot-title">
                Fig. uni&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Performance [Gf] of 7 miniapps on 4 current unicore processors

            </div>
        </div>
    );


}