import React, { useState, useEffect } from "react";
import { getAppColor, baseHistogramLayout, categorizeIntoBin, getProcessorColor, getAppName, formatValue, REACT_APP_API_BASE_URL } from "../../Constants";
import PlotlyHistogram from "./PlotlyHistogram";
import '../../css/graph.css'
import axios from "axios";
import HistogramBinSlider from "./HistogramBinSlider";


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
    const [rawData, setRawData] = useState(null);

    const [range, setRange] = useState(['<1.05', '1.05-1.1', '1.1-1.2', '1.2-1.5x']);
    const handleSliderChange = (newValue) => {
        const updatedFirstRange = `<${newValue}`;

        const secondRangeParts = range[1].split('-');
        secondRangeParts[0] = newValue;
        const updatedSecondRange = secondRangeParts.join('-');
        const updatedRange = [
            updatedFirstRange, //  before the second item
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
        axios.get(`${REACT_APP_API_BASE_URL}/get_arccomp_data`)
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
        const histogramData = rawData.Apps.map((app, index) => {
            const ratio = rawData['winner ratio'][index];
            let binKey = categorizeIntoBin(ratio, range);
            const transformedAppName = getAppName(app);

            //each app
            const appHistogramData = {
                x: range,
                y: range.map((val, i) => (range[i] === binKey ? 1 : 0)),
                type: 'bar',
                name: transformedAppName,
                marker: {
                    //winner processor color
                    color: getProcessorColor(rawData.winner[index]),

                },
                text: range.map((key) => (key === binKey ? transformedAppName : '')),
                hoverinfo: 'text',
                hovertext: `Ratio: ${formatValue(rawData['winner ratio'][index])} Winner: ${formatValue(rawData['winner'][index])}`,

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
            <HistogramBinSlider
                onChange={handleSliderChange}
                min={1.02}
                max={1.05}
                step={0.01}
                defaultValue={1.05}

            />
            <div className="plot-title-short-histogram" id="figarccomp">
                Fig. Arccomp&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Architecture Comparison [GF/core]: SPR/ICL wins in blue, ICL/SPR wins in red

            </div>
        </div>
    );
}

