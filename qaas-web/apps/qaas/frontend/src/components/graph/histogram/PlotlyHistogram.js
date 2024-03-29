import React from 'react';
import Plot from 'react-plotly.js';

export default function PlotlyHistogram({ data, layout }) {


    return (
        <Plot
            data={data}
            layout={layout}
            style={{ width: "100%", height: "100%" }}
            config={{ displayModeBar: false, responsive: true }}

        />
    );
}
