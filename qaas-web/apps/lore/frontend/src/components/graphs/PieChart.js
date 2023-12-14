import React from 'react';
import { Pie } from 'react-chartjs-2';
import '../css/main.css'
function PieChart({ data }) {
    return (
        <div className='graph-spacing'>
            <Pie
                data={data}
                options={{
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                    },
                }}
            />
            <div className='ttl3, center-text'>{data.title}</div>
        </div>
    );
}

export default PieChart;