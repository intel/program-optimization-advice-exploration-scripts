import React, { useState } from "react";
import { getAppColor, categorizeIntoBin, getCompilerColor } from "../../Constants";
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

export default function CompilerSpeedupComparisonHistorgram({ data }) {

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

    const processRawData = (rawData) => {
        if (!rawData || rawData.length === 0) {
            return [];
        }
        let processedData = rawData.map(dataPoint => {
            const binKey = categorizeIntoBin(dataPoint.speedup, range);
            const compilerColor = getCompilerColor(dataPoint.compiler.toUpperCase());
            return {
                x: [binKey],
                y: [1], // each data point is 1 count
                type: 'bar',
                name: dataPoint.compiler,
                marker: {
                    color: compilerColor,
                },
                hoverinfo: 'x+y+name',
            };
        });


        return processedData;
    };

    const processedData = processRawData(data);

    return (
        <div className='graph-container-short-histogram center-histogram'>
            <PlotlyHistogram data={processedData} layout={chartLayout} />
            <HistogramBinSlider
                onChange={handleSliderChange}
                min={1.02}
                max={1.1}
                step={0.01}
                defaultValue={1.1}

            />
            <div className="plot-title-short-histogram" id="compiler-comparison">
                Fig. compiler speedup comparison
            </div>
        </div>
    );
}

