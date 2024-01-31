import { getProcessorColor } from "../Constants";
export const BarTextPlugin = {
    id: 'barText',
    afterDraw: (chart) => {
        const ctx = chart.ctx;
        ctx.save();
        ctx.font = "9px Verdana";
        chart.data.datasets.forEach((dataset, datasetIndex) => {
            const meta = chart.getDatasetMeta(datasetIndex);
            if (meta.hidden) return;

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            meta.data.forEach((bar, index) => {
                const label = dataset.barText && dataset.barText[index];
                if (label) {
                    ctx.fillText(label, bar.x, bar.y + bar.height / 2); //middle
                }
            });
        });
        ctx.restore();
    }
};

const filterDatasetsByType = (datasets, type) => {
    return datasets.filter(dataset => dataset.name.toLowerCase().includes(type));
};
export const calculateMinMaxForLabelIndex = (datasets, labelIndex) => {
    let maxValue = -Infinity;
    let maxIndex = -1;
    let minValue = Infinity;
    let minIndex = -1;

    datasets.forEach((dataset, index) => {
        const value = dataset.y[labelIndex];
        if (value !== null && value !== undefined) {
            if (value > maxValue) {
                maxValue = value;
                maxIndex = index;
            }
            if (value < minValue) {
                minValue = value;
                minIndex = index;
            }
        }
    });

    return { maxValue, maxIndex, minValue, minIndex };
};


export const createMinMaxAnnotations = (chartData) => {
    const annotations = [];
    if (chartData.length > 0 && chartData[0].x.length > 0) {
        const labelCount = chartData[0].x.length;

        for (let labelIndex = 0; labelIndex < labelCount; labelIndex++) {
            const { maxValue, maxIndex, minValue, minIndex } = calculateMinMaxForLabelIndex(chartData, labelIndex);

            if (maxValue !== -Infinity && minValue !== Infinity) {
                const ratio = maxValue / minValue;
                // have to use log max value to get correct place
                const adjustedYValue = Math.log10(maxValue)

                const annotation = {
                    x: chartData[maxIndex].x[labelIndex],
                    y: adjustedYValue,
                    text: `${ratio.toFixed(2)}`,
                    xanchor: 'center',
                    yanchor: 'bottom',
                    showarrow: false, // Do not show an arrow
                    font: {
                        family: 'Arial',
                        size: 12,
                        color: chartData[maxIndex].line.color, // use max index color for the text
                    }
                };
                annotations.push(annotation);
            }
        }
    }
    return annotations;
};

export const createMultileMinMaxAnnotations = (chartData) => {
    const annotations = [];
    const totalLabel = 'total';
    const perCoreLabel = 'core';

    if (chartData.length > 0 && chartData[0].x.length > 0) {
        const labelCount = chartData[0].x.length;

        for (let labelIndex = 0; labelIndex < labelCount; labelIndex++) {
            // Filter datasets for total GFlops and calculate min-max
            const totalDatasets = filterDatasetsByType(chartData, totalLabel);
            const { maxValue: totalMax, maxIndex: totalMaxIndex, minValue: totalMin, minIndex: totalMinIndex }
                = calculateMinMaxForLabelIndex(totalDatasets, labelIndex);

            // Filter datasets for per-core GFlops and calculate min-max
            const perCoreDatasets = filterDatasetsByType(chartData, perCoreLabel);
            const { maxValue: perCoreMax, maxIndex: perCoreMaxIndex, minValue: perCoreMin, minIndex: perCoreMinIndex }
                = calculateMinMaxForLabelIndex(perCoreDatasets, labelIndex);

            // Create annotations for total GFlops if applicable
            if (totalMax !== -Infinity && totalMin !== Infinity) {
                const totalRatio = totalMax / totalMin;
                const totalAdjustedYValue = Math.log10(totalMax);
                annotations.push({
                    x: totalDatasets[totalMaxIndex].x[labelIndex],
                    y: totalAdjustedYValue + 0.1,
                    text: `${totalRatio.toFixed(2)}`,
                    showarrow: false, //  no arrow
                    font: {
                        size: 12,
                        color: totalDatasets[totalMaxIndex].line.color,
                    }

                    // ... other annotation properties
                });
            }

            // Create annotations for per-core GFlops if applicable
            if (perCoreMax !== -Infinity && perCoreMin !== Infinity) {
                const perCoreRatio = perCoreMax / perCoreMin;
                const perCoreAdjustedYValue = perCoreMax; //  not logged
                annotations.push({
                    x: perCoreDatasets[perCoreMaxIndex].x[labelIndex],
                    y: perCoreAdjustedYValue + 2,
                    yref: 'y2',
                    text: `${perCoreRatio.toFixed(2)}`,
                    showarrow: false, // no arrow
                    font: {
                        size: 12,
                        color: perCoreDatasets[perCoreMaxIndex].line.color,
                    }

                });
            }
        }
    }
    return annotations;
};
