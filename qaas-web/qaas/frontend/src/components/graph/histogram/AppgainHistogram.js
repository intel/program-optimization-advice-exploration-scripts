import React from "react";
import { getAppColor } from "../../Constants";
import '../../css/graph.css'
import PlotlyHistogram from "./PlotlyHistogram";
import { baseHistogramLayout } from "../../Constants";
const range = ['tie', '1.1-1.2', '1.2-1.5', '1.5-2X', '2X – 4X', '4X <']
const histogramData = [
    {
        x: range,
        y: [1, 0, 0, 0, 0, 0],
        type: 'bar',
        name: 'AMG',
        marker: {
            color: getAppColor('AMG'),
        },
        text: ['AMG', '', '', '', '', ''],
    },
    {
        x: range,
        y: [1, 0, 0, 0, 0, 0],
        type: 'bar',
        name: 'HACC',
        marker: {
            color: getAppColor('HACC'),
        },
        text: ['HACC', '', '', '', '', ''],
    },
    {
        x: range,
        y: [0, 1, 0, 0, 0, 0],
        type: 'bar',
        name: 'CoMD',
        marker: {
            color: getAppColor('CoMD'),
        },
        text: ['', 'CoMD', '', '', '', ''],
    },
    {
        x: range,
        y: [0, 0, 1, 0, 0, 0],
        type: 'bar',
        name: 'ClovF',
        marker: {
            color: getAppColor('ClovF'),
        },
        text: ['', '', 'ClovF', '', '', ''],
    },
    {
        x: range,
        y: [0, 0, 0, 1, 0, 0],
        type: 'bar',
        name: 'Miniqmc',
        marker: {
            color: getAppColor('Miniqmc'),
        },
        text: ['', '', '', 'Miniqmc', '', ''],
    },
    {
        x: range,
        y: [0, 0, 0, 0, 1, 0],
        type: 'bar',
        name: 'Kripke',
        marker: {
            color: getAppColor('Kripke'),
        },
        text: ['', '', '', '', 'Kripke', ''],
    },
    {
        x: range,
        y: [0, 0, 0, 0, 0, 1],
        type: 'bar',
        name: 'Clov++',
        marker: {
            color: getAppColor('Clov++'),
        },
        text: ['', '', '', '', '', 'Clov++'],
    },
];


function processData(dataset) {
    return {
        ...dataset,
        textposition: 'inside',
        insidetextanchor: 'middle',
        textangle: 0,
    };
}
const processedData = histogramData.map(processData);

const chartLayout = {
    ...baseHistogramLayout,
    barmode: 'stack',
    showlegend: false,
    xaxis: {
        tickmode: 'array',

    },
    yaxis: {
        title: 'Cases Count',
        automargin: true,


    },
    height: 120,
    width: 400,


};

export default function AppgainHistogram() {
    return (
        <div className='graphContainerShortHistogram'>
            <PlotlyHistogram data={processedData} layout={chartLayout} />

            <div className="plot-title">
                Fig. appgain
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                QaaS gain vs. other 2 baselines

            </div>
        </div>
    );
}

