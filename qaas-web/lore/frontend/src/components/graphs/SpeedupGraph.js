import React from 'react';
import Chart from 'chart.js/auto';
import { Line } from "react-chartjs-2";
import 'chartjs-adapter-date-fns';

const SpeedupGraph = ({ data }) => {


    const options = {
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time (Compiler Release Date)'
                },
                type: 'time',
                time: {
                    parser: 'dd MMM yyyy',
                    tooltipFormat: 'dd MMM yyyy',
                    displayFormats: {
                        day: 'MMM yyyy'
                    }
                }


            },
            y: {
                title: {
                    display: true,
                    text: 'Cycle'
                },
                beginAtZero: true,  // Ensures Y axis starts at 0
                ticks: {
                    min: 0, // Setting minimum value for y axis
                }
            }
        }
    };

    return (
        <div className='speedup-graph-container'>
            <Line data={data} options={options} />
        </div>
    );
};

export default SpeedupGraph;
