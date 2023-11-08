import React from 'react';
import { Line } from 'react-chartjs-2';

function LineGraph({ data, options, plugins }) {
    const defaultOptions = {

    };
    return (
        <Line
            data={data}
            options={{ ...defaultOptions, ...options }}
            plugins={plugins}
        />
    );
}

export default LineGraph;
