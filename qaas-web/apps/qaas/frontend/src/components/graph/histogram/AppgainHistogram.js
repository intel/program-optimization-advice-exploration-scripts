import React, { useState, useEffect } from "react";
import axios from "axios";

import { getAppColor, categorizeIntoBin } from "../../Constants";
import '../../css/graph.css'
import PlotlyHistogram from "./PlotlyHistogram";
import { baseHistogramLayout, getAppName } from "../../Constants";
import HistogramBinSlider from "./HistogramBinSlider";


const chartLayout = {
    ...baseHistogramLayout,
    barmode: 'stack',
    showlegend: false,
    xaxis: {
        tickmode: 'array',

    },
    yaxis: {
        title: 'Cases Count',
        automargin: true,
        dtick: 1,


    },
    height: 110,
    width: 400,


};

export default function AppgainHistogram() {

    const [data, setData] = useState(null);
    const [rawData, setRawData] = useState(null);
    const [range, setRange] = useState(['tie', '1.1-1.2', '1.2-1.5', '1.5-2x', '2x-4x', '>4x']);

    const handleSliderChange = (newValue) => {
        const secondRangeParts = range[1].split('-');
        secondRangeParts[0] = newValue;
        const updatedSecondRange = secondRangeParts.join('-');
        const updatedRange = [
            ...range.slice(0, 1), //  before the second item
            updatedSecondRange,
            ...range.slice(2) //  after the second item
        ];
        setRange(updatedRange);
    };


    useEffect(() => {
        if (rawData) { // only when rawData is not null
            const processedData = processRawData(rawData);
            setData(processedData);
        }
    }, [range]);
    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_BASE_URL}/get_appgain_data`)
            .then((response) => {

                const rawData = response.data
                setRawData(response.data);
                const processedData = processRawData(rawData)
                setData(processedData);



            })

    }, [])
    const processRawData = (rawData) => {
        if (!rawData || Object.keys(rawData).length === 0) {
            return [];
        }
        const histogramData = rawData.app.map((app, index) => {
            const largestGain = rawData['largest_gain'][index];
            let binKey = categorizeIntoBin(largestGain, range);
            const transformedAppName = getAppName(app);

            //each app
            const appHistogramData = {
                x: range,
                y: range.map((val, i) => (range[i] === binKey ? 1 : 0)),
                type: 'bar',
                name: transformedAppName,
                marker: {
                    //winner processor color
                    color: getAppColor(app),
                },
                text: range.map((key) => (key === binKey ? transformedAppName : '')),
                hoverinfo: 'text',
                hovertext: `Largest Gain: ${largestGain.toFixed(2)}`,

                textposition: 'inside',
                insidetextanchor: 'middle',
                textangle: 0,
            };

            return appHistogramData;
        });
        return histogramData;

    };
    return (
        <div className='graph-container-short-histogram'>
            <PlotlyHistogram data={data} layout={chartLayout} />
            <HistogramBinSlider
                onChange={handleSliderChange}
                min={1.02}
                max={1.1}
                step={0.01}
                defaultValue={1.1}

            />
            <div className="plot-title-short-histogram" id="figappgain">
                Fig. appgain
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                QaaS compiler gain vs. other 2 baselines

            </div>
        </div>
    );
}

