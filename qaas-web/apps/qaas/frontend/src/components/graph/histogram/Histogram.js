import React from 'react';
import { Bar } from 'react-chartjs-2';
export default function Histogram({ data, options, plugins }) {
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
            position: 'left',
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: data.xAxis,
                },




                stacked: true,

            },
            y: {
                title: {
                    display: true,
                    text: data.yAxis,
                },
                stacked: true,
                min: 0,
                beginAtZero: true,
                ticks: {
                    stepSize: 1,
                },
            },
        },
    };

    return (
        <Bar
            data={data}
            options={{ ...defaultOptions, ...options }}
            plugins={plugins}
        />
    );
}
