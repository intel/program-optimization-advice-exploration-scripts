import React, { useState, useEffect } from "react";
import { getAppColor, baseHistogramLayout, categorizeIntoBin, getProcessorColor } from "../../Constants";
import PlotlyHistogram from "./PlotlyHistogram";
import '../../css/graph.css'
import axios from "axios";

const range = ['<1.05', '1.05-1.1', '1.1-1.2', '1.2-1.5x']

const chartLayout = {
    ...baseHistogramLayout,
    barmode: 'stack',
    showlegend: false,
    xaxis: {
        tickmode: 'array',

    },
    yaxis: {
        title: 'count',
        automargin: true,

    },
    height: 130,
    width: 300,


};
export default function ArccompHistogram() {
    const [data, setData] = useState(null);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_arccomp_data`)
            .then((response) => {

                const rawData = response.data
                const processedData = processRawData(rawData)
                setData(processedData);



            })

    }, [])

    const processRawData = (rawData) => {
        const histogramData = rawData.Apps.map((app, index) => {
            const ratio = rawData['winner ratio'][index];
            let binKey = categorizeIntoBin(ratio, range);
            //each app
            const appHistogramData = {
                x: range,
                y: range.map((val, i) => (range[i] === binKey ? 1 : 0)),
                type: 'bar',
                name: app,
                marker: {
                    //winner processor color
                    color: getProcessorColor(rawData.winner[index]),

                },
                text: range.map((key) => (key === binKey ? app : '')),
                hoverinfo: 'text',
                hovertext: `Ratio: ${rawData['winner ratio'][index]} Winner: ${rawData['winner'][index]}`,

                textposition: 'inside',
                insidetextanchor: 'middle',
                textangle: 0,
            };

            return appHistogramData;
        });
        return histogramData;

    };

    return (
        <div className='graph-container-short-histogram' style={{ maxWidth: '300px' }}>
            <PlotlyHistogram data={data} layout={chartLayout} />

            <div className="plot-title-short-histogram">
                Fig. Arccomp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Architecture Comparison [GF/core]: SPR/ICL wins in blue, ICL/SPR wins in red

            </div>
        </div>
    );
}

