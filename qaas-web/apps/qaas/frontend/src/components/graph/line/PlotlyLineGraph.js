
import React from 'react';
import Plot from 'react-plotly.js';

function PlotlyLineGraph({ data, layout }) {

    return (
        <Plot
            data={data}
            layout={layout}
            style={{ width: '100%', height: '100%', maxHeight: 300 }}
            config={{ displayModeBar: false, responsive: true, autosize: true, }}
        />
    );
}

export default PlotlyLineGraph;