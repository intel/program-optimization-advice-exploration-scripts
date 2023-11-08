import React from "react";
import { getAppColor } from "../../Constants";
import Histogram from "./Histogram";
import { BarTextPlugin } from "../GraphPlugin";
const histogramData = {
    labels: ['<1.05', '1.05-1.1', '1.1-1.2', '1.2-1.5x'],
    datasets: [
        {
            label: 'ClovF',
            backgroundColor: getAppColor('ClovF'),
            data: [1, 0, 0, 0],
            barText: ['ClovF', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'AMG',
            data: [1, 0, 0, 0],
            backgroundColor: getAppColor('AMG'),

            barText: ['AMG', '', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },

        {
            label: 'Kripke',
            data: [0, 1, 0, 0],
            backgroundColor: getAppColor('Kripke'),

            barText: ['', 'Kripke', '', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },

        {
            label: 'Miniqmc',
            data: [0, 0, 1, 0],
            backgroundColor: getAppColor('Miniqmc'),

            barText: ['', '', 'Miniqmc', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },

        {
            label: 'Clov++',
            data: [0, 0, 1, 0],
            backgroundColor: getAppColor('Clov++'),

            barText: ['', '', 'Clov++', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'CoMD',
            data: [0, 0, 1, 0],
            backgroundColor: getAppColor('CoMD'),

            barText: ['', '', 'CoMD', ''],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
        {
            label: 'HACC',
            data: [0, 0, 0, 1],
            backgroundColor: getAppColor('HACC'),

            barText: ['', '', '', 'HACC'],
            barPercentage: 1.0,
            categoryPercentage: 1.0,
        },
    ]
};


const chartOptions = {
    plugins: {
        title: {
            display: true,
            text: 'Fig Arccomp',

        },


    },
    scales: {
        x: {
            title: {
                display: true,
                text: 'Time Ratio',
            },
            stacked: true,
        },
        y: {
            title: {
                display: true,
                text: 'count',
            },
            stacked: true,
            ticks: {
                stepSize: 1,
            },
        },
    },

};
export default function ArccompHistogram() {
    return (
        <div className='graphContainer'>
            <Histogram data={histogramData} options={chartOptions} plugins={[BarTextPlugin]} />
        </div>
    );
}

