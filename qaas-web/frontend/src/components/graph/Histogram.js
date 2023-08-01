import React from 'react';
import { Bar } from 'react-chartjs-2';

function Histogram({ data }) {
    return (
        <Bar
            data={data}

        />

    );
}

export default Histogram;