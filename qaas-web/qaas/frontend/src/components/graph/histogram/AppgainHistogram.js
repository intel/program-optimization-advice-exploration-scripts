import React from "react";
import { getAppColor } from "../../Constants";
import Histogram from "./Histogram";
import { BarTextPlugin } from "../GraphPlugin";
const histogramData = {
    labels: ['tie', '1.1-1.2', '1.2-1.5', '1.5-2X', '2X – 4X', '4X <'],
    datasets: [
        {
            label: 'AMG',
            backgroundColor: getAppColor('AMG'),

            data: [1, 0, 0, 0, 0, 0],
            barText: ['AMG', '', '', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'HACC',
            backgroundColor: getAppColor('HACC'),

            data: [1, 0, 0, 0, 0, 0],
            barText: ['HACC', '', '', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'CoMD',
            backgroundColor: getAppColor('CoMD'),

            data: [0, 1, 0, 0, 0, 0],
            barText: ['', 'CoMD', '', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'ClovF',
            backgroundColor: getAppColor('ClovF'),

            data: [0, 0, 1, 0, 0, 0],
            barText: ['', '', 'ClovF', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'Miniqmc',
            backgroundColor: getAppColor('Miniqmc'),

            data: [0, 0, 0, 1, 0, 0],
            barText: ['', '', '', 'Miniqmc', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'Kripke',
            backgroundColor: getAppColor('Kripke'),

            data: [0, 0, 0, 0, 1, 0],
            barText: ['', '', '', '', 'Kripke', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'Clov++',
            backgroundColor: getAppColor('Clov++'),

            data: [0, 0, 0, 0, 0, 1],
            barText: ['', '', '', '', '', 'Clov++'],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
    ]
};


const chartOptions = {
    plugins: {
        title: {
            display: true,
            text: 'Appgain',

        },


    },
    scales: {
        x: {
            title: {
                display: true,
                text: 'QaaS gain vs. other 2 baselines',
            },
            stacked: true,
        },
        y: {
            title: {
                display: true,
                text: 'Cases Count',
            },
            stacked: true,
            ticks: {
                stepSize: 1,
            },
        },
    },

};
export default function AppgainHistogram() {
    return (
        <div className='graphContainer'>
            <Histogram data={histogramData} options={chartOptions} plugins={[BarTextPlugin]} />


        </div>
    );
}

