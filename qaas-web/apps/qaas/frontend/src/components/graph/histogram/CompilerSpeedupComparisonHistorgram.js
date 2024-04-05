import React, { useState } from "react";
import { getAppColor, categorizeIntoBin, getCompilerColor } from "../../Constants";
import '../../css/graph.css'
import PlotlyHistogram from "./PlotlyHistogram";
import { baseHistogramLayout, getAppName, handleSliderChange } from "../../Constants";
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
    width: 600,
    height: 350,


};

export default function CompilerSpeedupComparisonHistorgram({ data }) {

    const [range, setRange] = useState(['no gain', '1.1-1.2', '1.2-1.5', '1.5-2x', '2x-4x', '>4x']);



    const processRawData = (rawData) => {
        if (!rawData || Object.keys(rawData).length === 0) {
            return [];
        }

        const binAggregates = {};
        rawData.forEach(dataPoint => {
            const binKey = categorizeIntoBin(dataPoint.speedup, range);
            const compilerName = dataPoint.compiler.toUpperCase();
            const hoverText = `${compilerName}${dataPoint.is_best ? ' (Best)' : ''}${dataPoint.is_orig ? ' (Orig)' : ''} - Speedup: ${dataPoint.speedup.toFixed(2)}`; // show is orig, is best, and speepdup
            const color = getCompilerColor(compilerName);

            //empty list to still show bin
            if (!binAggregates[binKey]) {
                binAggregates[binKey] = [];
            }

            binAggregates[binKey].push({
                compilerName,
                hoverText,
                color,
            });
        });

        // map each bin to plotly format add data from agggated results
        const histogramData = range.map(binKey => {
            const binDetails = binAggregates[binKey] || [];
            return {
                x: binDetails.length > 0 ? binDetails.map(() => binKey) : [binKey],
                y: binDetails.length > 0 ? binDetails.map(() => 1) : [0],
                type: 'bar',
                name: binDetails.map(detail => detail.compilerName).join(', ') || 'No data',
                marker: {
                    color: binDetails.length > 0 ? binDetails.map(detail => detail.color) : ['#ddd'],
                },
                hoverinfo: 'text',

                hovertext: binDetails.length > 0 ? binDetails.map(detail => detail.hoverText) : ['No data'],
                textposition: 'inside',
                insidetextanchor: 'middle',
                textangle: 0,
            };
        });

        return histogramData;
    };



    const processedData = processRawData(data);

    return (
        <div >
            <PlotlyHistogram data={processedData} layout={chartLayout} />
            {/* <HistogramBinSlider
                onChange={(e, newValue) => handleSliderChange(newValue, range, setRange)}
                min={1.02}
                max={1.1}
                step={0.01}
                defaultValue={1.1}

            /> */}
            <div className="plot-title-short-histogram" id="compiler-comparison">
                Compiler Speedup Relative to Default Compiler
            </div>
        </div>
    );
}

