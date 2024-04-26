import React from 'react';
// import { Bar } from 'react-chartjs-2';

function Histogram({ data }) {
    return (
        <div style={{ height: '40vh' }}>

            {/* <Bar
                data={data}
                options={{
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
                            max: 5,
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,


                            },
                        },
                    },
                }}
            /> */}
        </div>

    );
}

export default Histogram;