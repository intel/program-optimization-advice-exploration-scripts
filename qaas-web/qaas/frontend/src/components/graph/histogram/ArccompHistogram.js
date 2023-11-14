import React from "react";
import { getAppColor, baseHistogramLayout } from "../../Constants";
import PlotlyHistogram from "./PlotlyHistogram";
import '../../css/graph.css'
const range = ['<1.05', '1.05-1.1', '1.1-1.2', '1.2-1.5x']
const histogramData = [

    {
        x: range,
        y: [1, 0, 0, 0], // Data for ClovF
        type: 'bar',
        name: 'ClovF',
        marker: {
            color: getAppColor('ClovF'),
        },
        text: ['ClovF', '', '', ''],
    },
    {
        x: range,
        y: [1, 0, 0, 0], // Data for AMG
        type: 'bar',
        name: 'AMG',
        marker: {
            color: getAppColor('AMG'),
        },
        text: ['AMG', '', '', ''],
    },
    {
        x: range,
        y: [0, 1, 0, 0], // Data for Kripke
        type: 'bar',
        name: 'Kripke',
        marker: {
            color: getAppColor('Kripke'),
        },
        text: ['', 'Kripke', '', ''],
    },
    {
        x: range,
        y: [0, 0, 1, 0], // Data for Miniqmc
        type: 'bar',
        name: 'Miniqmc',
        marker: {
            color: getAppColor('Miniqmc'),
        },
        text: ['', '', 'Miniqmc', ''],

    },
    {
        x: range,
        y: [0, 0, 1, 0], // Data for Clov++
        type: 'bar',
        name: 'Clov++',
        marker: {
            color: getAppColor('Clov++'),
        },
        text: ['', '', 'Clov++', ''],
    },
    {
        x: range,
        y: [0, 0, 1, 0], // Data for CoMD
        type: 'bar',
        name: 'CoMD',
        marker: {
            color: getAppColor('CoMD'),
        },
        text: ['', '', 'CoMD', ''],

    },
    {
        x: range,
        y: [0, 0, 0, 1], // Data for HACC
        type: 'bar',
        name: 'HACC',
        marker: {
            color: getAppColor('HACC'),
        },
        text: ['', '', '', 'HACC'],

    },
]
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
        title: 'count',
        automargin: true,

    },
    height: 130,
    width: 300,


};
export default function ArccompHistogram() {
    return (
        <div className='graphContainerShortHistogram'>
            <PlotlyHistogram data={processedData} layout={chartLayout} />

            <div className="plotTitleShortHistogram">
                Fig. Arccomp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Architecture Comparison [GF/core]: SPR/ICL wins in green, ICL/SPR wins in blue

            </div>
        </div>
    );
}

